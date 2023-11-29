import sys
from awsglue.utils import getResolvedOptions
import awswrangler as wr
import logging
from datetime import datetime, timedelta
import pandas as pd


logging.getLogger().setLevel(logging.INFO)

args = getResolvedOptions(sys.argv, ["S3_BUCKET_NAME"])
bucket_name = args["S3_BUCKET_NAME"]


def create_died_column(df: pd.DataFrame) -> pd.DataFrame:
    logging.info('Creating died column')

    df['IS_DEAD'] = df['DATE_DIED'] == '9999-99-99'
    return df


# Function to create the full name with title
def create_full_names(df: pd.DataFrame) -> pd.DataFrame:
    logging.info('Creating full names column')

    df['FULL_NAME'] = df['FIRST_NAME'] + ' ' + df['LAST_NAME']

    mr_indexes = df[(df['AGE'] > 21) & (df['SEX'] == 'Male')].index
    df.loc[mr_indexes, 'FULL_NAME'] = 'Mr. ' + df.loc[mr_indexes, 'FULL_NAME']

    mrs_indexes = df[(df['AGE'] > 21) & (df['SEX'] == 'Female')].index
    df.loc[mrs_indexes, 'FULL_NAME'] = 'Mrs. ' + df.loc[mrs_indexes, 'FULL_NAME']
    return df


def add_age_group(df: pd.DataFrame) -> pd.DataFrame:
    logging.info('Adding age group column')

    df['AGE_GROUP'] = df['AGE'].apply(
        lambda x: f'{int(x) // 10 * 10}-{int(x) // 10 * 10 + 9}'
    )
    return df


def main():
    logging.info("Starting Glue enriched job")
    now = datetime.utcnow()

    trusted_path = f's3://{bucket_name}/trusted/{now.strftime("%d-%m-%Y_%H")}.csv'
    df = wr.s3.read_csv(trusted_path)
    enriched_df = create_died_column(df)
    enriched_df = create_full_names(enriched_df)
    enriched_df = add_age_group(enriched_df)

    enriched_path = f's3://{bucket_name}/enriched/{now.strftime("%d-%m-%Y_%H")}.parquet'
    
    dtype = {
        'FIRST_NAME': 'varchar(50)',
        'LAST_NAME': 'varchar(50)',
        'SEX': 'varchar(7)',
        'AGE': 'smallint',
        'DATE_DIED': 'varchar(20)',
        'INGESTION_DATETIME': 'timestamp',
        'IS_DEAD': 'boolean',
        'FULL_NAME': 'varchar(100)',
        'AGE_GROUP': 'varchar(20)',
    }

    wr.s3.to_parquet(enriched_df, path=enriched_path, index=False, dtype=dtype)


main()
