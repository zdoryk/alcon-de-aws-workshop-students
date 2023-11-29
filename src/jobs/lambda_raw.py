import requests
from os import getenv
from datetime import datetime, timedelta
import pandas as pd
import logging
import awswrangler as wr


logging.getLogger().setLevel(logging.INFO)


def get_data_df(hour_dt: datetime) -> pd.DataFrame:
    logging.info("Getting data from API")

    api_url = 'https://43bhzz3c3f.execute-api.us-east-1.amazonaws.com/v1/data'
    headers = {
        'Authorization': f'Bearer {getenv("AUTH_TOKEN")}'
    }
    params = {
        'date': hour_dt.strftime('%d-%m-%Y'),
        'start_time': (hour_dt - timedelta(seconds=1)).strftime('%H:%m'),
        'end_time': hour_dt.strftime('%H:%m'),
    }
    response = requests.get(api_url, headers=headers, params=params)
    return pd.DataFrame(response.json())


def main(handler=None, context=None):
    logging.info("Starting lambda_raw job")

    now = datetime.utcnow()
    df = get_data_df(now.replace(minute=0, second=0))

    filepath = f's3://{getenv("S3_BUCKET_NAME")}/{now.strftime("%d-%m-%Y_%H")}.csv'
    wr.s3.to_csv(df, path=filepath, index=False)
    return {"status": "OK"}


if __name__ == "__main__":
    # Only for local development
    from dotenv import load_dotenv

    load_dotenv()
    main()
