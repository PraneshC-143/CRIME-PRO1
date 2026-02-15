"""
Machine Learning-based Crime Prediction Module
Complete implementation with multiple models, visualizations, and metrics
"""

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')


def prepare_time_series_data(data, crime_types):
    """
    Aggregate crime data by year for time series analysis
    
    Args:
        data: DataFrame with crime data
        crime_types: List of crime type columns to aggregate
    
    Returns:
        DataFrame: Aggregated yearly data with crime types as columns
    """
    if data.empty or not crime_types:
        return pd.DataFrame()
    
    # Group by year and sum crime types
    yearly_data = data.groupby('year')[crime_types].sum().reset_index()
    
    # Sort by year
    yearly_data = yearly_data.sort_values('year').reset_index(drop=True)
    
    return yearly_data


def create_features(df, target_col):
    """
    Create time-based and lag features for ML models
    
    Args:
        df: DataFrame with yearly crime data
        target_col: Name of the target column
    
    Returns:
        tuple: (X, y) features and target
    """
    if df.empty or len(df) < 3:
        return None, None
    
    df = df.copy()
    
    # Create lag features
    df['lag_1'] = df[target_col].shift(1)
    df['lag_2'] = df[target_col].shift(2)
    
    # Create rolling mean feature
    df['rolling_mean_3'] = df[target_col].rolling(window=3, min_periods=1).mean()
    
    # Normalize year feature
    df['year_normalized'] = (df['year'] - df['year'].min()) / (df['year'].max() - df['year'].min() + 1e-10)
    
    # Drop rows with NaN values (due to lag)
    df = df.dropna()
    
    if df.empty:
        return None, None
    
    # Select features
    feature_cols = ['year_normalized', 'lag_1', 'lag_2', 'rolling_mean_3']
    X = df[feature_cols]
    y = df[target_col]
    
    return X, y


def train_prediction_models(data, crime_types, test_size=0.2):
    """
    Train multiple ML models for crime prediction
    
    Args:
        data: DataFrame with crime data
        crime_types: List of crime types
        test_size: Proportion of data for testing
    
    Returns:
        dict: Results containing models, metrics, and test data
    """
    # Prepare time series data
    yearly_data = prepare_time_series_data(data, crime_types)
    
    if yearly_data.empty or len(yearly_data) < 5:
        st.error("⚠️ Insufficient data for training. Need at least 5 years of data.")
        return None
    
    # Calculate total crimes per year
    yearly_data['total_crimes'] = yearly_data[crime_types].sum(axis=1)
    
    # Create features
    X, y = create_features(yearly_data, 'total_crimes')
    
    if X is None or y is None or len(X) < 3:
        st.error("⚠️ Insufficient data after feature engineering. Need at least 3 valid records.")
        return None
    
    # Split data (shuffle=False for time series)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, shuffle=False, random_state=42
    )
    
    # Initialize models
    models = {
        'Linear Regression': LinearRegression(),
        'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42, max_depth=5),
        'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, random_state=42, max_depth=3, learning_rate=0.1)
    }
    
    results = {
        'models': {},
        'metrics': {},
        'X_train': X_train,
        'X_test': X_test,
        'y_train': y_train,
        'y_test': y_test,
        'yearly_data': yearly_data,
        'crime_types': crime_types
    }
    
    # Train models and calculate metrics
    for name, model in models.items():
        try:
            # Train model
            model.fit(X_train, y_train)
            
            # Make predictions
            y_pred = model.predict(X_test)
            
            # Ensure non-negative predictions
            y_pred = np.maximum(y_pred, 0)
            
            # Calculate metrics
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            r2 = r2_score(y_test, y_pred)
            
            # Store results
            results['models'][name] = model
            results['metrics'][name] = {
                'MAE': mae,
                'RMSE': rmse,
                'R²': r2,
                'predictions': y_pred
            }
        except Exception as e:
            st.warning(f"Error training {name}: {str(e)}")
            continue
    
    return results


