import os
import boto3
from io import StringIO
from botocore.exceptions import ClientError
import requests
from datetime import datetime, timedelta
import pandas as pd
import logging
import io
import awswrangler as wr

logging.basicConfig(level=logging.INFO)

AWS_ACCESS_KEY_ID = 'AKIA23VCC75WKVJ3AF7W'
AWS_SECRET_ACCESS_KEY = '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'
BUCKET_NAME = 'alcon-workshop-data-746590502764'


def clean_age_column(df: pd.DataFrame) -> pd.DataFrame:
    # Negative age check
    df = df[df['AGE'] >= 0]

    # filtering ages > 122
    df = df[df['AGE'] <= 122]

    # filtering nulls
    df = df.dropna(subset=['AGE'])

    return df

def main(handler=None, context=None):
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

    #local_file_path = "C:\\Users\\User\\Desktop\\Alcon\\json.csv"
    s3_file_name = f"{date}-{start_time[:2]}.csv"
    logging.info('whateva')
    s3_resource = boto3.resource('s3')
    response = s3_resource.Object(BUCKET_NAME, f'raw/{s3_file_name}').get()


    # Read CSV
    df = pd.read_csv(io.BytesIO(response['Body'].read()))


    # Clean age column
    df_cleaned = clean_age_column(df)

    # Save 
    #desktop_path = "C:/Users/User/Desktop/"
    #file_path = desktop_path + "cleaned_data.csv"
    #df_cleaned.to_csv(file_path, index=False)
    csv_buffer = StringIO()
    df_cleaned.to_csv(csv_buffer, index=False)
    s3_resource.Object(BUCKET_NAME, f'trusted/{s3_file_name}').put(Body=csv_buffer.getvalue())

    logging.info(f"Saved cleaned data")

    return {"status": "OK"}

if __name__ == "__main__":
    main()
