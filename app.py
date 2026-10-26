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

    return sqlalchemy.create_engine(url, echo=False)


def postgres_staging_setup(engine):
    """Recreate staging schema and tables in Postgres DB"""

    schema = "staging"
    with engine.begin() as connection:
        connection.execute(sqlalchemy.text(f"DROP SCHEMA IF EXISTS {schema} CASCADE"))
        connection.execute(sqlalchemy.text(f"CREATE SCHEMA {schema}"))
        connection.execute(sqlalchemy.text(f"""
            CREATE TABLE {schema}.generation_log (
                timestamp TIMESTAMP,
                country_code VARCHAR(5)
            )
        """))
        connection.execute(sqlalchemy.text(f"""
            CREATE TABLE {schema}.load_log (
                timestamp TIMESTAMP,
                country_code VARCHAR(5)
            )
        """))


def normalize_generation_columns(df):
    """Flatten columns and merge duplicates. Keeps the first non-null value per row"""

    merged = {}

    for pos, col in enumerate(df.columns):
        if isinstance(col, tuple):
            if col[1].strip().lower() != "actual aggregated":
                continue
            name = col[0].strip().lower()
        else:
            name = col.strip().lower()

        series = df.iloc[:, pos]
        if name in merged:
            merged[name] = merged[name].combine_first(series)
        else:
            merged[name] = series

    return pd.DataFrame(merged, index=df.index)


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


def fetch_generation_data(engine, client, start, end, country_codes):
    """Get, flatten, and insert generation data for the given date range and all given countries into Postgres DB"""

    print(f"\nFetching data from {start} to {end}.\n")

    for code in country_codes:
        print(f"Fetching '{code}' generation data...")
        try:
            df = client.query_generation(code, start=start, end=end, psr_type=None)
            df = normalize_generation_columns(df)
            df.index.name = "timestamp"
            df = df.reset_index()
            df['timestamp'] = df['timestamp'].dt.tz_localize(None)
            df["country_code"] = code
            insert_into_staging(engine, df, "generation_log")
        except Exception as e:
            print(f"Failed to fetch generation data for country {code}: {e}")


def fetch_load_data(engine, client, start, end, country_codes):
    """Get and insert load data for the given date range and all given countries into Postgres DB"""

    for code in country_codes:
        print(f"Fetching '{code}' load data...")
        try:
            df = client.query_load(code, start=start, end=end)
            df.index.name = "timestamp"
            df = df.reset_index()
            df['timestamp'] = df['timestamp'].dt.tz_localize(None)
            df["country_code"] = code
            insert_into_staging(engine, df, "load_log")
        except Exception as e:
            print(f"Failed to fetch load data for country {code}: {e}")



if __name__ == "__main__":

    # Setup
    engine = sqlalchemy_engine_setup()
    postgres_staging_setup(engine)
    client = get_entsoe_client()

    # Get data from ENTSO-E
    country_codes = ["ES", "FR", "BE", "DE_LU", "PL"]
    start = pd.Timestamp("2019-01-01", tz="Europe/Madrid")
    end = (pd.Timestamp.now(tz="Europe/Madrid").normalize() - pd.Timedelta(seconds=1))

    fetch_generation_data(engine, client, start, end, country_codes)
    fetch_load_data(engine, client, start, end, country_codes)

    # Run dbt
    dbt = dbtRunner()
    dbt.invoke(["build", "--project-dir", "/workspace/dbt", "--profiles-dir", "/workspace/dbt"])