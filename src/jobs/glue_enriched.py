import sys
from awsglue.utils import getResolvedOptions
import awswrangler as wr
import logging
from datetime import datetime, timedelta, timezone
import pandas as pd

args = getResolvedOptions(sys.argv, ["S3_BUCKET_NAME"])
bucket_name = args["S3_BUCKET_NAME"]


# Function to create the full name with title
def create_full_name(row):
    if row['AGE'] <= 21:
        name_pfx = ''
    elif row['SEX'] == 'Male':
        name_pfx = 'Mr. '
    else:
        name_pfx = 'Mrs. '
        
    return f"{name_pfx}{row['FIRST_NAME']} {row['LAST_NAME']}"

def add_age_group(df):
    max_age = int(df['AGE'].max())

    bin_width = 10
    bins = list(range(0, max_age + bin_width, bin_width))

    # Add one more bin for the highest values
    bins.append(bins[-1] + bin_width)

    age_labels = [f"{x}-{x + bin_width - 1}" for x in bins[0:len(bins)-1]]

    df['AGE_GRP'] = pd.cut(df['AGE'], bins=bins, labels=age_labels, 
                           right=False)

    return df


def main():
    logging.info("Starting Glue enriched job")

    current_utc_time = datetime.now(timezone.utc)
    
    start_hour = (current_utc_time - timedelta(hours=1)).strftime('%H')

    date = current_utc_time.strftime('%Y-%m-%d')

    df = wr.s3.read_csv(
        path=f"s3://{bucket_name}/raw/{date}_{start_hour}.csv",
        sep=","
    )

    # Add DIED column

    df.loc[df["DATE_DIED"] == "9999-99-99", "DIED"] = False
    df.loc[df["DATE_DIED"] != "9999-99-99", "DIED"] = True

    # Add FULL_NAME

    df['FULL_NAME'] = df.apply(create_full_name, axis=1)

    # Add AGE_GROUP

    df = add_age_group(df)

    # Define the schema (in ATHENA format)

    schema = {
        "FIRST_NAME": "varchar(50)",
        "LAST_NAME": "varchar(50)",
        "SEX": "varchar(10)",
        "AGE": "int",
        "DATE_DIED": "varchar(50)",
        "INGESTION_DATETIME": "timestamp",
        "FULL_NAME": "varchar(100)",
        "DIED": "boolean",
        "AGE_GRP": "varchar(50)"
    } 

    wr.s3.to_parquet(
        df, 
        path=f"s3://{bucket_name}/enriched/{date}_{start_hour}.parquet",
        index=False,
        dtype=schema
    )

main()
