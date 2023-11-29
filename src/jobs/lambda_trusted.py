import awswrangler as wr
import pandas as pd
from os import getenv
from datetime import datetime, timedelta, timezone
import logging


def clean_age_column(df: pd.DataFrame) -> pd.DataFrame:
    # Remove negative values, outliers and missing values
    df = df[~df['AGE'].isna() & df['AGE'].between(0, 122)]

    return df


def main(handler=None, context=None):
    logging.info("Starting lambda_raw job")

    current_utc_time = datetime.now(timezone.utc)
    
    start_hour = (current_utc_time - timedelta(hours=1)).strftime('%H')

    date = current_utc_time.strftime('%Y-%m-%d')

    df = wr.s3.read_csv(
        path=f"s3://{ getenv('S3_BUCKET_NAME') }/raw/{date}_{start_hour}.csv",
        sep=","
    )

    df = clean_age_column(df)

    wr.s3.to_csv(
        df, 
        path=f"s3://{ getenv('S3_BUCKET_NAME') }/trusted/{date}_{start_hour}.csv",
        index=False
    )

    return {"status": "OK"}


if __name__ == "__main__":
    # Only for local development
    from dotenv import load_dotenv

    load_dotenv()
    main()
