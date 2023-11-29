import requests
from os import getenv
from datetime import datetime, timedelta
import pandas as pd
import logging
import awswrangler as wr


logging.getLogger().setLevel(logging.INFO)


def get_data_df(hour: str):
    logging.info("Getting data from API")


def main(handler=None, context=None):
    logging.info("Starting lambda_raw job")

    return {"status": "OK"}


if __name__ == "__main__":
    # Only for local development
    from dotenv import load_dotenv

    load_dotenv()
    main()
