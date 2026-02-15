"""
CrimeScope: Interactive IPC Crime Intelligence Dashboard
Main Streamlit Application
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime

# Import custom modules
from config import PAGE_TITLE, PAGE_LAYOUT, PAGE_ICON
from data_loader import load_data, validate_data, filter_data
from visualizations import (
    plot_top_districts, plot_crime_trend, plot_distribution,
    plot_correlation_heatmap, plot_heatmap_by_district, plot_crime_hotspots
)
from analytics import get_crime_statistics
from utils import (
    apply_custom_styling, format_number, get_download_button,
    display_kpi_card, display_warning_message, display_info_message
)
from prediction import (
    train_prediction_models, predict_future, plot_prediction_comparison,
    plot_future_predictions, plot_crime_type_forecast, display_model_metrics
)


# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=PAGE_LAYOUT,
    initial_sidebar_state="expanded"
)

# Apply custom styling
apply_custom_styling()


# ==================================================
# LOAD DATA
# ==================================================
df, crime_columns = load_data()

if not validate_data(df):
    st.error("❌ Failed to load or validate data. Please check the data file.")
    st.stop()


# ==================================================
# SIDEBAR CONFIGURATION
# ==================================================
with st.sidebar:
    st.title("🔍 CrimeScope")
    st.caption("IPC Crime Intelligence System")
    st.divider()
    
    # State Selection
    state = st.selectbox(
        "📍 Select State",
        sorted(df["state_name"].unique()),
        help="Choose a state to analyze"
    )
    
    # District Selection
    districts = sorted(df[df["state_name"] == state]["district_name"].unique())
    district = st.selectbox(
        "🏘️ Select District",
        ["All Districts"] + list(districts),
        help="Choose a specific district or view all"
    )
    
    # Year Range Selection
    year_range = st.slider(
        "📅 Select Year Range",
        int(df["year"].min()),
        int(df["year"].max()),
        (int(df["year"].min()), int(df["year"].max())),
        help="Filter data by year range"
    )
    
    # Crime Types Selection
    st.divider()
    st.subheader("🚨 Crime Types")
    all_crimes = st.checkbox("Select All", value=True, help="Toggle all crime types")
    
    if all_crimes:
        crime_types = list(crime_columns)
    else:
        crime_types = st.multiselect(
            "Choose crime types",
            crime_columns.tolist(),
            default=list(crime_columns[:3])
        )
    
    if not crime_types:
        display_warning_message("Please select at least one crime type")
        crime_types = list(crime_columns[:1])


# ==================================================
# FILTER DATA
# ==================================================
filtered_df = filter_data(df, state, district, year_range, crime_types)


# ==================================================
# HEADER & CONTEXT
# ==================================================
st.markdown("# 📊 IPC Crime Analysis Dashboard")

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown(f"""
    **State:** `{state}` | **District:** `{district}` | **Years:** `{year_range[0]} – {year_range[1]}`
    """)
with col2:
    get_download_button(filtered_df, filename=f"crime_analysis_{state}")


# ==================================================
# KPIs (CONTEXT-AWARE)
# ==================================================
st.subheader("📈 Key Performance Indicators")

stats = get_crime_statistics(filtered_df)

col1, col2, col3, col4 = st.columns(4)

with col1:
    display_kpi_card("Total Crimes", stats['total_crimes'], "🔢")

with col2:
    display_kpi_card("Peak Year", stats['peak_year'], "📍")

with col3:
    display_kpi_card("Avg/Year", stats['avg_crimes_per_year'], "📊")

with col4:
    display_kpi_card("Std Dev", stats['std_deviation'], "📉")


# ==================================================
# VISUALIZATIONS
# ==================================================
st.divider()
st.subheader("📊 Crime Analytics")

# Tabs for different visualizations
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏙️ District Analysis",
    "📈 Trends",
    "🔥 Heatmaps",
    "🌍 Geographic",
    "🔮 Predictions"
])

with tab1:
    st.markdown("### Top Districts by Crime Count")
    fig = plot_top_districts(filtered_df, top_n=10)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### Crime Type Distribution")
    fig = plot_distribution(filtered_df, crime_types)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown("### Crime Trend Over Years")
    fig = plot_crime_trend(filtered_df, crime_types)
    st.plotly_chart(fig, use_container_width=True)
    
    # Yearly comparison table
    st.markdown("### Yearly Statistics")
    yearly_stats = filtered_df.groupby('year')[crime_types].sum()
    yearly_stats['Total'] = yearly_stats.sum(axis=1)
    st.dataframe(yearly_stats.style.highlight_max(axis=0, color='#ffcccc'))

with tab3:
    st.markdown("### Crime Type Correlation")
    if len(crime_types) >= 2:
        fig = plot_correlation_heatmap(filtered_df, crime_types)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    else:
        display_info_message("Select at least 2 crime types to view correlation")
    
    st.markdown("### District-wise Crime Heatmap")
    fig = plot_heatmap_by_district(filtered_df, crime_types)
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.markdown("### Geographic Crime Distribution")
    fig = plot_crime_hotspots(filtered_df, crime_types)
    st.plotly_chart(fig, use_container_width=True)
    
    # Top districts table
    st.markdown("### Top 10 Districts Summary")
    top_districts_data = filtered_df.groupby('district_name')[crime_types].sum()
    top_districts_data['Total'] = top_districts_data.sum(axis=1)
    top_districts_data = top_districts_data.sort_values('Total', ascending=False).head(10)
    st.dataframe(top_districts_data.style.background_gradient(cmap='Reds'))

with tab5:
    st.markdown("### 🔮 Crime Prediction & Forecasting")
    st.markdown("""
    This section uses machine learning to forecast future crime trends based on historical data.
    Three models are trained and compared: **Linear Regression**, **Random Forest**, and **Gradient Boosting**.
    """)
    
    # Model Training Section
    st.divider()
    st.subheader("📊 Model Training & Performance")
    
    with st.spinner("Training machine learning models... This may take a moment."):
        results = train_prediction_models(filtered_df, crime_types, test_size=0.2)
    
    if results:
        # Model Performance Comparison
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### Model Performance Comparison")
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
            - **R²**: Coefficient of determination (higher is better)
            
            🟢 *Green highlight indicates best performing model*
            """)
        
        # Future Forecast Section
        st.divider()
        st.subheader("🔭 Future Crime Forecast")
        
        years_ahead = st.slider(
            "Select forecast horizon (years ahead)",
            min_value=1,
            max_value=10,
            value=5,
            help="Choose how many years into the future to predict"
        )
        
        # Generate predictions from all models
        predictions_dict = {}
        for model_name, model in results['models'].items():
            forecast = predict_future(
                model, 
                results['yearly_data'], 
                years_ahead=years_ahead,
                crime_types=crime_types
            )
            predictions_dict[model_name] = forecast['predictions']
        
        # Get future years
        future_years = list(range(
            int(results['yearly_data']['year'].max()) + 1,
            int(results['yearly_data']['year'].max()) + years_ahead + 1
        ))
        
        # Plot future predictions
        st.markdown("#### Historical Data & Future Predictions")
        fig = plot_future_predictions(results['yearly_data'], future_years, predictions_dict)
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed Forecast Table
        st.markdown("#### Detailed Forecast Summary")
        
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
        
        # Individual Crime Type Forecasts
        st.divider()
        st.subheader("📈 Individual Crime Type Forecasts")
        
        forecast_years = st.slider(
            "Forecast horizon for crime types",
            min_value=1,
            max_value=5,
            value=3,
            help="Choose forecast period for individual crime types"
        )
        
        fig = plot_crime_type_forecast(filtered_df, crime_types, years_ahead=forecast_years)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Insufficient data for individual crime type forecasting.")
        
        # Key Insights
        st.divider()
        st.subheader("💡 Key Insights & Predictions")
        
        col1, col2, col3 = st.columns(3)
        
        # Current year crime count
        current_year = int(results['yearly_data']['year'].max())
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
                value=format_number(current_crimes),
                delta=None
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
        
        # Additional insights
        st.markdown("#### 📊 Forecast Summary")
        
        # Calculate average prediction across all forecast years
        avg_future_crimes = int(all_predictions.mean())
        
        # 5-year outlook
        if years_ahead >= 5:
            five_year_pred = int(all_predictions.mean(axis=0)[4] if len(all_predictions[0]) >= 5 else all_predictions.mean(axis=0)[-1])
            five_year_change = five_year_pred - current_crimes
            five_year_pct = (five_year_change / current_crimes * 100) if current_crimes > 0 else 0
            
            st.markdown(f"""
            - **Short-term Outlook (1 year):** Crimes expected to **{trend_direction.split()[1].lower()}** by **{abs(trend_pct):.1f}%**
            - **Long-term Outlook (5 years):** Projected **{five_year_pct:+.1f}%** change from current levels
            - **Average Forecast:** {format_number(avg_future_crimes)} crimes per year over the next {years_ahead} years
            - **Confidence:** Models trained on {len(results['yearly_data'])} years of historical data
            """)
        else:
            st.markdown(f"""
            - **Outlook ({years_ahead} year{'s' if years_ahead > 1 else ''}):** Crimes expected to **{trend_direction.split()[1].lower()}** by **{abs(trend_pct):.1f}%**
            - **Average Forecast:** {format_number(avg_future_crimes)} crimes per year
            - **Confidence:** Models trained on {len(results['yearly_data'])} years of historical data
            """)
        
        # Download forecast data
        st.divider()
        st.markdown("#### 📥 Download Forecast Data")
        
        csv = forecast_df.to_csv(index=False)
        st.download_button(
            label="Download Forecast as CSV",
            data=csv,
            file_name=f"crime_forecast_{state}_{current_year}_{years_ahead}years.csv",
            mime="text/csv",
            help="Download the forecast data for further analysis"
        )
    else:
        st.warning("""
        ⚠️ **Unable to generate predictions**
        
        Possible reasons:
        - Insufficient historical data (need at least 5 years)
        - Selected filters resulted in too few data points
        - Try selecting a broader date range or different location
        """)



