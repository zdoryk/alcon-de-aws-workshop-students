import requests
from datetime import datetime, timedelta
import pandas as pd
import logging
import awswrangler as wr
from typing import Dict, Union

logging.basicConfig(level=logging.INFO)
# load_dotenv()
# auth_token = os.getenv('AUTH_TOKEN')
# BUCKET_NAME = os.getenv('BUCKET_NAME')
BUCKET_NAME = 'alcon-workshop-data-746590502764'


def get_path_info():
    current_utc_datetime = datetime.utcnow()
    start_time_utc = current_utc_datetime - timedelta(hours=1)

    # Yesterday Check
    if start_time_utc.date() < current_utc_datetime.date():
        logging.error("Error: can't request data from the previous day.")
        raise ValueError("Can't request data from the previous day.")

    file_date = start_time_utc.strftime('%d-%m-%Y-%H')
    date = start_time_utc.strftime('%d-%m-%Y')
    start_time = start_time_utc.strftime('%H:00')
    end_time = start_time_utc.strftime('%H:59')
    return date, start_time, end_time, file_date


def get_data_df(date: str, start_time: str, end_time: str) -> Union[Dict, None]:
    url = "https://43bhzz3c3f.execute-api.us-east-1.amazonaws.com/v1/data"
    headers = {"Authorization": "Bearer 1q2w3e4r5t"}
    params = {"date": date, "start_time": start_time, "end_time": end_time}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        logging.error(
            f"Failed to fetch data. Status code: {response.status_code}")
        return None

    return response.json()


def write_raw_df_to_s3(data_response, bucket_name, file_date):
    try:
        df = pd.DataFrame(data_response)
        path = f's3://{bucket_name}/raw/{file_date}.csv'
        wr.s3.to_csv(df, path, index=False)
    except Exception as e:
        logging.error(f"Failed to write DataFrame to S3. Error: {e}")
        return False
    return True


def main(event, context):
    logging.info("Starting lambda_raw job")

    try:
        date, start_time, end_time, file_date = get_path_info()
        data_response = get_data_df(date, start_time, end_time)
    except Exception as e:
        logging.error(f"Failed to fetch data. Error: {e}")
        return {"status": "Failed"}

    if data_response is not None:
        # Dataframe -> CSV -> S3
        try:
            write_raw_df_to_s3(data_response, BUCKET_NAME, file_date)
        except Exception as e:
            logging.error(f"Failed to write DataFrame to S3. Error: {e}")
            return {"status": "Failed"}

    logging.info("Finished lambda_raw job")
    return {"status": "OK"}


if __name__ == "__main__":
    main(None, None)
