import awswrangler as wr
import logging
from datetime import datetime, timedelta
import pandas as pd

logging.basicConfig(level=logging.INFO)

# args = getResolvedOptions(sys.argv, ["S3_BUCKET_NAME"])
# bucket_name = args["S3_BUCKET_NAME"]
BUCKET_NAME = 'alcon-workshop-data-746590502764'


def get_time_range():
    current_utc_datetime = datetime.utcnow()
    start_time_utc = current_utc_datetime - timedelta(hours=1)

    # Yesterday Check
    if start_time_utc.date() < current_utc_datetime.date():
        logging.error("Error: can't request data from the previous day.")
        return {"status": "Error"}

    date = start_time_utc.strftime('%d-%m-%Y')
    start_time = f'{start_time_utc.hour}:00'
    end_time = f'{(start_time_utc+timedelta(hours=1)).hour}:00'

    return date, start_time, end_time


def create_full_name(row):
    if row["AGE"] < 21:
        return f"{row['FIRST_NAME']} {row['LAST_NAME']}"
    title = "Mr" if row["SEX"] == "Male" else "Mrs"

    return f"{title}. {row['FIRST_NAME']} {row['LAST_NAME']}"


def add_age_group(df):
    df['AGE_GROUP'] = ((df['AGE'] - 1) // 10 * 10 + 1).astype(int).astype(str) + \
        '-' + ((df['AGE'] - 1) // 10 * 10 + 9).astype(int).astype(str)

    return df


def create_died_column(df):
    df['DIED'] = df['DATE_DIED'].apply(
        lambda x: True if x != '9999-99-99' else False)
    df['DIED'] = df['DIED'].astype(bool)

    return df


def main():
    logging.info("Starting Glue enriched job")
    date, start_time, end_time = get_time_range()

    df = wr.s3.read_csv(
        f's3://{BUCKET_NAME}/trusted/{date}-{end_time[:2]}.csv'
    )

    df['FULL_NAME'] = df.apply(create_full_name, axis=1)
    df = add_age_group(df)
    df = create_died_column(df)

    dtypes = {
        'FIRST_NAME': 'varchar(40)',
        'LAST_NAME': 'varchar(40)',
        'SEX': 'varchar(6)',
        'AGE': 'int',
        'DATE_DIED': 'varchar(10)',
        'INGESTION_DATETIME': 'varchar(20)',
        'FULL_NAME': 'varchar(80)',
        'AGE_GROUP': 'varchar(7)',
        'DIED': 'varchar(5)',
    }

    if df is not None:
        s3_file_path = f"enriched/{date}-{end_time[:2]}.parquet"

        wr.s3.to_parquet(
            df=pd.DataFrame(df),
            path=f's3://{BUCKET_NAME}/{s3_file_path}',
            index=False,
            dtype=dtypes,
        )

    logging.info("File Uploaded to S3")
    return {"status": "OK"}


main()
