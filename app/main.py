
import pandas as pd

# Data ingestion into memory
df = pd.read_excel('./data/Tick sightings.xlsx') 

def dataframe_validation(dataframe):
    """
    Performs basic data validation on ingested tick data.

    Checks for:
    Missing values
    Correct date format
    Data Uniqueness
    """
    # Ensure data has no missing values
    assert dataframe.isna().sum().sum() == 0, "Dataset contains missing values"

    # Date format Validation
    temp_dates = pd.to_datetime(
        dataframe['date'], # gets date column
        format="%Y-%m-%dT%H:%M:%S", # ensures ISO 8601 format
        errors="coerce" # returns NaT if invalid date format found
    )
    # Verify no rows failed date parsing
    failed_rows = temp_dates.isna().sum()
    assert failed_rows == 0, "Date format incorrect"

    # ID uniqueness validation
    assert dataframe['id'].is_unique, "Data ids should be unique"

    print("Validation tests passed")
    return True

# Runs dataset validation checks
dataframe_validation(df)
print(df.head())