def predict_future(model, last_data, years_ahead=5, crime_types=None):
    """
    Forecast future years using trained model with lag features
    
    Args:
        model: Trained ML model
        last_data: DataFrame with recent historical data
        years_ahead: Number of years to forecast
        crime_types: List of crime types
    
    Returns:
        dict: Dictionary with years and predictions
    """
    if last_data.empty or len(last_data) < 3:
        return {'years': [], 'predictions': []}
    
    # Get last year and prepare for forecasting
    last_year = int(last_data['year'].max())
    
    # Calculate total crimes for recent years
    if crime_types:
        last_data['total_crimes'] = last_data[crime_types].sum(axis=1)
    
    last_data = last_data.sort_values('year').tail(3)  # Use last 3 years
    
    # Initialize prediction list with recent data
    recent_values = last_data['total_crimes'].values.tolist()
    future_years = []
    future_predictions = []
    
    # Year normalization parameters
    year_min = last_data['year'].min()
    year_max = last_data['year'].max()
    year_range = year_max - year_min + 1e-10
    
    for i in range(years_ahead):
        year = last_year + i + 1
        
        # Create features for prediction
        if len(recent_values) >= 2:
            lag_1 = recent_values[-1]
            lag_2 = recent_values[-2]
        else:
            lag_1 = recent_values[-1] if len(recent_values) >= 1 else 0
            lag_2 = lag_1
        
        rolling_mean = np.mean(recent_values[-3:]) if len(recent_values) >= 3 else np.mean(recent_values)
        year_norm = (year - year_min) / year_range
        
        # Create feature vector
        X_pred = pd.DataFrame({
            'year_normalized': [year_norm],
            'lag_1': [lag_1],
            'lag_2': [lag_2],
            'rolling_mean_3': [rolling_mean]
        })
        
        # Make prediction
        pred = model.predict(X_pred)[0]
        pred = max(0, pred)  # Ensure non-negative
        
        # Store results
        future_years.append(year)
        future_predictions.append(pred)
        
        # Update recent values
        recent_values.append(pred)
    
    return {
        'years': future_years,
        'predictions': future_predictions
    }


