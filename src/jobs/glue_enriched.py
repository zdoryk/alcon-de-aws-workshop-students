import sys
from awsglue.utils import getResolvedOptions
import awswrangler as wr
import logging
from datetime import datetime, timedelta, timezone
import pandas as pd

args = getResolvedOptions(sys.argv, ["S3_BUCKET_NAME"])
bucket_name = args["S3_BUCKET_NAME"]


def create_full_name(x):
    if x['AGE'] > 21 and x['SEX'] == 'Female':
        return 'Mrs ' + x['FULL_NAME']
    elif x['AGE'] > 21 and x['SEX'] == 'Male':
        return 'Mr ' + x['FULL_NAME']
    else:
        return x['FULL_NAME']


def add_age_group(df):
    max_age = int(df['AGE'].max())
    df['AGE_GROUP'] = ''
    for i in range(0, max_age + 1, 10):
        condition = (df['AGE'] >= i) & (df['AGE'] < i + 10)
        df.loc[condition, 'AGE_GROUP'] = f'{i}-{i+9}'

    condition = df['AGE'] >= max_age
    df.loc[condition, 'AGE_GROUP'] = f'{max_age}-{max_age + 9}'
#enriching
    df['DIED'] = df['DATE_DIED'] != '9999-99-99'
    df['FULL_NAME'] = df.apply(create_full_name, axis=1)
def main():
    logging.info("Starting Glue enriched job")
    utc = datetime.now(timezone.utc)
    date = utc.strftime('%Y-%m-%d')
    S_H = (utc - timedelta(hours=1)).strftime('%H')
    df = wr.s3.read_csv(path=f"s3://{bucket_name}/raw/{date}_{S_H}.csv", sep=',')


    schema = {"FIRST_NAME": "varchar(50)",
        "LAST_NAME": "varchar(50)",
        "SEX": "varchar(10)",
        "AGE": "int",
        "DATE_DIED": "varchar(50)",
        "INGESTION_DATETIME": "timestamp",
        "FULL_NAME": "varchar(100)",
        "DIED": "boolean",
        "AGE_GRP": "varchar(50)"} 

    wr.s3.to_parquet(df, path=f"s3://{bucket_name}/enriched/{date}_{S_H}.parquet", index=False, dtype=schema)

main()
