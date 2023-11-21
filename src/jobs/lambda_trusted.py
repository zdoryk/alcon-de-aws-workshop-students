import awswrangler as wr
import pandas as pd
from os import getenv
from datetime import datetime, timedelta
import logging


def clean_age_column(df: pd.DataFrame) -> pd.DataFrame:
    # Remove negative values
    df = df[df["AGE"] >= 0]

    # Remove all values above 120
    df = df[df["AGE"] <= 120]

    # Remove all missing values
    df = df[df["AGE"].notna()]

    return df


def main(handler=None, context=None):
    logging.info("Starting lambda_raw job")
    previous_hour_dt = datetime.utcnow() - timedelta(hours=1)

    # Get data from S3 RAW layer
    df = wr.s3.read_csv(
        path=f's3://{getenv("S3_BUCKET_NAME")}/raw/{previous_hour_dt.strftime("%d-%m-%Y_%H")}.csv',
        sep=",",
        header=0,
    )

    # Task #1
    df["IS_DEAD"] = df["DATE_DIED"].apply(
        lambda x: True if x == "9999-99-99" else False
    )

    # Task #2
    df = clean_age_column(df=df)

    # Write data to S3 TRUSTED layer
    wr.s3.to_csv(
        df=df,
        path=f's3://{getenv("S3_BUCKET_NAME")}/trusted/{previous_hour_dt.strftime("%d-%m-%Y_%H")}.csv',
        index=False,
    )

    return {"status": "OK"}


if __name__ == "__main__":
    # Only for local development
    from dotenv import load_dotenv

    load_dotenv()
    main()