def plot_prediction_comparison(results, X_test, y_test, yearly_data):
    """
    Compare actual vs predicted for all models
    
    Args:
        results: Dictionary with model results
        X_test: Test features
        y_test: Test targets
        yearly_data: Historical yearly data
    
    Returns:
        plotly figure
    """
    fig = go.Figure()
    
    # Get test years (approximate based on position)
    all_years = yearly_data['year'].values
    test_size = len(y_test)
    test_years = all_years[-test_size:] if test_size <= len(all_years) else all_years
    
    # Plot actual values
    fig.add_trace(go.Scatter(
        x=test_years,
        y=y_test.values,
        mode='lines+markers',
        name='Actual',
        line=dict(color='black', width=3),
        marker=dict(size=10)
    ))
    
    # Plot predictions for each model
    colors = {'Linear Regression': 'blue', 'Random Forest': 'green', 'Gradient Boosting': 'red'}
    
    for model_name, metrics in results['metrics'].items():
        fig.add_trace(go.Scatter(
            x=test_years,
            y=metrics['predictions'],
            mode='lines+markers',
            name=model_name,
            line=dict(color=colors.get(model_name, 'gray'), width=2, dash='dash'),
            marker=dict(size=8)
        ))
    
    fig.update_layout(
        title='Model Performance Comparison: Actual vs Predicted',
        xaxis_title='Year',
        yaxis_title='Total Crimes',
        hovermode='x unified',
        template='plotly_white',
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig


def plot_future_predictions(yearly_data, future_years, predictions_dict):
    """
    Show historical data + future forecasts
    
    Args:
        yearly_data: DataFrame with historical data
        future_years: List of future years
        predictions_dict: Dictionary with model predictions
    
    Returns:
        plotly figure
    """
    fig = go.Figure()
    
    # Plot historical data
    historical_years = yearly_data['year'].values
    historical_crimes = yearly_data['total_crimes'].values
    
    fig.add_trace(go.Scatter(
        x=historical_years,
        y=historical_crimes,
        mode='lines+markers',
        name='Historical',
        line=dict(color='black', width=3),
        marker=dict(size=10)
    ))
    
    # Plot future predictions for each model
    colors = {'Linear Regression': 'blue', 'Random Forest': 'green', 'Gradient Boosting': 'red'}
    
    for model_name, predictions in predictions_dict.items():
        fig.add_trace(go.Scatter(
            x=future_years,
            y=predictions,
            mode='lines+markers',
            name=f'{model_name} (Forecast)',
            line=dict(color=colors.get(model_name, 'gray'), width=2, dash='dot'),
            marker=dict(size=8, symbol='diamond')
        ))
    
    # Add vertical line to separate historical and forecast
    if len(historical_years) > 0:
        last_year = historical_years[-1]
        fig.add_vline(
            x=last_year,
            line_dash="dash",
            line_color="gray",
            annotation_text="Forecast Start",
            annotation_position="top"
        )
    
    fig.update_layout(
        title='Crime Forecast: Historical Data + Future Predictions',
        xaxis_title='Year',
        yaxis_title='Total Crimes',
        hovermode='x unified',
        template='plotly_white',
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig


def plot_crime_type_forecast(data, crime_types, years_ahead=3):
    """
    Individual crime type forecasts
    
    Args:
        data: DataFrame with crime data
        crime_types: List of crime types
        years_ahead: Number of years to forecast
    
    Returns:
        plotly figure
    """
    yearly_data = prepare_time_series_data(data, crime_types)
    
    if yearly_data.empty or len(yearly_data) < 3:
        return None
    
    fig = go.Figure()
    
    # For each crime type, create simple trend forecast
    last_year = int(yearly_data['year'].max())
    future_years = list(range(last_year + 1, last_year + years_ahead + 1))
    
    for crime_type in crime_types[:5]:  # Limit to top 5 for clarity
        # Get historical data
        historical_values = yearly_data[crime_type].values
        historical_years = yearly_data['year'].values
        
        # Plot historical
        fig.add_trace(go.Scatter(
            x=historical_years,
            y=historical_values,
            mode='lines+markers',
            name=f'{crime_type}',
            line=dict(width=2)
        ))
        
        # Simple linear trend for forecast
        if len(historical_values) >= 2:
            # Calculate trend
            x = np.arange(len(historical_values))
            z = np.polyfit(x, historical_values, 1)
            p = np.poly1d(z)
            
            # Forecast
            future_x = np.arange(len(historical_values), len(historical_values) + years_ahead)
            future_pred = p(future_x)
            future_pred = np.maximum(future_pred, 0)  # Non-negative
            
            # Plot forecast
            fig.add_trace(go.Scatter(
                x=future_years,
                y=future_pred,
                mode='lines+markers',
                name=f'{crime_type} (Forecast)',
                line=dict(width=2, dash='dot'),
                marker=dict(symbol='diamond'),
                showlegend=False
            ))
    
    if len(yearly_data) > 0:
        last_year = yearly_data['year'].max()
        fig.add_vline(
            x=last_year,
            line_dash="dash",
            line_color="gray",
            annotation_text="Forecast",
            annotation_position="top"
        )
    
    fig.update_layout(
        title=f'Individual Crime Type Forecasts ({years_ahead} Years)',
        xaxis_title='Year',
        yaxis_title='Crime Count',
        hovermode='x unified',
        template='plotly_white',
        height=500
    )
    
    return fig


def display_model_metrics(results):
    """
    Show comparison table with highlighting for best model
    
    Args:
        results: Dictionary with model results
    
    Returns:
        Styled DataFrame or None if error occurs
    """
    try:
        # Validate input
        if not results or 'metrics' not in results:
            st.warning("No metrics available to display.")
            return None
        
        if not results['metrics']:
            st.warning("Metrics dictionary is empty.")
            return None
        
        # Create metrics dataframe
        metrics_data = []
        for model_name, metrics in results['metrics'].items():
            try:
                metrics_data.append({
                    'Model': model_name,
                    'MAE': f"{metrics['MAE']:.2f}",
                    'RMSE': f"{metrics['RMSE']:.2f}",
                    'R² Score': f"{metrics['R²']:.4f}"
                })
            except (KeyError, TypeError, ValueError) as e:
                st.warning(f"Error processing metrics for {model_name}: {str(e)}")
                continue
        
        if not metrics_data:
            st.warning("No valid metrics data to display.")
            return None
        
        df = pd.DataFrame(metrics_data)
        
        # Validate required columns exist
        required_columns = ['MAE', 'RMSE', 'R² Score']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"Missing required columns: {missing_columns}")
            return None
        
        # Convert numeric columns for styling with error handling
        df_numeric = df.copy()
        
        # Clean and convert each numeric column
        for col in required_columns:
            try:
                # Strip whitespace from string values and convert to numeric
                # Use errors='coerce' to handle conversion issues gracefully
                df_numeric[col] = df_numeric[col].str.strip()
                df_numeric[col] = pd.to_numeric(df_numeric[col], errors='coerce')
                
                # Check if conversion resulted in NaN values
                nan_count = df_numeric[col].isna().sum()
                if nan_count > 0:
                    st.warning(f"{nan_count} value(s) in '{col}' could not be converted to numeric.")
                    
            except AttributeError:
                # If str.strip() fails, values might not be strings
                # Try direct conversion
                try:
                    df_numeric[col] = pd.to_numeric(df_numeric[col], errors='coerce')
                except Exception as e:
                    st.error(f"Error converting column '{col}' to numeric: {str(e)}")
                    return None
            except Exception as e:
                st.error(f"Error converting column '{col}' to numeric: {str(e)}")
                return None
        
        # Verify we have valid numeric data
        # Check if all values in any column are NaN or if more than half are NaN
        for col in required_columns:
            col_len = len(df_numeric[col])
            if df_numeric[col].isna().all():
                st.error(f"Could not convert any values in '{col}' to numeric format.")
                return None
            nan_ratio = df_numeric[col].isna().sum() / col_len
            if nan_ratio > 0.5:
                st.error(f"More than 50% of values in '{col}' could not be converted to numeric format.")
                return None
        
        # Style: Lower MAE/RMSE is better (green), Higher R² is better (green)
        def highlight_best(s):
            try:
                if s.name == 'MAE' or s.name == 'RMSE':
                    # Filter out NaN values for comparison
                    valid_values = s.dropna()
                    if len(valid_values) == 0:
                        return ['' for _ in s]
                    is_min = s == valid_values.min()
                    return ['background-color: lightgreen' if v else '' for v in is_min]
                elif s.name == 'R² Score':
                    # Filter out NaN values for comparison
                    valid_values = s.dropna()
                    if len(valid_values) == 0:
                        return ['' for _ in s]
                    is_max = s == valid_values.max()
                    return ['background-color: lightgreen' if v else '' for v in is_max]
                return ['' for _ in s]
            except Exception:
                return ['' for _ in s]
        
        # Apply styling with error handling
        try:
            styled_df = df_numeric.style.apply(highlight_best, subset=required_columns)
            return styled_df
        except Exception as e:
            st.warning(f"Could not apply styling to metrics table: {str(e)}")
            # Return unstyled dataframe as fallback
            return df_numeric
            
    except Exception as e:
        st.error(f"Unexpected error in display_model_metrics: {str(e)}")
        return None
