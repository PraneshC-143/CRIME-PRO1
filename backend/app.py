import pandas as pd
import numpy as np
import os
from flask import Flask, jsonify, request
from flask_cors import CORS

try:
    from sklearn.linear_model import LinearRegression
    has_sklearn = True
except ImportError:
    has_sklearn = False

app = Flask(__name__)
# Enable CORS so the HTML frontend can query the Python API seamlessly
CORS(app)

# Global dataset cache
_DATA_CACHE = None

def get_data():
    """Load and preprocess the dataset"""
    global _DATA_CACHE
    if _DATA_CACHE is not None:
        return _DATA_CACHE
        
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "districtwise-ipc-crimes.xlsx")
    if not os.path.exists(data_path):
        return None
        
    df = pd.read_excel(data_path, sheet_name="districtwise-ipc-crimes")
    cols_to_drop = ["id", "state_code", "district_code"]
    df.drop(columns=[col for col in cols_to_drop if col in df.columns], inplace=True)
    df["year"] = df["year"].astype(int)
    
    crime_cols = df.select_dtypes(include="number").columns.drop("year", errors='ignore')
    df[crime_cols] = df[crime_cols].fillna(0)
    df["total_crimes"] = df[crime_cols].sum(axis=1)
    
    _DATA_CACHE = (df, crime_cols.tolist())
    return _DATA_CACHE

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "ml_enabled": has_sklearn})


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """
    Returns high-level statistics: total crimes, YoY growth, and top state.
    Can be filtered by state and year_range.
    """
    data = get_data()
    if not data:
        return jsonify({"error": "Dataset not found"}), 404
        
    df, _ = data
    
    # Optional Filtering
    state = request.args.get('state', 'all')
    try:
        min_year = int(request.args.get('min_year', df['year'].min()))
        max_year = int(request.args.get('max_year', df['year'].max()))
    except ValueError:
        return jsonify({"error": "Invalid year format"}), 400

    filtered_df = df[(df['year'] >= min_year) & (df['year'] <= max_year)]
    if state.lower() != 'all':
        filtered_df = filtered_df[filtered_df['state_name'].str.lower() == state.lower()]

    if filtered_df.empty:
         return jsonify({"total_crimes": 0, "yoy_growth": 0, "top_state": "None", "dominant_crime": "None"})

    total_crimes = int(filtered_df['total_crimes'].sum())
    
    # Calculate YoY (Current Max Year vs Previous Year)
    yearly_totals = filtered_df.groupby('year')['total_crimes'].sum()
    yoy_growth = 0
    if len(yearly_totals) >= 2:
        last_year = yearly_totals.iloc[-1]
        prev_year = yearly_totals.iloc[-2]
        if prev_year > 0:
            yoy_growth = ((last_year - prev_year) / prev_year) * 100

    # Top State
    top_state = "Multiple"
    top_state_crimes = 0
    if state.lower() == 'all':
        state_totals = filtered_df.groupby('state_name')['total_crimes'].sum().sort_values(ascending=False)
        if not state_totals.empty:
            top_state = state_totals.index[0]
            top_state_crimes = int(state_totals.iloc[0])
    
    # Dominant Crime
    crime_cols = [col for col in filtered_df.columns if col not in ['state_name', 'district_name', 'year', 'total_crimes']]
    crime_totals = filtered_df[crime_cols].sum().sort_values(ascending=False)
    dominant_crime = "None"
    dominant_crime_count = 0
    if not crime_totals.empty:
        dominant_crime = crime_totals.index[0].replace('_', ' ').title()
        dominant_crime_count = int(crime_totals.iloc[0])

    return jsonify({
        "total_crimes": total_crimes,
        "yoy_growth": round(yoy_growth, 2),
        "top_state": top_state,
        "top_state_crimes": top_state_crimes,
        "dominant_crime": dominant_crime,
        "dominant_crime_count": dominant_crime_count
    })