# ==================================================
# DETAILED DATA EXPLORER
# ==================================================
st.divider()
st.subheader("🔍 Detailed Data Explorer")

with st.expander("📋 View Raw Data", expanded=False):
    st.dataframe(
        filtered_df[['state_name', 'district_name', 'year'] + crime_types],
        use_container_width=True,
        height=400
    )
    
    st.markdown(f"**Total Records:** {len(filtered_df)}")


# ==================================================
# INSIGHTS & RECOMMENDATIONS
# ==================================================
st.divider()
st.subheader("💡 Key Insights")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🔍 Observations")
    
    # Calculate insights
    top_district = filtered_df.groupby('district_name')['crime_sum'].sum().idxmax()
    top_district_crimes = int(filtered_df.groupby('district_name')['crime_sum'].sum().max())
    
    most_common_crime = filtered_df[crime_types].sum().idxmax()
    most_common_crime_count = int(filtered_df[crime_types].sum().max())
    
    st.markdown(f"""
    - **Highest Crime District:** `{top_district}` with **{format_number(top_district_crimes)}** crimes
    - **Most Common Crime Type:** `{most_common_crime}` with **{format_number(most_common_crime_count)}** cases
    - **Analysis Period:** {year_range[1] - year_range[0] + 1} years
    - **Districts Analyzed:** {filtered_df['district_name'].nunique()}
    """)

with col2:
    st.markdown("### 📊 Statistics Summary")
    
    yearly_change = filtered_df.groupby('year')['crime_sum'].sum()
    if len(yearly_change) > 1:
        trend = "📈 Increasing" if yearly_change.iloc[-1] > yearly_change.iloc[0] else "📉 Decreasing"
        change_pct = ((yearly_change.iloc[-1] - yearly_change.iloc[0]) / yearly_change.iloc[0] * 100)
        
        st.markdown(f"""
        - **Overall Trend:** {trend}
        - **Change Rate:** {change_pct:.1f}%
        - **Peak Year:** {stats['peak_year']}
        - **Average Annual Crimes:** {format_number(stats['avg_crimes_per_year'])}
        """)
    else:
        st.info("Select multiple years to see trend analysis")


# ==================================================
# FOOTER
# ==================================================
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p><strong>CrimeScope</strong> - IPC Crime Intelligence Dashboard</p>
    <p>Data Source: District-wise IPC Crimes | Last Updated: 2024</p>
</div>
""", unsafe_allow_html=True)
