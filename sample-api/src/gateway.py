import datetime
import json
from dataclasses import dataclass
from os import getenv

import awswrangler as wr
import re

import awswrangler.s3
import boto3
import pandas as pd

s3 = boto3.client('s3')


@dataclass
class Settings:
    date: str
    start_time: str
    end_time: str
    auth_token: str

    def __post_init__(self):
        self.validate()

    def validate(self):
        self.validate_formats()
        self.auth_token = self.auth_token.replace('Bearer ', '')

        if not self.auth_token == '1q2w3e4r5t':
            raise ValueError("Invalid authorization token.")

        if not self.date == datetime.datetime.today().strftime('%d-%m-%Y'):
            raise ValueError("Invalid date. Must be today's date.")

        if not self.start_time < self.end_time:
            raise ValueError("Invalid start_time and end_time. start_time must be before end_time.")

    def validate_formats(self):
        date_pattern = re.compile(r"\d{2}-\d{2}-\d{4}")
        time_pattern = re.compile(r"\d{2}:\d{2}")

        if not date_pattern.match(self.date):
            raise ValueError("Invalid date format. Must be in the format 'dd-mm-YYYY'.")

        if not time_pattern.match(self.start_time):
            raise ValueError("Invalid start_time format. Must be in the format 'HH:MM'.")

        if not time_pattern.match(self.end_time):
            raise ValueError("Invalid end_time format. Must be in the format 'HH:MM'.")

        if not self.auth_token:
            raise ValueError("Authorization token not found in headers.")

        if not self.auth_token.startswith('Bearer '):
            raise ValueError("Invalid authorization token. Token must start with 'Bearer '.")


def get_data(settings: Settings):
    # Read data from S3
    bucket_name = getenv('BUCKET_NAME')
    objects = wr.s3.list_objects(f's3://{bucket_name}/')
    df_list = []
    for obj in objects:
        temp_clean_obj = obj.split('/')[-1].split('.')[0]
        if temp_clean_obj.replace('_', '-').startswith(settings.date):
            temp_clean_obj_time = ":".join(temp_clean_obj.split('_')[-2:])
            if settings.start_time <= temp_clean_obj_time <= settings.end_time:
                # response = s3.get_object(Bucket=bucket_name, Key=f"{temp_clean_obj}.csv")
                df_list.append(awswrangler.s3.read_csv(
                    path=f"s3://{bucket_name}/{temp_clean_obj}.csv",
                    sep=',',
                    header=0
                ))
    return pd.concat(df_list, ignore_index=False)


def lambda_handler(event, context):
    try:
        # Extract query parameters
        query_params = event.__getitem__('queryStringParameters')
        headers = event.__getitem__('headers')

        date: str = query_params.get('date', '')
        start_time: str = query_params.get('start_time', '')
        end_time: str = query_params.get('end_time', '')

        # Extract Bearer token from headers
        auth_token: str = headers.get('Authorization', '')
        settings = Settings(date=date, start_time=start_time, end_time=end_time, auth_token=auth_token)
        df = get_data(settings=settings)
        df = df.drop("Unnamed: 0", axis=1)
        json_response = df.to_json(orient='records', date_format='iso', index=False)

        # Your existing Lambda logic goes here
        return {
            'statusCode': 200,
            'body': json_response
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps(str(e))
        }
