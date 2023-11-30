from datetime import datetime, timedelta
import pandas as pd
import logging
import awswrangler as wr

logging.basicConfig(level=logging.INFO)

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


def clean_age_column(df: pd.DataFrame) -> pd.DataFrame:
    df = df[df['AGE'] >= 0]
    df = df[df['AGE'] <= 122]
    df = df.dropna(subset=['AGE'])

    return df


def main(handler=None, context=None):
    logging.info("Starting lambda_raw job")

    date, start_time, end_time = get_time_range()

    s3_file_path = f"raw/{date}-{end_time[:2]}.csv"

    df = wr.s3.read_csv(f's3://{BUCKET_NAME}/{s3_file_path}')

    # Clean age column
    df_cleaned = clean_age_column(df)

    if df_cleaned is not None:
        s3_file_path = f"trusted/{date}-{end_time[:2]}.csv"

        # Dataframe -> CSV
        wr.s3.to_csv(
            df=pd.DataFrame(df_cleaned),
            path=f's3://{BUCKET_NAME}/{s3_file_path}',
            index=False,
        )

    logging.info(f"Saved cleaned data")

    return {"status": "OK"}


if __name__ == "__main__":
    main()
