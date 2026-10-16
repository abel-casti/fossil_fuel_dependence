import os

from entsoe import EntsoePandasClient
from dbt.cli.main import dbtRunner
import pandas as pd
import sqlalchemy


def sqlalchemy_engine_setup():
    """Create and return a SQLAlchemy engine connected to the Postgres DB."""

    postgres_user = os.getenv("POSTGRES_USER")
    postgres_password = os.getenv("POSTGRES_PASSWORD")
    postgres_host = os.getenv("POSTGRES_HOST")
    postgres_db = os.getenv("POSTGRES_DB")

    if not postgres_user or not postgres_password or not postgres_host or not postgres_db:
        raise ValueError("Missing postgres connection parameter(s) on .env file")

    url = sqlalchemy.URL.create(
        drivername="postgresql+pg8000",
        username=postgres_user,
        password=postgres_password,
        host=postgres_host,
        database=postgres_db
    )

    return sqlalchemy.create_engine(url)


def postgres_schemas_setup(engine):
    """Create 'raw' and 'trfm' schemas in Postgres DB if they don't exist already"""

    schemas = ["staging", "intermediate", "marts"]
    with engine.begin() as connection:
        for schema in schemas:
            connection.execute(
                sqlalchemy.text(f"CREATE SCHEMA IF NOT EXISTS {schema};")
            )


def get_entsoe_client():
    """Initialize and return the ENTSO-E Pandas client."""

    api_token = os.getenv("ENTSOE_API_TOKEN")
    if not api_token:
        raise ValueError("ENTSOE_API_TOKEN not found in .env file")

    return EntsoePandasClient(api_key=api_token)


def fetch_generation_data(client, start, end, country_codes):
    """Get, flatten, and cocatenate generation data for the given date range and all given countries into a single df"""

    print(f"\nFetching data from {start} to {end}.\n")

    all_dfs = []
    for code in country_codes:
        print(f"Fetching '{code}' generation data...")
        try:
            df = client.query_generation(code, start=start, end=end, psr_type=None)
            df.columns = [
                f"{column[0].lower().replace(' ', '_')}_{column[1].lower().replace(' ', '_')}"
                for column in df.columns
            ]
            df = df.reset_index().rename(columns={"index": "timestamp"})
            df["country_code"] = code
            all_dfs.append(df)

        except Exception as e:
            print(f"Failed to fetch generation data for country {code}: {e}")

    if not all_dfs:
        raise RuntimeError(f"No load data fetched for any country on given period")

    df_generation = pd.concat(all_dfs, ignore_index=True)
    return df_generation


def fetch_load_data(client, start, end, country_codes):
    """Get and concatenate load data for the given date range and all given countries into a single df"""

    all_dfs = []
    for code in country_codes:
        print(f"Fetching '{code}' load data...")
        try:
            df = client.query_load(code, start=start, end=end)
            df = df.reset_index().rename(columns={"index": "timestamp"})
            df["country_code"] = code
            all_dfs.append(df)
        except Exception as e:
            print(f"Failed to fetch load data for country {code}: {e}")

    if not all_dfs:
        raise RuntimeError(f"No load data fetched for any country on given period")

    df_load = pd.concat(all_dfs, ignore_index=True)
    df_load.columns = [col.lower().replace(' ', '_') for col in df_load.columns]
    return df_load



if __name__ == "__main__":

    # Get SQLAlchemy engine
    engine = sqlalchemy_engine_setup()

    # Setup Postgres schemas
    postgres_schemas_setup(engine)

    # Get client
    client = get_entsoe_client()

    # Set query parameters
    country_codes = ["ES", "FR", "NL", "DE_LU", "PL"]
    end = (pd.Timestamp.now(tz="Europe/Madrid") - pd.Timedelta(days=1)).normalize()
    start = end - pd.DateOffset(days=60)

    # Get generation data
    df_generation = fetch_generation_data(client, start, end, country_codes)

    # Get load data
    df_load = fetch_load_data(client, start, end, country_codes)

    # Load data into Postgres DB
    df_generation.to_sql("generation_log", con=engine, schema="staging", if_exists="delete_rows", index=False)
    df_load.to_sql("load_log", con=engine, schema="staging", if_exists="delete_rows", index=False)

    # Run dbt
    dbt = dbtRunner()
    dbt.invoke(["build", "--project-dir", "/workspace/dbt", "--profiles-dir", "/workspace/dbt"])
