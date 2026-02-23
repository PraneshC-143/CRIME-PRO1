"""
Script to generate projected crime data for 2023.
This uses a simple growth rate model (CAGR or moving average) 
to project 2023 crimes based on 2017-2022 data.
"""

import pandas as pd
import numpy as np
import os
import sys

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATA_FILE, SHEET_NAME

def calculate_projection(series):
    """
    Calculate projection for next year using weighted moving average
    of the last 3 years.
    """
    if len(series) < 3:
        return series.mean()
    
    # Weights for last 3 years (more weight to recent years)
    weights = np.array([0.2, 0.3, 0.5])
    last_3_years = series.iloc[-3:].values
    
    if len(last_3_years) < 3:
        return series.iloc[-1]
    
    try:
        # Ensure we have numeric data
        last_3_years = last_3_years.astype(float)
        projection = np.dot(last_3_years, weights)
        return max(0, int(projection))
    except Exception:
        # Fallback for non-numeric or problematic data
        return 0

def generate_projections():
    print("Generating projected data for 2023...")
    
    # Load existing data
    base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), DATA_FILE)
    if not os.path.exists(base_path):
        print(f"❌ Error: Data file not found at {base_path}")
        return

    df = pd.read_excel(base_path, sheet_name=SHEET_NAME)
    
    # Identify crime columns (numeric excluding metadata)
    metadata_cols = ['state_name', 'district_name', 'year']
    # Select only numeric columns first
    numeric_df = df.select_dtypes(include=[np.number])
    crime_cols = [col for col in numeric_df.columns if col not in metadata_cols and col not in ['id', 'state_code', 'district_code']]
    
    # Create a list to hold new rows
    new_rows = []
    
    # Group by state and district
    grouped = df.groupby(['state_name', 'district_name'])
    
    count = 0
    total_groups = len(grouped)
    
    for (state, district), group in grouped:
        # Sort by year to ensure correct order
        group = group.sort_values('year')
        
        # Create a new row for 2023
        new_row = {
            'state_name': state,
            'district_name': district,
            'year': 2023
        }
        
        # Calculate projection for each crime type
        for col in crime_cols:
            history = group[col]
            # Simple projection logic
            projection = calculate_projection(history)
            new_row[col] = projection
            
        new_rows.append(new_row)
        
        count += 1
        if count % 100 == 0:
            print(f"   Processed {count}/{total_groups} districts...")

    # Create DataFrame for 2023
    df_2023 = pd.DataFrame(new_rows)
    
    # Save to CSV
    output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw", "projected_2023.csv")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    df_2023.to_csv(output_path, index=False)
    print(f"\nProjected data saved to: {output_path}")
    print(f"   Generated {len(df_2023)} rows for year 2023")
    
    return df_2023

if __name__ == "__main__":
    generate_projections()
