import os
import boto3
from io import StringIO
from botocore.exceptions import ClientError
import requests
from datetime import datetime, timedelta
import pandas as pd
import logging
from io import StringIO
import awswrangler as wr

logging.basicConfig(level=logging.INFO)

AWS_ACCESS_KEY_ID = 'AKIA23VCC75WKVJ3AF7W'
AWS_SECRET_ACCESS_KEY = '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'
BUCKET_NAME = 'alcon-workshop-data-746590502764'


def get_data_df(date: str, start_time: str, end_time: str):
    url = f"https://43bhzz3c3f.execute-api.us-east-1.amazonaws.com/v1/data?date={date}&start_time={start_time}&end_time={end_time}"
    headers = {"Authorization": "Bearer 1q2w3e4r5t"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        logging.error(f"Failed to fetch data. Status code: {response.status_code}")
        return None

def main(event, context):
    logging.info("Starting lambda_raw job")

    current_utc_datetime = datetime.utcnow()

    # Start time
    start_time_utc = current_utc_datetime - timedelta(hours=1)

    # Yesterday Check
    if start_time_utc.date() < current_utc_datetime.date():
        logging.error("Error: can't request data from previous day.")
        return {"status": "Error"}

    # End time utc
    end_time_utc = current_utc_datetime

    # Date formats
    date_format = "%d-%m-%Y"
    time_format = "%H:%M"

    # Setting vars
    date = start_time_utc.strftime(date_format)
    start_time = f"{start_time_utc.strftime(time_format)[:2]}:00"
    end_time = f"{end_time_utc.strftime(time_format)[:2]}:00"
    logging.info(start_time)
    logging.info(end_time)
    logging.info(date)

    data_response = get_data_df(date, start_time, end_time)

    if data_response is not None:
        # API -> DataFrame
        df = pd.DataFrame(data_response)

        # Saving file to S3 bucket
        s3_file_path = f"raw/{date}-{start_time[:2]}.csv"

        # Dataframe -> CSV
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)

        s3_resource = boto3.resource('s3')
        s3_resource.Object(BUCKET_NAME, s3_file_path).put(Body=csv_buffer.getvalue())

    return {"status": "OK"}

if __name__ == "__main__":
    main(None, None)

