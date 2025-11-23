from fastapi import FastAPI, HTTPException
import pandas as pd
from datetime import datetime, date
from typing import Optional
app = FastAPI()


def dataframe_validation(dataframe):
        """
        Performs data validation on ingested tick data.

        Steps:
        1. Checks for Missing values
        2. Parses 'date' column into ISO8601 format
        3. Checks Data Uniqueness

        Raises AssertionError if validation fails
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

# ensure dataframe is created and validated
try:
    df = pd.read_excel('../data/Tick Sightings.xlsx')
    df = dataframe_validation(df)
except FileNotFoundError:
    print("File not found")
    df = pd.DataFrame()
except AssertionError as err:
    print(f"Validation failed: {err}")

    df = pd.DataFrame() # fallback so app doesnt fail

@app.get("/sightings")
def sightings( 
    location: Optional[str] = None,
    specific_date: Optional[date] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
              ):
    """
    Retrieves tick sightings with optional filters

    location: Provides sightings in that city
    specific_date: Provides sightings for a specified date
    start_date: Provides sightings after start_date
    end_date: Provides sightings after end_date
    """
    if df.empty:
        raise HTTPException(status_code=503, detail="DData unavailable")
    
    copied_data = df.copy()
    
    if location:
        copied_data = copied_data[copied_data['location'].str.contains(location, case=False)]

    if specific_date:
        copied_data = copied_data[copied_data['date'].dt.date == specific_date]

    if start_date:
        copied_data = copied_data[copied_data['date'] >= start_date]

    if end_date:
        copied_data = copied_data[copied_data['date'] <= end_date]

    if copied_data.empty:
        raise HTTPException(status_code=404, detail="Empty dataset")
    return copied_data.to_dict(orient="records")


@app.get("/sightings/{id}")
def sightings_id(id: str):
    """
    Finds and returns returns sighting by given id
    """
    if df.empty:
        raise HTTPException(status_code=503, detail="DData unavailable")
    
    result = df[df['id'] == id]
    if result.empty:
        raise HTTPException(status_code=404, detail="Empty dataset")
    return result.to_dict(orient="records")[0]

@app.get("/reports/region-counts")
def region_counts(species: Optional[str] = None):
    """
    Counts then returns the total number of sightings for each region.
    If 'species' is provided, it filters the data to that specific species first.
    """
    if df.empty:
        raise HTTPException(status_code=503, detail="DData unavailable")
    
    copied_data = df.copy()

    if species:
        copied_data = copied_data[copied_data['species'].str.contains(species, case=False)]

    if copied_data.empty:
        raise HTTPException(status_code=404, detail="Empty dataset")
    return copied_data['location'].value_counts().to_dict()

@app.get("/reports/trends")
def region_trends():
    """
    Placeholder
    """
    if df.empty:
        raise HTTPException(status_code=503, detail="DData unavailable")
    
    return {"Message": "Not implemented yet"}

