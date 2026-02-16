"""
Historical Crime Data Fetcher
Downloads and processes crime data from 1969-2016 from CrimeDataset repository
"""

import os
import sys
import pandas as pd
import requests
from typing import List, Dict, Optional
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import CRIME_DATASET_REPO, MIN_YEAR, MAX_YEAR, HISTORICAL_DATA_FILE, DATA_FILE


def download_year_data(year: int, local_path: Optional[str] = None) -> Optional[pd.DataFrame]:
    """
    Download data for a specific year from GitHub or local path
    
    Args:
        year: Year to download (1969-2016)
        local_path: Optional local path to CrimeDataset folder
    
    Returns:
        DataFrame with year's data or None if failed
    """
    if local_path:
        # Read from local downloaded CrimeDataset folder
        year_folder = os.path.join(local_path, f"{year}.0")
        if not os.path.exists(year_folder):
            print(f"⚠️  Year folder not found: {year_folder}")
            return None
        return process_year_folder(year_folder, year)
    else:
        # Download from GitHub (not implemented in this version)
        print(f"⚠️  Remote download not implemented. Please provide local_path to CrimeDataset.")
        return None


def process_year_folder(year_folder: str, year: int) -> Optional[pd.DataFrame]:
    """
    Process all CSV files in a year folder
    
    Args:
        year_folder: Path to year folder
        year: Year number
    
    Returns:
        Combined DataFrame for the year
    """
    csv_files = [f for f in os.listdir(year_folder) if f.endswith('.csv')]
    
    if not csv_files:
        print(f"⚠️  No CSV files found in {year_folder}")
        return None
    
    year_dfs = []
    
    for csv_file in csv_files:
        try:
            file_path = os.path.join(year_folder, csv_file)
            df = pd.read_csv(file_path)
            
            # Look for district-wise data (contains 'district' in filename or columns)
            if 'district' in csv_file.lower() or 'DISTRICT' in df.columns:
                year_dfs.append(df)
            elif 'District' in df.columns or 'district_name' in df.columns:
                year_dfs.append(df)
                
        except Exception as e:
            print(f"⚠️  Error reading {csv_file}: {str(e)}")
            continue
    
    if not year_dfs:
        print(f"⚠️  No valid district data found for year {year}")
        return None
    
    # Combine all dataframes for this year
    combined_df = pd.concat(year_dfs, ignore_index=True)
    combined_df['year'] = year
    
    return combined_df