@app.route('/api/chart/trend', methods=['GET'])
def get_trend_data():
    """Returns Yearly Total Crimes for charting."""
    data = get_data()
    if not data:
         return jsonify({"error": "Dataset not found"}), 404
         
    df, _ = data
    state = request.args.get('state', 'all')
    
    if state.lower() != 'all':
        df = df[df['state_name'].str.lower() == state.lower()]
        
    yearly_totals = df.groupby('year')['total_crimes'].sum().reset_index()
    
    # Prepare for Chart.js
    labels = yearly_totals['year'].astype(str).tolist()
    values = yearly_totals['total_crimes'].tolist()
    
    return jsonify({
        "labels": labels,
        "values": values
    })


@app.route('/api/predict', methods=['GET'])
def get_prediction():
    """
    ML Predictive Analysis Endpoint
    Forecasts a target year using historical data and linear regression.
    """
    data = get_data()
    if not data:
         return jsonify({"error": "Dataset not found"}), 404
         
    df, _ = data
    state = request.args.get('state', 'all')
    try:
        target_year = int(request.args.get('target_year', df['year'].max() + 1))
    except ValueError:
        return jsonify({"error": "Invalid target_year format"}), 400

    if state.lower() != 'all':
         df = df[df['state_name'].str.lower() == state.lower()]

    yearly_totals = df.groupby('year')['total_crimes'].sum().reset_index()
    years = yearly_totals["year"].values
    totals = yearly_totals["total_crimes"].values

    prediction = 0
    method = "Weighted Moving Average"

    if has_sklearn and len(years) >= 3:
        model = LinearRegression()
        model.fit(years.reshape(-1, 1), totals)
        predicted_vals = model.predict(np.array([[target_year]]))
        prediction = int(max(0, predicted_vals[0]))
        method = "Linear Regression"
    else:
        # Fallback
        if len(totals) >= 3:
            # Simple weighted average prioritizing recent years
            weights = np.array([0.2, 0.3, 0.5])
            prediction = int(np.dot(totals[-3:], weights))
        elif len(totals) > 0:
            prediction = int(np.mean(totals))

    return jsonify({
        "target_year": target_year,
        "predicted_crimes": prediction,
        "model_used": method,
        "historical_context": {
            "last_year": int(years[-1]) if len(years)>0 else None,
            "last_year_crimes": int(totals[-1]) if len(totals)>0 else 0
        }
    })


@app.route('/api/dataset', methods=['GET'])
def get_dataset():
    """
    Returns the complete preprocessed dataset so the frontend 
    can maintain all its interactive charts, maps, and tables 
    without relying on fake mock generation.
    """
    data = get_data()
    if not data:
         return jsonify([]), 404
         
    df, _ = data
    
    # Map backend columns names to what frontend expects 
    # The frontend expects: State, District, Year, Total and specific CrimeTypes
    # For now, we return it as is but format names to Title Case if needed.
    # The backend excel columns are assumed to be state_name, district_name, year, total_crimes
    
    # We will rename state_name -> State, district_name -> District, year -> Year, total_crimes -> Total
    export_df = df.copy()
    
    rename_map = {
        'state_name': 'State',
        'district_name': 'District',
        'year': 'Year',
        'total_crimes': 'Total'
    }
    
    # Title-case all crime type columns so they match the frontend's Expectation
    for col in export_df.columns:
        if col not in rename_map:
            # e.g 'murder' -> 'Murder', 'cyber_crime' -> 'Cyber Crime'
            new_col = col.replace('_', ' ').title()
            rename_map[col] = new_col
            
    export_df.rename(columns=rename_map, inplace=True)
    
    # Replace NaN with 0
    export_df.fillna(0, inplace=True)
    
    records = export_df.to_dict(orient='records')
    return jsonify(records)


if __name__ == '__main__':
    # Run the Flask app on port 5000
    print("Starting CrimeScope API Backend on port 5000...")
    app.run(debug=True, port=5000)
