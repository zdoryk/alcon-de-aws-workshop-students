import sys
from awsglue.utils import getResolvedOptions
import awswrangler as wr
import logging
from datetime import datetime, timedelta
import pandas as pd

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
