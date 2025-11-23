from fastapi import FastAPI
import pandas as pd

app = FastAPI()


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
        dataframe['date'] = pd.to_datetime(
            dataframe['date'], # gets date column
            format="%Y-%m-%dT%H:%M:%S", # ensures ISO 8601 format
            errors="coerce" # returns NaT if invalid date format found
        )
        # Verify no rows failed date parsing
        failed_rows = dataframe['date'].isna().sum()
        assert failed_rows == 0, "Date format incorrect"

        # ID uniqueness validation
        assert dataframe['id'].is_unique, "Data ids should be unique"

        print("Validation tests passed")
        return dataframe




df = pd.read_excel('../data/Tick Sightings.xlsx')
df = dataframe_validation(df)   


@app.get("/sightings")
def sightings():
    data = df.copy()
    return data.to_dict(orient="records")


@app.get("/sightings/{id}")
def sightings_id(id: str):
    result = df[df['id'] == id]
    if result.empty:
        return {"Error": f"{id} not found"}
    return result.to_dict(orient="records")[0]

@app.get("/reports/region-counts")
def region_counts():
    return

@app.get("/reports/trends")
def region_trends():
    return

