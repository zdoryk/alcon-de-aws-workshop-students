import sys
import pandas as pd
import awswrangler as wr
import logging
from datetime import datetime, timedelta
from awsglue.utils import getResolvedOptions

args = getResolvedOptions(sys.argv, ["S3_BUCKET_NAME"])
bucket_name = args["S3_BUCKET_NAME"]


# Function to create the full name with title
def create_full_name(row):
    pass


def add_age_group(df):
    pass


def main():
    logging.info("Starting Glue enriched job")


main()