def standardize_schema(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize column names to match current schema
    
    Args:
        df: Input DataFrame
    
    Returns:
        DataFrame with standardized columns
    """
    # Common column name mappings
    column_mappings = {
        'STATE': 'state_name',
        'State': 'state_name',
        'STATE_NAME': 'state_name',
        'DISTRICT': 'district_name',
        'District': 'district_name',
        'DISTRICT_NAME': 'district_name',
        'YEAR': 'year',
        'Year': 'year',
        # Add more mappings as needed
    }
    
    # Rename columns
    df = df.rename(columns=column_mappings)
    
    # Convert column names to lowercase and replace spaces with underscores
    df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('-', '_')
    
    # Ensure required columns exist
    required_cols = ['state_name', 'district_name', 'year']
    for col in required_cols:
        if col not in df.columns:
            print(f"⚠️  Required column missing: {col}")
    
    return df


def combine_all_years(local_path: str, start_year: int = 1969, end_year: int = 2016) -> pd.DataFrame:
    """
    Combine all years into single dataframe
    
    Args:
        local_path: Path to CrimeDataset folder
        start_year: Starting year (default: 1969)
        end_year: Ending year (default: 2016)
    
    Returns:
        Combined DataFrame with all years
    """
    all_years_data = []
    
    print(f"📊 Processing data from {start_year} to {end_year}...")
    
    for year in range(start_year, end_year + 1):
        print(f"Processing year {year}...", end=' ')
        
        year_df = download_year_data(year, local_path)
        
        if year_df is not None:
            # Standardize schema
            year_df = standardize_schema(year_df)
            all_years_data.append(year_df)
            print(f"✓ ({len(year_df)} records)")
        else:
            print("✗ (no data)")
    
    if not all_years_data:
        raise ValueError("No data could be processed from any year")
    
    # Combine all years
    combined_df = pd.concat(all_years_data, ignore_index=True)
    
    print(f"\n✅ Successfully processed {len(all_years_data)} years")
    print(f"   Total records: {len(combined_df)}")
    
    return combined_df


def merge_with_current_data(historical_df: pd.DataFrame, output_path: str) -> pd.DataFrame:
    """
    Merge historical data with current data
    
    Args:
        historical_df: Historical data (1969-2016)
        output_path: Path to save merged data
    
    Returns:
        Merged DataFrame
    """
    # Load current data
    current_data_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        DATA_FILE
    )
    
    if not os.path.exists(current_data_path):
        print(f"⚠️  Current data file not found: {current_data_path}")
        print("   Saving historical data only...")
        historical_df.to_csv(output_path, index=False)
        return historical_df
    
    try:
        # Read current data
        current_df = pd.read_excel(current_data_path, sheet_name='districtwise-ipc-crimes')
        
        # Drop unnecessary columns from current data
        cols_to_drop = ['id', 'state_code', 'district_code']
        current_df = current_df.drop(columns=cols_to_drop, errors='ignore')
        
        # Get common columns
        common_cols = list(set(historical_df.columns) & set(current_df.columns))
        
        # Ensure both have at least the required columns
        required_cols = ['state_name', 'district_name', 'year']
        for col in required_cols:
            if col not in common_cols:
                print(f"⚠️  Cannot merge: missing required column '{col}' in one dataset")
                historical_df.to_csv(output_path, index=False)
                return historical_df
        
        # Fill missing columns with 0
        for col in current_df.columns:
            if col not in historical_df.columns and col not in ['id', 'state_code', 'district_code']:
                historical_df[col] = 0
        
        for col in historical_df.columns:
            if col not in current_df.columns:
                current_df[col] = 0
        
        # Merge dataframes
        merged_df = pd.concat([historical_df, current_df], ignore_index=True)
        
        # Sort by year
        merged_df = merged_df.sort_values(['year', 'state_name', 'district_name'])
        
        # Save merged data
        merged_df.to_csv(output_path, index=False)
        
        print(f"\n✅ Merged data saved to: {output_path}")
        print(f"   Historical records: {len(historical_df)}")
        print(f"   Current records: {len(current_df)}")
        print(f"   Total records: {len(merged_df)}")
        print(f"   Year range: {merged_df['year'].min()} - {merged_df['year'].max()}")
        
        return merged_df
        
    except Exception as e:
        print(f"❌ Error merging data: {str(e)}")
        print("   Saving historical data only...")
        historical_df.to_csv(output_path, index=False)
        return historical_df


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description='Fetch and process historical crime data (1969-2016)'
    )
    parser.add_argument(
        '--local-path',
        type=str,
        required=True,
        help='Path to local CrimeDataset folder'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output file path (default: historical-crime-data-complete.csv in root)'
    )
    parser.add_argument(
        '--start-year',
        type=int,
        default=1969,
        help='Start year (default: 1969)'
    )
    parser.add_argument(
        '--end-year',
        type=int,
        default=2016,
        help='End year (default: 2016)'
    )
    parser.add_argument(
        '--no-merge',
        action='store_true',
        help='Do not merge with current data'
    )
    
    args = parser.parse_args()
    
    # Validate local path
    if not os.path.exists(args.local_path):
        print(f"❌ Error: Path does not exist: {args.local_path}")
        sys.exit(1)
    
    # Set output path
    if args.output:
        output_path = args.output
    else:
        output_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            HISTORICAL_DATA_FILE
        )
    
    try:
        print("=" * 60)
        print("🚀 Historical Crime Data Fetcher")
        print("=" * 60)
        
        # Combine all years
        historical_df = combine_all_years(args.local_path, args.start_year, args.end_year)
        
        # Merge with current data or save separately
        if args.no_merge:
            historical_df.to_csv(output_path, index=False)
            print(f"\n✅ Historical data saved to: {output_path}")
        else:
            merge_with_current_data(historical_df, output_path)
        
        print("\n" + "=" * 60)
        print("✅ Data processing complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
