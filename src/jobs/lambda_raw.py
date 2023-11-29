import requests
from os import getenv
from datetime import datetime, timedelta
import pandas as pd
import logging
import awswrangler as wr


def get_data_df(hour: str):
    logging.info("Getting data from API")

    if df_list:
        
        df = pd.concat(df_list, ignore_index=True)

        # cleaning code
        df["DIED"] = df["DATE_DIED"].eq("9999-99-99")
        df.drop(df[(df["AGE"] < 0) | (df["AGE"] > 110) | (df["AGE"].isnull())].index, inplace=True)
        df["FULL_NAME"] = df["FIRST_NAME"] + " " + df["LAST_NAME"]

        def idioms(x):
            if x["AGE"] > 21 and x["SEX"] == "Female":
                return "Mrs " + x["FULL_NAME"]
            elif x["AGE"] > 21 and x["SEX"] == "Male":
                return "Mr " + x["FULL_NAME"]
            else:
                return x["FULL_NAME"]

        df["FULL_NAME"] = df.apply(idioms, axis=1)

        max_age = df["AGE"].max()
        age_bins = list(range(0, max_age + 10, 10))
        df["AGE_GROUP"] = pd.cut(df["AGE"], bins=age_bins, 
        labels=[f"{i}-{i+9}" for i in range(0, max_age, 10)], right=False)

        return df

    return pd.DataFrame()

def main(handler=None, context=None):
    logging.info("Starting lambda_raw job")

    return {"status": "OK"}


if __name__ == "__main__":
    # Only for local development
    from dotenv import load_dotenv

    load_dotenv()
    main()
