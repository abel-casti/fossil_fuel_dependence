import os

from entsoe import EntsoePandasClient
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


def get_entsoe_client():
    """Initialize and return the ENTSO-E Pandas client."""

    api_token = os.getenv("ENTSOE_API_TOKEN")
    if not api_token:
        raise ValueError("ENTSOE_API_TOKEN not found in .env file")

    return EntsoePandasClient(api_key=api_token)


def fetch_generation_data(client, start, end, country_code):
    """Get and flatten generation data for a given contry and datetime range"""

    df_generation = client.query_generation(country_code, start=start, end=end, psr_type=None)

    df_generation.columns = [
        f"{column[0].lower().replace(' ', '_')}_{column[1].replace(' ', '')}" 
        for column in df_generation.columns
    ]

    return df_generation


def fetch_load_data(client, start, end, country_code):
    """Get load data for a given country and datetime range"""

    df_load = client.query_load(country_code, start=start, end=end)

    df_load.columns = [col.lower().replace(' ', '_') for col in df_load.columns]

    return df_load



if __name__ == "__main__":

    # Get SQLAlchemy engine
    engine = sqlalchemy_engine_setup()

    # Get client
    client = get_entsoe_client()

    # Get query parameters
    start = pd.Timestamp('2026-09-15', tz='Europe/Madrid')
    end = pd.Timestamp('2026-09-16', tz='Europe/Madrid')
    country_code = "ES"

    # Get generation data
    df_generation = fetch_generation_data(client, start, end, country_code)

    # Get load data
    df_load = fetch_load_data(client, start, end, country_code)