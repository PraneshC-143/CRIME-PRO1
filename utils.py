import pandas as pd

def load_data(file_path):
    """Load data from CSV file."""
    return pd.read_csv(file_path)

def save_data(data, file_path):
    """Save DataFrame to CSV."""
    data.to_csv(file_path, index=False)

def clean_data(data):
    """Clean the DataFrame by removing NaN values."""
    return data.dropna()

def format_date(date_str):
    """Convert date string to datetime."""
    return pd.to_datetime(date_str)

# Add more utility functions as needed
