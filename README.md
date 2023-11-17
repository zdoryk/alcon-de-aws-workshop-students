
# Data Engineering Challenge

## Introduction
You will be working with a dataset of patients in the hospital.

Imagine that you have not only historic data as but the new data is constantly coming from the data source. 
The job will run every day at night while your stakeholders sleep. Your main goal is to create a
Data Lake on which we will have data for separate day in separate file for example:
S3_Bucket
|- covid_data=10-10-2023
|- covid_data=11-10-2023
You will need to make a request to this endpoint: "TODO", to get the data you will need to provide as a query parameters:
1. Date in the next format: "dd-mm-yyyy". 
2. Start_time in the next format: "HH:mm".
3. End_time in the next format: "HH:mm".

Also you will need to provide the AUTH_TOKEN, that you have in your .env file, 
**read this env variable from the file using Python code**.
Token should be in the headers as "Authorization: Bearer <TOKEN>". 



### You will need to clean the data and save it in the appropriate S3 bucket layer.
#### What should be cleaned:
1. Delete redundant column.
2. You will need to create a new column called "died" which will be a binary column with 0
  and 1 values. 0 means that the patient survived and 1 means that the patient died. If the pation has an actual date
  in the "DATE_DIED" column it means that the patient died. If the patient has "9999-99-99" in the "DATE_DIED" column
  it means that the patient survived.
3. Validate the data in the "AGE" column to ensure it makes sense.  If this column has any problems please fix
   them to work automatically in the future.
TODO. For example, ensure that there are
   - Handling Invalid Ages - no negative ages
   - Identify Outliers - no ages that are unrealistically high.
   - Identify Missing Values - no missing ages.

4. Age Grouping:
Create age groups/bins with a 10-year step (e.g., 0-10 years, 11-20 years, etc.) 
and assign each patient to their respective age group.

5. You have a column "SEX", "AGE", "FIRST_NAME", "LAST_NAME" using these values please create a new column where
   you will have a full name of the patient in the following format: "FIRST_NAME LAST_NAME". Also if the person
   is older than 21y.o.use "Mr" or "Mrs" if the person is male or a female.
   For example: "Mr. John Smith" or "Mrs. Jane Smith".

## Notes
### Please for all of the data manipulation use Pandas library that can be found here: https://pandas.pydata.org/docs/
### Remember after this cleaning you will need to save the data in the S3 bucket or to .csv if we are running out of time.