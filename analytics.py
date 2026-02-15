import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor


def predict_crime_trend(data, target):
    """Predict crime trends using Random Forest"""
    X = data.drop(target, axis=1)
    y = data[target]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    return model.predict(X_test)


def get_crime_statistics(data):
    """Calculate crime statistics from filtered data"""
    numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
    
    exclude_cols = ['year']
    crime_cols = [col for col in numeric_cols if col not in exclude_cols]
    
    total_crimes = int(data[crime_cols].sum().sum())
    
    yearly_crimes = data.groupby('year')[crime_cols].sum().sum(axis=1)
    peak_year = int(yearly_crimes.idxmax()) if len(yearly_crimes) > 0 else int(data['year'].max())
    avg_crimes_per_year = int(yearly_crimes.mean()) if len(yearly_crimes) > 0 else 0
    std_deviation = int(yearly_crimes.std()) if len(yearly_crimes) > 0 else 0
    
    return {
        'total_crimes': total_crimes,
        'peak_year': peak_year,
        'avg_crimes_per_year': avg_crimes_per_year,
        'std_deviation': std_deviation,
        'crime_columns': crime_cols
    }


def get_crime_by_type(data, crime_type):
    """Filter data by specific crime type"""
    if crime_type in data.columns:
        return data[['state_name', 'district_name', 'year', crime_type]]
    return data
