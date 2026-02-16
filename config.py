"""
Configuration file for CrimeScope Dashboard
"""

# Page Configuration
PAGE_TITLE = "CrimeScope | IPC Crime Intelligence"
PAGE_LAYOUT = "wide"
PAGE_ICON = "📊"

# Data Configuration
DATA_FILE = "districtwise-ipc-crimes.xlsx"
SHEET_NAME = "districtwise-ipc-crimes"
COLUMNS_TO_DROP = ["id", "state_code", "district_code"]

# Historical Data Configuration
HISTORICAL_DATA_ENABLED = True
HISTORICAL_DATA_FILE = "historical-crime-data-complete.csv"
CRIME_DATASET_REPO = "https://raw.githubusercontent.com/avinashladdha/CrimeDataset/master"
MIN_YEAR = 1969
MAX_YEAR = 2023

# UI Configuration
PRIMARY_COLOR = "#1f77b4"
BACKGROUND_COLOR = "#fafafa"
SIDEBAR_COLOR = "#f9fafb"
BORDER_COLOR = "#e5e7eb"

# Visualization Configuration
PLOT_HEIGHT = 400
KPI_DECIMAL_PLACES = 0
TOP_DISTRICTS_COUNT = 10

# ML Configuration
TEST_SIZE = 0.2
RANDOM_STATE = 42
N_ESTIMATORS = 100