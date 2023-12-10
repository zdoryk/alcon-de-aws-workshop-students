import awswrangler as wr
import pandas as pd
from os import getenv
from datetime import datetime, timedelta, timezone
import logging


def clean_age_column(df: pd.DataFrame) -> pd.DataFrame:
    
    df.drop(df[(df['AGE'] < 0) | (df['AGE'] > 110) | (df['AGE'].isnull())].index, inplace=True)
    return df


def main(handler=None, context=None):
    logging.info("Starting lambda_raw job")
    utc = datetime.now(timezone.utc)
    date = utc.strftime('%Y-%m-%d')
    S_H = (utc - timedelta(hours=1)).strftime('%H')
    df = wr.s3.read_csv(path=f"s3://{getenv('S3_BUCKET_NAME')}/raw/{date}_{S_H}.csv", sep=',')
    df = clean_age_column(df)

    wr.s3.to_csv(df, path=f"s3://{getenv('S3_BUCKET_NAME')}/trusted/{date}_{S_H}.csv", index=False)
    return {"status": "OK"}


if __name__ == "__main__":
    # Only for local development
    from dotenv import load_dotenv

    load_dotenv()
    main()
