#!/bin/bash
# Example script for fetching and integrating historical crime data

echo "============================================================"
echo "Historical Crime Data Integration - Example Usage"
echo "============================================================"

# Check if CrimeDataset path is provided
if [ -z "$1" ]; then
    echo "Usage: $0 /path/to/CrimeDataset"
    echo ""
    echo "Example:"
    echo "  $0 ~/Downloads/CrimeDataset"
    echo ""
    echo "Download CrimeDataset from:"
    echo "  https://github.com/avinashladdha/CrimeDataset"
    exit 1
fi

DATASET_PATH="$1"

# Verify path exists
if [ ! -d "$DATASET_PATH" ]; then
    echo "❌ Error: Directory not found: $DATASET_PATH"
    exit 1
fi

echo "✓ CrimeDataset path: $DATASET_PATH"
echo ""

# Run the fetcher script
echo "Running historical data fetcher..."
echo "This may take several minutes depending on the number of years..."
echo ""

python scripts/fetch_historical_data.py --local-path "$DATASET_PATH"

if [ $? -eq 0 ]; then
    echo ""
    echo "============================================================"
    echo "✅ Success! Historical data has been integrated."
    echo "============================================================"
    echo ""
    echo "Next steps:"
    echo "1. Restart your Streamlit app:"
    echo "   streamlit run streamlit_app.py"
    echo ""
    echo "2. The dashboard will now show data from 1969-2023"
    echo "3. Year slider will automatically adjust to full range"
    echo ""
else
    echo ""
    echo "❌ Error: Data fetching failed"
    echo "Please check the error messages above"
    exit 1
fi
