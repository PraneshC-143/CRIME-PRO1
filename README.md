# IPC State-wise Crime Analysis V2

## Introduction
This repository contains the upgraded crime analysis dashboard, which provides an interactive platform for analyzing crime data across different states in India. The dashboard utilizes the latest technologies to offer insightful data visualization and reporting features with **54 years of historical data (1969-2023)**.

## Features
- **State-wise Crime Data Visualization**: Users can view crime data for each state, allowing for comparative analysis.
- **Historical Data Integration**: Analyze crime trends from 1969 to 2023 (54 years of data)
- **Interactive Charts**: The dashboard includes interactive charts that enable users to filter and customize their views of the data.
- **ML-Powered Predictions**: Train models on 50+ years of data for accurate crime forecasting
- **Data Sources**: Comprehensive listings of data sources used for analytics, including links to datasets and documentation.
- **User-Friendly Interface**: A simple and straightforward user interface designed for ease of use.

## Data Coverage

### Current Data (Built-in)
- **Years**: 2017-2022
- **Source**: District-wise IPC crimes Excel file
- **Records**: ~5,322 district-level entries

### Historical Data (Optional)
- **Years**: 1969-2016 (48 years)
- **Source**: [CrimeDataset by avinashladdha](https://github.com/avinashladdha/CrimeDataset)
- **Coverage**: State and district-wise IPC and SLL crimes
- **Total Coverage**: 1969-2023 (54 years when combined)

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup Instructions

1. **Clone the repository**
```bash
git clone https://github.com/PraneshC-143/IPC-State-wise-Crime-Analysis-V2.git
cd IPC-State-wise-Crime-Analysis-V2
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the Streamlit app**
```bash
streamlit run streamlit_app.py
```

4. **Access the dashboard**
Open your web browser and navigate to `http://localhost:8501`

## Historical Data Integration

### Quick Start

To integrate historical crime data from 1969-2016, follow these steps:

#### Step 1: Download the CrimeDataset

Download and extract the CrimeDataset repository:
```bash
# Clone the CrimeDataset repository
git clone https://github.com/avinashladdha/CrimeDataset.git
```

Or download the ZIP file manually from: https://github.com/avinashladdha/CrimeDataset

#### Step 2: Run the Data Fetcher Script

Process and combine historical data with current data:

```bash
python scripts/fetch_historical_data.py --local-path /path/to/CrimeDataset
```

**Options:**
- `--local-path`: Path to the downloaded CrimeDataset folder (required)
- `--output`: Custom output file path (default: historical-crime-data-complete.csv)
- `--start-year`: Starting year for processing (default: 1969)
- `--end-year`: Ending year for processing (default: 2016)
- `--no-merge`: Save historical data separately without merging

**Example:**
```bash
# Process all years and merge with current data
python scripts/fetch_historical_data.py --local-path ~/Downloads/CrimeDataset

# Process specific year range
python scripts/fetch_historical_data.py --local-path ~/Downloads/CrimeDataset --start-year 1990 --end-year 2016

# Save without merging
python scripts/fetch_historical_data.py --local-path ~/Downloads/CrimeDataset --no-merge --output historical-only.csv
```

#### Step 3: Verify Integration

After running the script, you should see a new file `historical-crime-data-complete.csv` in the root directory. Restart the Streamlit app to load the combined dataset:

```bash
streamlit run streamlit_app.py
```

The dashboard will automatically detect and load the historical data, showing year range from 1969-2023.

### Data Processing Details

The `fetch_historical_data.py` script performs the following operations:

1. **Reads year folders** (1969.0 to 2016.0) from CrimeDataset
2. **Processes CSV files** in each year folder
3. **Standardizes column names** to match current schema
4. **Combines all years** into a single dataframe
5. **Merges with current data** (2017-2022) from districtwise-ipc-crimes.xlsx
6. **Exports combined data** as CSV for faster loading

### Configuration

Historical data integration can be configured in `config.py`:

```python
# Historical Data Configuration
HISTORICAL_DATA_ENABLED = True  # Enable/disable historical data
HISTORICAL_DATA_FILE = "historical-crime-data-complete.csv"  # Output filename
CRIME_DATASET_REPO = "https://raw.githubusercontent.com/avinashladdha/CrimeDataset/master"
MIN_YEAR = 1969  # Minimum year supported
MAX_YEAR = 2023  # Maximum year supported
```

## Data Schema

### Required Columns
- `state_name`: Name of the state
- `district_name`: Name of the district
- `year`: Year of the crime data

### Crime Columns
The dataset includes various IPC crime types such as:
- Murder, Rape, Kidnapping, Robbery, Theft
- Dowry deaths, Assault on women
- Riots, Dacoity, Burglary
- And many more...

Missing crime columns are automatically filled with 0 values.

## Usage

### Basic Navigation

1. **Select State**: Choose a state from the sidebar
2. **Select District**: Choose a specific district or "All Districts"
3. **Select Year Range**: Use the slider to select years (1969-2023 with historical data)
4. **Choose Crime Types**: Select specific crime types to analyze
5. **View Analytics**: Explore trends, predictions, and insights

### Features Available

- **Crime Trends**: View time-series trends for selected crimes
- **Top Districts**: See districts with highest crime rates
- **Heatmaps**: Visualize crime patterns across geography
- **Predictions**: ML-based forecasts for future crime rates
- **Statistics**: Comprehensive statistical analysis
- **Data Export**: Download filtered data for further analysis

## Attribution

This project uses crime data from multiple sources:

### Primary Data Source
- **Current Data (2017-2022)**: Built-in district-wise IPC crimes dataset

### Historical Data Source
- **Historical Data (1969-2016)**: [CrimeDataset by avinashladdha](https://github.com/avinashladdha/CrimeDataset)
  - Source: Government of India Open Data
  - License: As per source repository
  - Special thanks to @avinashladdha for compiling and organizing the historical dataset

## Technical Stack

- **Frontend**: Streamlit
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly, Matplotlib, Seaborn
- **Machine Learning**: Scikit-learn
- **Data Format**: Excel (XLSX), CSV

## Project Structure

```
IPC-State-wise-Crime-Analysis-V2/
├── streamlit_app.py              # Main Streamlit application
├── data_loader.py                # Data loading and preprocessing
├── config.py                     # Configuration settings
├── analytics.py                  # Statistical analysis functions
├── visualizations.py             # Plotting and charting functions
├── prediction.py                 # ML prediction models
├── utils.py                      # Utility functions
├── requirements.txt              # Python dependencies
├── districtwise-ipc-crimes.xlsx  # Current data (2017-2022)
├── historical-crime-data-complete.csv  # Combined data (1969-2023) [Generated]
├── scripts/
│   └── fetch_historical_data.py  # Historical data fetcher script
└── README.md                     # This file
```

## Troubleshooting

### Historical Data Not Loading

If historical data is not loading:

1. Check if `historical-crime-data-complete.csv` exists in the root directory
2. Verify `HISTORICAL_DATA_ENABLED = True` in `config.py`
3. Ensure the CSV file is not corrupted (check file size > 0)
4. Clear Streamlit cache: `streamlit cache clear`

### Data Fetcher Script Errors

If the fetcher script fails:

1. Verify the CrimeDataset path is correct
2. Check that year folders (e.g., `1969.0/`) exist in CrimeDataset
3. Ensure CSV files are present in year folders
4. Check Python version (3.8+ required)

### Performance Issues

For better performance with large datasets:

1. Use CSV format instead of Excel (faster loading)
2. Enable caching in Streamlit (already configured)
3. Filter data by year range to reduce memory usage
4. Consider processing a subset of years if full range is not needed

## Contribution
We welcome contributions to the project! Please check out the CONTRIBUTING.md for guidelines to get started.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- Special thanks to the data science community for providing invaluable datasets and tools that have made this project possible.
- Acknowledgment to @avinashladdha for the [CrimeDataset](https://github.com/avinashladdha/CrimeDataset) repository.
- Thanks to contributors who have worked tirelessly to enhance the functionality of the dashboard.
- Data sourced from Government of India Open Data platform.

## Contact
For any inquiries or feedback, please reach out to the project maintainer.

---
**Version**: 2.0  
**Last Updated**: 2026-02-16