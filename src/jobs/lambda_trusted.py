import awswrangler as wr
import pandas as pd
from os import getenv
from datetime import datetime, timedelta
import logging


logging.getLogger().setLevel(logging.INFO)


def clean_age_column(df: pd.DataFrame) -> pd.DataFrame:
    return df


def main(handler=None, context=None):
    logging.info("Starting lambda_raw job")

    return {"status": "OK"}


if __name__ == "__main__":
    # Only for local development
    from dotenv import load_dotenv

    load_dotenv()
    main()
