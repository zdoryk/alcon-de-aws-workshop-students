import awswrangler as wr
import pandas as pd
from os import getenv
from datetime import datetime, timedelta
import logging


logging.getLogger().setLevel(logging.INFO)

AGE = 'AGE'


def clean_age_column(df: pd.DataFrame) -> pd.DataFrame:
    logging.info("Cleaning age column")
    min_years = 0
    max_years = 100

    cleaned_df = df[df[AGE].notnull()]
    cleaned_df = cleaned_df[
        (min_years <= cleaned_df[AGE]) & (cleaned_df[AGE] <= max_years)
    ]
    return cleaned_df


def main(handler=None, context=None):
    logging.info("Starting lambda_trusted job")

    now = datetime.utcnow()
    raw_path = f's3://{getenv("S3_BUCKET_NAME")}/raw/{now.strftime("%d-%m-%Y_%H")}.csv'
    df = wr.s3.read_csv(raw_path)
    cleaned_df = clean_age_column(df)

    trusted_path = f's3://{getenv("S3_BUCKET_NAME")}/trusted/{now.strftime("%d-%m-%Y_%H")}.csv'
    wr.s3.to_csv(cleaned_df, path=trusted_path, index=False)

    return {"status": "OK"}


if __name__ == "__main__":
    # Only for local development
    from dotenv import load_dotenv

    load_dotenv()
    main()
