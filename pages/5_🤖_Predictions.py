"""
Predictions & Forecasting Page - Machine Learning Based Crime Forecasting
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Import custom modules
from data_loader import load_data, validate_data, filter_data
from prediction import (
    train_prediction_models,
    predict_future,
    plot_prediction_comparison,
    plot_future_predictions,
    plot_crime_type_forecast,
    display_model_metrics
)
from utils.export_utils import export_to_csv
from utils import format_number, apply_custom_styling

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="Predictions & Forecasting | CrimeScope",
    page_icon="🤖",
    layout="wide"
)

apply_custom_styling()

# ==================================================
# LOAD DATA
# ==================================================
df, crime_columns = load_data()

if not validate_data(df):
    st.error("❌ Failed to load or validate data.")
    st.stop()

# ==================================================
# HEADER
# ==================================================
st.title("🤖 Crime Predictions & Forecasting")
st.markdown("""
Advanced machine learning models to forecast future crime trends. Three models are trained and compared:
**Linear Regression**, **Random Forest**, and **Gradient Boosting**.
""")
st.divider()

# ==================================================
# SIDEBAR FILTERS
# ==================================================
with st.sidebar:
    st.title("🔍 Prediction Settings")
    
    # State Selection
    state = st.selectbox(
        "📍 Select State",
        sorted(df["state_name"].unique()),
        help="Choose a state for prediction"
    )
    
    # District Selection
    districts = sorted(df[df["state_name"] == state]["district_name"].unique())
    district = st.selectbox(
        "🏘️ Select District",
        ["All Districts"] + list(districts),
        help="Choose a specific district or view all"
    )
    
    # Year Range
    year_range = st.slider(
        "📅 Training Data Year Range",
        int(df["year"].min()),
        int(df["year"].max()),
        (int(df["year"].min()), int(df["year"].max())),
        help="Select year range for model training"
    )
    
    st.divider()
    
    # Crime Types
    st.subheader("🚨 Crime Types")
    all_crimes = st.checkbox("Use All Crime Types", value=True)
    
    if all_crimes:
        crime_types = list(crime_columns)
    else:
        top_crimes = df[crime_columns].sum().nlargest(15).index.tolist()
        crime_types = st.multiselect(
            "Select crime types",
            top_crimes,
            default=top_crimes[:5]
        )
    
    if not crime_types:
        crime_types = [crime_columns[0]]
    
    st.divider()
    
    # Model Settings
    st.subheader("⚙️ Model Settings")
    
    test_size = st.slider(
        "Test Set Size",
        0.1,
        0.4,
        0.2,
        0.05,
        help="Proportion of data used for testing"
    )
    
    forecast_horizon = st.slider(
        "Forecast Horizon (years)",
        1,
        10,
        5,
        help="Number of years to predict into the future"
    )

# ==================================================
# FILTER DATA
# ==================================================
filtered_df = filter_data(df, state, district, year_range, crime_types)

# ==================================================
# INFO SECTION
# ==================================================
st.info(f"""
**Analysis Configuration:**
- **State:** {state}
- **District:** {district}
- **Training Period:** {year_range[0]} - {year_range[1]}
- **Crime Types:** {len(crime_types)} types selected
- **Records:** {format_number(len(filtered_df))} data points
""")

st.divider()

# ==================================================
# MODEL TRAINING
# ==================================================
st.subheader("📊 Model Training & Performance")

with st.spinner("🔄 Training machine learning models... This may take a moment."):
    results = train_prediction_models(filtered_df, crime_types, test_size=test_size)

if results:
    # ==================================================
    # MODEL PERFORMANCE
    # ==================================================
    tab1, tab2, tab3 = st.tabs([
        "📊 Model Comparison",
        "🔮 Future Forecast",
        "📈 Crime Type Forecasts"
    ])
    
    with tab1:
        st.markdown("### Model Performance Comparison")
        st.caption("Comparison of actual vs predicted values on test set")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = plot_prediction_comparison(
                results,
                results['X_test'],
                results['y_test'],
                results['yearly_data']
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### Performance Metrics")
            styled_metrics = display_model_metrics(results)
            if styled_metrics is not None:
                st.dataframe(styled_metrics, use_container_width=True)
            
            st.markdown("""
            **Metrics Explained:**
            - **MAE**: Mean Absolute Error (lower is better)
            - **RMSE**: Root Mean Squared Error (lower is better)
            - **R²**: Coefficient of determination (higher is better, max 1.0)
            
            🟢 *Green highlight indicates best performing model*
            """)
            
            # Best model - handle different metric key names
            try:
                # Try 'rmse' first (lowercase), then 'RMSE' (uppercase)
                best_model = min(results['metrics'].items(), key=lambda x: x[1].get('rmse', x[1].get('RMSE', float('inf'))))
            except (KeyError, TypeError, ValueError):
                # Fallback: just take the first model
                best_model = list(results['metrics'].items())[0] if results['metrics'] else (None, {'rmse': 0, 'RMSE': 0, 'r2': 0, 'R²': 0})
            
            if best_model[0]:
                st.success(f"""
                **🏆 Best Model:** {best_model[0]}
                - RMSE: {best_model[1].get('rmse', best_model[1].get('RMSE', 'N/A'))}
                - R² Score: {best_model[1].get('r2', best_model[1].get('R²', 'N/A'))}
                """)
        
        # Model details
        st.divider()
        st.markdown("### Model Training Details")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Training Data Points",
                len(results['X_train'])
            )
        
        with col2:
            st.metric(
                "Test Data Points",
                len(results['X_test'])
            )
        
        with col3:
            st.metric(
                "Total Years Analyzed",
                len(results['yearly_data'])
            )
    
    with tab2:
        st.markdown("### Future Crime Forecast")
        st.caption(f"Predictions for the next {forecast_horizon} years")
        
        # Generate predictions from all models
        predictions_dict = {}
        for model_name, model in results['models'].items():
            forecast = predict_future(
                model,
                results['yearly_data'],
                years_ahead=forecast_horizon,
                crime_types=crime_types
            )
            predictions_dict[model_name] = forecast['predictions']
        
        # Get future years
        current_year = int(results['yearly_data']['year'].max())
        future_years = list(range(current_year + 1, current_year + forecast_horizon + 1))
        
        # Plot future predictions
        fig = plot_future_predictions(results['yearly_data'], future_years, predictions_dict)
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Detailed forecast table
        st.markdown("### Detailed Forecast Summary")
        
        forecast_data = {'Year': future_years}
        for model_name, predictions in predictions_dict.items():
            forecast_data[model_name] = [int(p) for p in predictions]
        
        # Calculate ensemble average
        all_predictions = np.array([predictions_dict[m] for m in predictions_dict.keys()])
        forecast_data['Ensemble Average'] = [int(p) for p in all_predictions.mean(axis=0)]
        
        forecast_df = pd.DataFrame(forecast_data)
        
        # Style the dataframe
        styled_forecast = forecast_df.style.background_gradient(
            subset=[col for col in forecast_df.columns if col != 'Year'],
            cmap='YlOrRd'
        ).format({col: "{:,.0f}" for col in forecast_df.columns if col != 'Year'})
        
        st.dataframe(styled_forecast, use_container_width=True)
        
        # Key insights
        st.divider()
        st.markdown("### 💡 Key Insights & Predictions")
        
        col1, col2, col3 = st.columns(3)
        
        # Current year crime count
        current_crimes = int(results['yearly_data']['total_crimes'].iloc[-1])
        
        # Predicted next year (ensemble average)
        next_year_pred = int(all_predictions.mean(axis=0)[0])
        
        # Calculate trend
        trend_change = next_year_pred - current_crimes
        trend_pct = (trend_change / current_crimes * 100) if current_crimes > 0 else 0
        trend_direction = "📈 Increasing" if trend_change > 0 else "📉 Decreasing"
        
        with col1:
            st.metric(
                label=f"Current ({current_year})",
                value=format_number(current_crimes)
            )
        
        with col2:
            st.metric(
                label=f"Predicted ({current_year + 1})",
                value=format_number(next_year_pred),
                delta=f"{trend_pct:+.1f}%"
            )
        
        with col3:
            st.metric(
                label="Trend Direction",
                value=trend_direction,
                delta=f"{abs(trend_change):,.0f} crimes"
            )
        
        # Forecast summary
        st.markdown("#### 📊 Forecast Summary")
        
        avg_future_crimes = int(all_predictions.mean())
        
        if forecast_horizon >= 5:
            five_year_pred = int(all_predictions.mean(axis=0)[4])
            five_year_change = five_year_pred - current_crimes
            five_year_pct = (five_year_change / current_crimes * 100) if current_crimes > 0 else 0
            
            st.markdown(f"""
            - **Short-term Outlook (1 year):** Crimes expected to **{trend_direction.split()[1].lower()}** by **{abs(trend_pct):.1f}%**
            - **Long-term Outlook (5 years):** Projected **{five_year_pct:+.1f}%** change from current levels
            - **Average Forecast:** {format_number(avg_future_crimes)} crimes per year over the next {forecast_horizon} years
            - **Confidence:** Models trained on {len(results['yearly_data'])} years of historical data
            - **Model Agreement:** {len(predictions_dict)} models provide ensemble prediction
            """)
        else:
            st.markdown(f"""
            - **Outlook ({forecast_horizon} year{'s' if forecast_horizon > 1 else ''}):** Crimes expected to **{trend_direction.split()[1].lower()}** by **{abs(trend_pct):.1f}%**
            - **Average Forecast:** {format_number(avg_future_crimes)} crimes per year
            - **Confidence:** Models trained on {len(results['yearly_data'])} years of historical data
            - **Model Agreement:** {len(predictions_dict)} models provide ensemble prediction
            """)
        
        # Export forecast
        st.divider()
        st.markdown("### 📥 Download Forecast Data")
        
        export_to_csv(
            forecast_df,
            filename=f"crime_forecast_{state.replace(' ', '_')}_{current_year}_{forecast_horizon}years.csv"
        )
    
    with tab3:
        st.markdown("### Individual Crime Type Forecasts")
        st.caption("Separate predictions for each crime category")
        
        forecast_years = st.slider(
            "Forecast horizon for crime types",
            1,
            5,
            3,
            help="Choose forecast period for individual crime types"
        )
        
        fig = plot_crime_type_forecast(filtered_df, crime_types, years_ahead=forecast_years)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
            
            st.info("""
            💡 **Note:** Individual crime type forecasts use simple linear regression for each crime category.
            These predictions show specific trends for each crime type separately.
            """)
        else:
            st.warning("⚠️ Insufficient data for individual crime type forecasting.")

else:
    st.error("""
    ⚠️ **Unable to generate predictions**
    
    **Possible reasons:**
    - Insufficient historical data (need at least 5 years)
    - Selected filters resulted in too few data points
    - Try selecting a broader date range or different location
    
    **Suggestions:**
    - Select "All Districts" for more data points
    - Expand the year range
    - Try a different state with more historical data
    """)

# ==================================================
# METHODOLOGY
# ==================================================
st.divider()
st.subheader("📚 Methodology")

with st.expander("Learn about the prediction models", expanded=False):
    st.markdown("""
    ### Machine Learning Models Used
    
    #### 1. Linear Regression
    - **Type:** Simple statistical model
    - **Best for:** Linear trends and basic forecasting
    - **Advantages:** Fast, interpretable, works well with clear trends
    
    #### 2. Random Forest Regressor
    - **Type:** Ensemble learning method
    - **Best for:** Non-linear patterns and complex relationships
    - **Advantages:** Robust to outliers, handles non-linearity
    
    #### 3. Gradient Boosting Regressor
    - **Type:** Advanced ensemble method
    - **Best for:** High accuracy predictions
    - **Advantages:** Often provides best performance, adapts to patterns
    
    ### Features Used
    - Normalized year values
    - Lag features (previous year values)
    - Rolling mean trends
    - Historical patterns
    
    ### Model Selection
    The models are compared using:
    - **RMSE (Root Mean Squared Error):** Overall prediction accuracy
    - **MAE (Mean Absolute Error):** Average prediction error
    - **R² Score:** Proportion of variance explained (0-1, higher is better)
    
    ### Ensemble Prediction
    The final forecast uses the **average** of all three models to provide
    a more robust and reliable prediction.
    """)

# ==================================================
# FOOTER
# ==================================================
st.divider()
st.caption(f"Predictions & Forecasting | {state} | {district} | {year_range[0]}-{year_range[1]}")
