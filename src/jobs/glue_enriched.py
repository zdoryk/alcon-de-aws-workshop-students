import awswrangler as wr
import logging
from datetime import datetime, timedelta
import pandas as pd

logging.basicConfig(level=logging.INFO)

BUCKET_NAME = 'alcon-workshop-data-746590502764'


def get_path_info():
    current_utc_datetime = datetime.utcnow()
    start_time_utc = current_utc_datetime - timedelta(hours=1)

    # Yesterday Check
    if start_time_utc.date() < current_utc_datetime.date():
        logging.error("Error: can't request data from the previous day.")
        raise ValueError("Can't request data from the previous day.")

    file_date = start_time_utc.strftime('%d-%m-%Y-%H')
    return file_date


def create_full_name(row):
    if row["AGE"] < 21:
        return f"{row['FIRST_NAME']} {row['LAST_NAME']}"
    title = "Mr" if row["SEX"] == "Male" else "Mrs"
    return f"{title}. {row['FIRST_NAME']} {row['LAST_NAME']}"


def add_age_group(df):
    bins = range(0, int(df['AGE'].max()) + 10, 10)
    labels = [f"{i}-{i+9}" for i in bins[:-1]]
    df['AGE_GROUP'] = pd.cut(df['AGE'], bins=bins, labels=labels, right=False)
    return df


def create_died_column(df):
    df['IS_DEAD'] = df['DATE_DIED'].apply(
        lambda x: True if x != '9999-99-99' else False)
    return df


def read_trusted_csv_from_s3(file_date):
    try:
        df = wr.s3.read_csv(
            f's3://{BUCKET_NAME}/trusted/{file_date}.csv'
        )
    except Exception as e:
        logging.error(f"Failed to load data: {e}")
        return None
    return df


def process_data(df):
    df['FULL_NAME'] = df.apply(create_full_name, axis=1)
    df = add_age_group(df)
    df = create_died_column(df)
    return df


def write_enriched_df_to_s3(df, dtypes, file_date, BUCKET_NAME):
    try:
        wr.s3.to_parquet(
            df=pd.DataFrame(df),
            path=f's3://{BUCKET_NAME}/enriched/{file_date}.parquet',
            index=False,
            dtype=dtypes,
        )
    except Exception as e:
        logging.error(f"Failed to write DataFrame to S3. Error: {e}")
        return {"status": "Failed"}
    return {"status": "OK"}


def main():
    logging.info("Starting Glue enriched job")

    try:
        file_date = get_path_info()
    except Exception as e:
        logging.error(e)
        return {"status": "Failed", "error": str(e)}

    df = read_trusted_csv_from_s3(file_date)

    df = process_data(df)
    logging.info("Finished processing data")

    dtypes = {
        'FIRST_NAME': 'varchar(50)',
        'LAST_NAME': 'varchar(50)',
        'SEX': 'varchar(7)',
        'AGE': 'smallint',
        'DATE_DIED': 'varchar(20)',
        'INGESTION_DATETIME': 'timestamp',
        'FULL_NAME': 'varchar(100)',
        'AGE_GROUP': 'varchar(7)',
        'IS_DEAD': 'boolean',
    }

    write_enriched_df_to_s3(df, dtypes, file_date, BUCKET_NAME)

    logging.info(f"Finished writing data to S3")
    return {"status": "OK"}


if __name__ == "__main__":
    main()
