from datetime import datetime, timedelta
import pandas as pd
import logging
import awswrangler as wr

logging.basicConfig(level=logging.INFO)

# load_dotenv()
# BUCKET_NAME = os.getenv('BUCKET_NAME')
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


def clean_age_column(df: pd.DataFrame) -> pd.DataFrame:
    df = df[df['AGE'] >= 0]
    df = df[df['AGE'] <= 122]
    df = df.dropna(subset=['AGE'])

    return df


def read_raw_csv_from_s3(bucket_name, file_date):
    try:
        return wr.s3.read_csv(f's3://{bucket_name}/raw/{file_date}.csv')
    except Exception as e:
        logging.error(f"Failed to read CSV from S3. Error: {e}")
        return None


def write_trusted_df_to_s3(df_cleaned, bucket_name, file_date):
    try:
        wr.s3.to_csv(
            df=pd.DataFrame(df_cleaned),
            path=f's3://{bucket_name}/trusted/{file_date}.csv',
            index=False,
        )
    except Exception as e:
        logging.error(f"Failed to write DataFrame to S3. Error: {e}")
        return False
    return True


def main(handler=None, context=None):
    logging.info("Starting lambda_raw job")

    try:
        file_date = get_path_info()
        df = read_raw_csv_from_s3(BUCKET_NAME, file_date)
        df_cleaned = clean_age_column(df)
        if df_cleaned is not None:
            if not write_trusted_df_to_s3(df_cleaned, BUCKET_NAME, file_date):
                return {"status": "Failed"}
    except Exception as e:
        logging.error(f"Failed to process data. Error: {e}")
        return {"status": "Failed"}

    logging.info("Cleaned file uploaded to S3")
    return {"status": "OK"}


if __name__ == "__main__":
    main()
