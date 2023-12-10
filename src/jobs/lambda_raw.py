import requests
from os import getenv
from datetime import datetime, timedelta, timezone
import pandas as pd
import logging
import awswrangler as wr

# # # AUTH_TOKEN = 1q2w3e4r5t
# # # S3_BUCKET_NAME = alcon-workshop-data-689308297941

# def get_data_df(hour: str):
#     logging.info("https://43bhzz3c3f.execute-api.us-east-1.amazonaws.com/v1/data?date=08-12-2023&start_time=01:00&end_time=02:00", headers={"Authorization": "Bearer 1q2w3e4r5t"})
   
def get_data_df(hour: str):
    logging.info("Getting data from API")

    url = 'https://43bhzz3c3f.execute-api.us-east-1.amazonaws.com/v1/data'
    params = {'date': datetime.now(timezone.utc).strftime('%d-%m-%Y'), 'start_time':  f'{hour}:00', 'end_time':  f'{hour}:59'}
    headers = {"Authorization": f"Bearer {getenv('AUTH_TOKEN')}"}
    r = requests.get(url, params=params, headers=headers)
    df = pd.DataFrame(r.json())

    return df
    
    
def main(handler=None, context=None):
    logging.info("Starting lambda_raw job")
    utc = datetime.now(timezone.utc)
    date = utc.strftime('%Y-%m-%d')
    S_H = (utc - timedelta(hours=1)).strftime('%H')
    df = get_data_df(S_H)
    wr.s3.to_csv(df, path=f"s3://{getenv('S3_BUCKET_NAME')}/raw/{date}_{S_H}.csv", index=False)

    return {"status": "OK"}


if __name__ == "__main__":
    # Only for local development
    from dotenv import load_dotenv

    load_dotenv()
    main()
