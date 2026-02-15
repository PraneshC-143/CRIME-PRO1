import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
import warnings
warnings.filterwarnings('ignore')


def prepare_time_series_data(data):
    # Your implementation here
    pass


def create_features(data):
    # Your implementation here
    pass


def train_prediction_models(X_train, y_train):
    models = {
        'Linear Regression': LinearRegression(),
        'Random Forest': RandomForestRegressor(),
        'Gradient Boosting': GradientBoostingRegressor()
    }
    results = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        results[name] = model
    return results


def predict_future(model, X_test):
    return model.predict(X_test)


def plot_prediction_comparison(y_true, y_pred):
    df = pd.DataFrame({'True': y_true, 'Predicted': y_pred})
    fig = px.line(df, title='Prediction Comparison')
    st.plotly_chart(fig)


def plot_future_predictions(future_dates, predictions):
    df = pd.DataFrame({'Date': future_dates, 'Predicted': predictions})
    fig = px.line(df, x='Date', y='Predicted', title='Future Predictions')
    st.plotly_chart(fig)


def plot_crime_type_forecast(crime_data):
    # Your implementation here
    pass


def display_model_metrics(metrics):
    for model_name, metric in metrics.items():
        st.write(f'{model_name}: {metric}')