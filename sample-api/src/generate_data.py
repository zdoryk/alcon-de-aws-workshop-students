import pandas as pd
import random
from datetime import datetime, timedelta
import os
import awswrangler as wr
from names import get_random_first_name, get_random_last_name

random.seed(42)


def generate_one_record(date: datetime):
    # Generate random values for each column
    first_name = get_random_first_name()
    last_name = get_random_last_name()
    sex = random.choice(['Male', 'Female'])

    # Introduce randomness in the AGE column
    age = random.randint(1, 100)

    # Add some outliers, blank values, and negative values
    if random.random() < 0.2:
        if random.random() < 0.25:
            age = None  # Blank value
        elif random.random() < 0.1:
            age = -1  # Negative value
        elif random.random() < 0.15:
            age = random.randint(150, 170)  # Outlier (unrealistically high age)

    # Generate a random date of death between 2019-01-01 and 2023-12-31
    start_date = datetime(2023, 10, date.day)
    end_date = datetime(2023, 10, date.day)

    # Introduce randomness to have some patients with "9999-99-99" as the date of death
    if random.random() < 0.2:
        date_died = "9999-99-99"
    else:
        date_died = (start_date + timedelta(days=random.randint(0, (end_date - start_date).days))).strftime(
            '%Y-%m-%d')

    # Append the data as a dictionary
    return {
        'FIRST_NAME': first_name,
        'LAST_NAME': last_name,
        'SEX': sex,
        'AGE': age,
        'DATE_DIED': date_died,
        'INGESTION_DATETIME': date.strftime('%Y-%m-%d %H:%M:%S'),
    }


# Set a seed for reproducibility
def lambda_handler(event, context):
    today = datetime.utcnow()
    data = []
    bucket_name = os.environ['BUCKET_NAME']
    for _ in range(100):
        data.append(generate_one_record(today))

    df = pd.DataFrame(data)
    filename = today.strftime('%d_%m_%Y_%H_%M.csv')

    wr.s3.to_csv(df, f's3://{bucket_name}/{filename}', index=False)
    return {"Status": "OK"}


if __name__ == '__main__':
    lambda_handler(None, None)
