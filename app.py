import os

from entsoe import EntsoePandasClient
from dbt.cli.main import dbtRunner
import pandas as pd
import sqlalchemy



def get_entsoe_client():
    """Initialize and return the ENTSO-E Pandas client."""

    api_token = os.getenv("ENTSOE_API_TOKEN")
    if not api_token:
        raise ValueError("ENTSOE_API_TOKEN not found in .env file")

    return EntsoePandasClient(api_key=api_token)


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

    return sqlalchemy.create_engine(url, echo=True)


def postgres_staging_setup(engine):
    """Drop all existing tables and create 'staging' schema in Postgres DB if it  doesn't already exist"""

    schema = "staging"
    with engine.begin() as connection:
        connection.execute(sqlalchemy.text(f"DROP SCHEMA IF EXISTS {schema} CASCADE"))
        connection.execute(sqlalchemy.text(f"CREATE SCHEMA {schema};"))
        connection.execute(sqlalchemy.text(f"""
            CREATE TABLE {schema}.generation_log (
                timestamp TIMESTAMP,
                country_code VARCHAR(5)
            )
        """))


def insert_into_staging(engine, df, table_name):
    """Insert a dataframe into the given table in the 'staging' schema. If column does not exist in the predefined table, it will be added automatically"""
    
    with engine.begin() as connection:

        existing = {row[0] for row in connection.execute(sqlalchemy.text(f"""
            SELECT column_name FROM information_schema.columns
            WHERE table_schema = 'staging' AND table_name = '{table_name}'
        """))}

        for col in df.columns:
            if col not in existing:
                connection.execute(sqlalchemy.text(f"""
                    ALTER TABLE staging.{table_name} ADD COLUMN "{col}" DOUBLE PRECISION
                """))

        df.to_sql(table_name, con=connection, schema="staging", if_exists="append", index=False)


def flatten_generation_columns(df):
    """Flatten columns for multi-index dataframes"""

    positions, names = [], []

    for pos, col in enumerate(df.columns):
        if isinstance(col, tuple):
            if col[1] == "Actual Aggregated":
                positions.append(pos)
                names.append(col[0])
        else:
            positions.append(pos)
            names.append(col)

    df = df.iloc[:, positions]
    df.columns = names

    return df


def fetch_generation_data(engine, client, start, end, country_codes):
    """Get, flatten, and cocatenate generation data for the given date range and all given countries into a single df"""

    print(f"\nFetching data from {start} to {end}.\n")

    for code in country_codes:
        print(f"Fetching '{code}' generation data...")
        try:
            df = client.query_generation(code, start=start, end=end, psr_type=None)
            df = flatten_generation_columns(df)
            df.index.name = "timestamp"
            df = df.reset_index()
            df["country_code"] = code

            insert_into_staging(engine, df, "generation_log")

        except Exception as e:
            print(f"Failed to fetch generation data for country {code}: {e}")

    return None


def fetch_load_data(client, start, end, country_codes):
    """Get and concatenate load data for the given date range and all given countries into a single df"""

    all_dfs = []
    for code in country_codes:
        print(f"Fetching '{code}' load data...")
        try:
            df = client.query_load(code, start=start, end=end)
            df.index.name = "timestamp"
            df = df.reset_index()
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
    postgres_staging_setup(engine)

    # Get client
    client = get_entsoe_client()

    # Set query parameters
    country_codes = ["ES", "FR", "NL", "DE_LU", "PL"]
    end = (pd.Timestamp.now(tz="Europe/Madrid") - pd.Timedelta(days=1826)).normalize()
    start = end - pd.DateOffset(days=30)

    # Get generation data
    fetch_generation_data(engine, client, start, end, country_codes)

    # Get load data
    #df_load = fetch_load_data(client, start, end, country_codes)

    # Run dbt
    #dbt = dbtRunner()
    #dbt.invoke(["build", "--project-dir", "/workspace/dbt", "--profiles-dir", "/workspace/dbt"])
