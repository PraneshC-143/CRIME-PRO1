"""
Data loading and preprocessing module
"""

import pandas as pd
import streamlit as st
import os


@st.cache_data
def load_data():
    """
    Load and preprocess crime data from Excel file
    
    Returns:
        tuple: (DataFrame, crime_columns)
    """
    try:
        path = os.path.join(os.path.dirname(__file__), "districtwise-ipc-crimes.xlsx")
        
        if not os.path.exists(path):
            st.error(f"❌ Data file not found: {path}")
            return None, None
        
        # Read Excel file
        df = pd.read_excel(path, sheet_name="districtwise-ipc-crimes")
        
        # Drop unnecessary columns
        cols_to_drop = ["id", "state_code", "district_code"]
        df.drop(columns=cols_to_drop, inplace=True, errors='ignore')
        
        # Identify crime columns (numeric columns excluding 'year')
        crime_cols = df.select_dtypes(include="number").columns.drop("year", errors='ignore')
        
        # Create total crimes column
        df["total_crimes"] = df[crime_cols].sum(axis=1)
        
        # Ensure year is integer
        df["year"] = df["year"].astype(int)
        
        return df, crime_cols
    
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        return None, None


def validate_data(df):
    """
    Validate data integrity
    
    Returns:
        bool: True if valid, False otherwise
    """
    if df is None or df.empty:
        return False
    
    required_columns = ["state_name", "district_name", "year"]
    return all(col in df.columns for col in required_columns)


def filter_data(df, state, district, year_range, crime_types):
    """
    Filter dataframe based on user selections
    
    Args:
        df: DataFrame
        state: Selected state
        district: Selected district
        year_range: Tuple (min_year, max_year)
        crime_types: List of crime type columns
    
    Returns:
        DataFrame: Filtered dataframe
    """
    filtered = df[
        (df["state_name"] == state) &
        (df["year"] >= year_range[0]) &
        (df["year"] <= year_range[1])
    ]
    
    if district != "All Districts":
        filtered = filtered[filtered["district_name"] == district]
    
    filtered = filtered.copy()
    filtered["crime_sum"] = filtered[crime_types].sum(axis=1)
    
    return filtered