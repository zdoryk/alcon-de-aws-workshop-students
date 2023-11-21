import sys
from awsglue.utils import getResolvedOptions
import awswrangler as wr
import logging
from datetime import datetime, timedelta
import pandas as pd

args = getResolvedOptions(sys.argv, ["S3_BUCKET_NAME"])
bucket_name = args["S3_BUCKET_NAME"]
# bucket_name = 'alcon-workshop-data-099605873748'


# Function to create the full name with title
def create_full_name(row):
    # If the person is under 21, return only the first and last name
    if row["AGE"] < 21:
        return f"{row['FIRST_NAME']} {row['LAST_NAME']}"
    # If the person is over 21, return the title, first and last name
    title = "Mr" if row["SEX"] == "Male" else "Mrs"
    return f"{title}. {row['FIRST_NAME']} {row['LAST_NAME']}"


def add_age_group(df):
    # Calculate dynamic bin max value
    max_age: int = int(df["AGE"].max())
    # Specify the bin width
    bin_width = 10

    # Create bins and labels dynamically
    bins = list(range(0, max_age + bin_width, bin_width))
    labels = [f"{x}-{x + bin_width - 1} years" for x in range(0, max_age, bin_width)]

    # Add the last bin for values greater than the last specified bin edge
    labels.append(f"{bins[-1] + 1}+ years")
    bins.append(float("inf"))

    # Create the 'AGE_GROUP' column
    df["AGE_GROUP"] = pd.cut(
        df["AGE"], bins=bins, labels=labels, include_lowest=True, right=False
    )


def main():
    logging.info("Starting Glue enriched job")
    previous_hour_dt = datetime.utcnow() - timedelta(hours=1)

    # Getting the data from the S3 bucket
    df = wr.s3.read_csv(
        f's3://{bucket_name}/trusted/{previous_hour_dt.strftime("%d-%m-%Y_%H")}.csv'
    )

    # Task #3
    df["FULL_NAME"] = df.apply(lambda row: create_full_name(row), axis=1)

    # Task #4
    add_age_group(df=df)

    df["INGESTION_DATETIME"] = pd.to_datetime(df["INGESTION_DATETIME"])

    # Define the schema
    dtype = {
        "FIRST_NAME": "varchar(50)",
        "LAST_NAME": "varchar(50)",
        "SEX": "varchar(7)",
        "AGE": "smallint",
        "DATE_DIED": "varchar(20)",
        "INGESTION_DATETIME": "timestamp",
        "IS_DEAD": "boolean",
        "FULL_NAME": "varchar(100)",
        "AGE_GROUP": "varchar(20)",
    }

    # Write the .parquet file to the S3 bucket
    wr.s3.to_parquet(
        df=df,
        path=f's3://{bucket_name}/enriched/{previous_hour_dt.strftime("%d-%m-%Y_%H")}.parquet',
        index=False,
        dtype=dtype,
    )


main()
