import requests
from os import getenv
from datetime import datetime, timedelta
import pandas as pd
import logging
import awswrangler as wr


def get_data_df(hour: str):
    logging.info("Getting data from API")
    headers = {"Authorization": f"Bearer {getenv('AUTH_TOKEN')}"}
    today = datetime.utcnow()
    # Get current hour number
    (datetime.utcnow() - timedelta(hours=1))
    start_time = f"{hour}:00"
    end_time = f"{hour}:59"
    api_base_url = "https://bc3v3ovbcc.execute-api.us-east-1.amazonaws.com/v1"
    # Get data from the API
    response = requests.get(
        f"{api_base_url}/data?date={today.strftime('%d-%m-%Y')}&start_time={start_time}&end_time={end_time}",
        headers=headers,
    )
    return pd.DataFrame(response.json())


def main(handler=None, context=None):
    logging.info("Starting lambda_raw job")
    previous_hour_dt = datetime.utcnow() - timedelta(hours=1)
    # Get data from API
    df = get_data_df(hour=previous_hour_dt.strftime("%H"))

    # Write data to S3
    wr.s3.to_csv(
        df=df,
        path=f's3://{getenv("S3_BUCKET_NAME")}/raw/{previous_hour_dt.strftime("%d-%m-%Y_%H")}.csv',
        index=False,
    )

    return {"status": "OK"}


if __name__ == "__main__":
    # Only for local development
    from dotenv import load_dotenv

    load_dotenv()
    main()
