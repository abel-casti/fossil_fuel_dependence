from dotenv import load_dotenv
from entsoe import EntsoePandasClient
import pandas as pd
import os


def get_entsoe_client():
    # Get API token from .env file
    load_dotenv()
    API_TOKEN = os.getenv("ENTSOE_API_TOKEN")

    if not API_TOKEN:
        raise ValueError("ENTSOE_API_TOKEN not found in .env file")

    # Return the ENTSOE client for pandas
    return EntsoePandasClient(api_key=API_TOKEN)



def fetch_generation_data(client, start, end, country_code):
    # Make API call through the ENTSOE client
    df_generation = client.query_generation(country_code, start=start, end=end, psr_type=None)

    # Flatten and format MultiIndex columns '(Energy Storage, Actual Consumption)' --> 'energy_storage_ActualConsumption'
    df_generation.columns = [
        f"{column[0].lower().replace(' ', '_')}_{column[1].replace(' ', '')}" 
        for column in df_generation.columns
    ]

    return df_generation



def fetch_load_data(client, start, end, country_code):
    # Make API call through the ENTSOE client
    df_load = client.query_load(country_code, start=start, end=end)

    # Format column name 'Actual Load' --> 'actual_load'
    df_load.columns = [col.lower().replace(' ', '_') for col in df_load.columns]

    return df_load



if __name__ == "__main__":

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
