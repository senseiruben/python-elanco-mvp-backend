from fastapi import FastAPI, HTTPException, Query
import pandas as pd
from datetime import datetime, date
from typing import Optional
import os

app = FastAPI()


def dataframe_validation(dataframe):
        """
        Performs data validation and transformation on ingested tick data.

        Tasks:
        1. Checks for Missing (NaN) values.
        2. Changes 'date' columns into datetime objects.
        3. Ensures 'id' column contains no duplicates.

        Args:
            dataframe: Contains excel data.
        
        Returns:
            pd.dataframe: Complete validation and transformation of original data.

        Raises:
            AssertionError: If validation fails.
        """
        # 1. Ensure data has no missing values
        assert dataframe.isna().sum().sum() == 0, "Dataset contains missing values"

        # 2. Transform into datetime format
        dataframe['date'] = pd.to_datetime(
            dataframe['date'], # gets date column
            format="%Y-%m-%dT%H:%M:%S", # ensures ISO 8601 format
            errors="coerce" # returns NaT if invalid date format found
        )
        # Verify no rows failed date parsing
        failed_rows = dataframe['date'].isna().sum()
        assert failed_rows == 0, "Date format incorrect"

        # 3. ID uniqueness validation
        assert dataframe['id'].is_unique, "Data ids should be unique"

        print("Validation tests passed")
        return dataframe

# Data ingestion
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, '..', 'data', 'Tick Sightings.xlsx')
try:
    df = pd.read_excel(file_path)
    df = dataframe_validation(df)
except FileNotFoundError:
    print("File not found")
    df = pd.DataFrame()
except AssertionError as err:
    print(f"Validation failed: {err}")
    df = pd.DataFrame() # fallback so app doesnt fail


# Endpoints

@app.get("/sightings")
def sightings( 
    location: Optional[str] = None,
    specific_date: Optional[date] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
              ):
    """
    Retrieves tick sightings with optional filters

    Args:
        location (string, optional): case-insensitive, looks for city.
        specific_date (date, optional): Exact date search in format (YYYY/MM/DD).
        start_date (datetime, optional): Filters results to be on or after this date.
        end_date (datetime, optional): Filters results to be on or before this date.

    Returns:
        list: a list of sighting records in JSON format.
    """
    if df.empty:
        raise HTTPException(status_code=503, detail="Data unavailable")
    
    copied_data = df.copy()
    
    if location:
        copied_data = copied_data[copied_data['location'].str.contains(location, case=False, na=False)]

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

    Args:
        id (string): Unique identifier

    Returns:
        dict: Single sighting record
    """
    if df.empty:
        raise HTTPException(status_code=503, detail="Data unavailable")
    
    result = df[df['id'] == id]
    if result.empty:
        raise HTTPException(status_code=404, detail=f"id not found: {id}")
    return result.to_dict(orient="records")[0]

@app.get("/reports/region-counts")
def region_counts(species: Optional[str] = None):
    """
    Counts then returns the total number of sightings for each region.
    
    Args:
        species (string, optional): Filters count to specific species.
    
    Return:
        dictionary: Region name and its count.

    """
    if df.empty:
        raise HTTPException(status_code=503, detail="Data unavailable")
    
    copied_data = df.copy()

    if species:
        copied_data = copied_data[copied_data['species'].str.contains(species, case=False, na=False)]

    if copied_data.empty:
        raise HTTPException(status_code=404, detail="Empty dataset")
    return copied_data['location'].value_counts().to_dict()

@app.get("/reports/trends")
def region_trends(frequency: str = Query("M", enum=["W","M"])):
    """
    Returns tick sighting trends based on frequency.

    Args:
        frequency (string): 'W' for weekly and 'M' for monthly.

    Returns:
        dict: Dates (YYYY-MM-DD format) and sighting counts.
    """
    if df.empty:
        raise HTTPException(status_code=503, detail="Data unavailable")
    
    # set date to index to allow sampling
    copied_df = df.set_index('date')

    # resample counts rows based on time
    trends = copied_df.resample(frequency).size()

    # assigns it
    trends.index = trends.index.strftime('%Y-%m-%d')
    return trends.to_dict()

