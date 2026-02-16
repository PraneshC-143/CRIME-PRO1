"""
Dashboard Page - Comprehensive Analytics Overview
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Import custom modules
from data_loader import load_data, validate_data, filter_data
from utils.kpi_calculator import (
    calculate_total_crimes,
    calculate_crime_rate,
    get_most_affected_state,
    get_highest_crime_category,
    calculate_yoy_growth,
    get_top_states_ranking,
    calculate_district_kpis
)
from utils.export_utils import export_to_csv, create_summary_report
from utils import format_number, apply_custom_styling
from analytics import get_crime_statistics
from visualizations import plot_top_districts, plot_crime_trend, plot_distribution

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="Dashboard | CrimeScope",
    page_icon="📊",
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
st.title("📊 Comprehensive Analytics Dashboard")
st.markdown("Detailed overview of crime statistics with interactive filters and KPIs")
st.divider()

# ==================================================
# SIDEBAR FILTERS
# ==================================================
with st.sidebar:
    st.title("🔍 Filters")
    st.caption("Customize your analysis")
    
    # State Selection
    states = sorted(df["state_name"].unique())
    selected_states = st.multiselect(
        "📍 Select States",
        options=states,
        default=[states[0]],
        help="Choose one or more states"
    )
    
    if not selected_states:
        st.warning("⚠️ Please select at least one state")
        selected_states = [states[0]]
    
    # Year Range
    year_min = int(df["year"].min())
    year_max = int(df["year"].max())
    year_range = st.slider(
        "📅 Year Range",
        year_min,
        year_max,
        (year_min, year_max),
        help="Select year range for analysis"
    )
    
    # Crime Types
    st.divider()
    st.subheader("🚨 Crime Types")
    
    select_all = st.checkbox("Select All Crime Types", value=True)
    
    if select_all:
        selected_crimes = list(crime_columns)
    else:
        # Show top 20 crime types for selection
        top_crimes = df[crime_columns].sum().nlargest(20).index.tolist()
        selected_crimes = st.multiselect(
            "Choose crime types",
            options=top_crimes,
            default=top_crimes[:5],
            help="Select specific crime types to analyze"
        )
    
    if not selected_crimes:
        st.warning("⚠️ Please select at least one crime type")
        selected_crimes = [crime_columns[0]]
    
    # Quick Actions
    st.divider()
    if st.button("🔄 Reset Filters"):
        st.rerun()

# ==================================================
# FILTER DATA
# ==================================================
filtered_df = df[
    (df["state_name"].isin(selected_states)) &
    (df["year"] >= year_range[0]) &
    (df["year"] <= year_range[1])
].copy()

filtered_df["crime_sum"] = filtered_df[selected_crimes].sum(axis=1)

# ==================================================
# KPI SECTION
# ==================================================
st.subheader("📊 Key Performance Indicators")

kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5, kpi_col6 = st.columns(6)

with kpi_col1:
    total_crimes = int(filtered_df[selected_crimes].sum().sum())
    st.metric(
        label="Total Crimes",
        value=format_number(total_crimes)
    )

with kpi_col2:
    districts_count = filtered_df["district_name"].nunique()
    st.metric(
        label="Districts Analyzed",
        value=districts_count
    )

with kpi_col3:
    years_analyzed = year_range[1] - year_range[0] + 1
    avg_per_year = int(total_crimes / years_analyzed) if years_analyzed > 0 else 0
    st.metric(
        label="Avg Crimes/Year",
        value=format_number(avg_per_year)
    )

with kpi_col4:
    # Peak year
    yearly_crimes = filtered_df.groupby('year')[selected_crimes].sum().sum(axis=1)
    if len(yearly_crimes) > 0:
        peak_year = int(yearly_crimes.idxmax())
        peak_crimes = int(yearly_crimes.max())
        st.metric(
            label="Peak Year",
            value=peak_year,
            delta=format_number(peak_crimes)
        )
    else:
        st.metric(label="Peak Year", value="N/A")

with kpi_col5:
    # YoY Change
    if len(yearly_crimes) >= 2:
        last_year = yearly_crimes.iloc[-1]
        prev_year = yearly_crimes.iloc[-2]
        yoy_change = ((last_year - prev_year) / prev_year * 100) if prev_year > 0 else 0
        st.metric(
            label="YoY Change",
            value=f"{yoy_change:+.1f}%",
            delta=f"{int(last_year - prev_year):+,}",
            delta_color="inverse"
        )
    else:
        st.metric(label="YoY Change", value="N/A")

with kpi_col6:
    # Crime Rate per District
    crime_rate = total_crimes / districts_count if districts_count > 0 else 0
    st.metric(
        label="Crimes/District",
        value=format_number(int(crime_rate))
    )

st.divider()

# ==================================================
# MAIN VISUALIZATIONS
# ==================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Trends Analysis",
    "🏘️ District Rankings",
    "📊 Crime Distribution",
    "📋 Detailed Statistics"
])

with tab1:
    st.markdown("### Crime Trends Over Time")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Yearly trend
        fig = plot_crime_trend(filtered_df, selected_crimes)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Yearly Statistics")
        yearly_stats = filtered_df.groupby('year')[selected_crimes].sum()
        yearly_stats['Total'] = yearly_stats.sum(axis=1)
        yearly_stats = yearly_stats[['Total']].sort_index(ascending=False)
        
        # Calculate YoY change
        yearly_stats['YoY Change %'] = yearly_stats['Total'].pct_change(-1) * 100
        
        st.dataframe(
            yearly_stats.style.format({
                'Total': '{:,.0f}',
                'YoY Change %': '{:+.1f}%'
            }).background_gradient(subset=['Total'], cmap='Reds'),
            use_container_width=True,
            height=400
        )

with tab2:
    st.markdown("### Top Districts by Crime Count")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = plot_top_districts(filtered_df, top_n=15)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Top 10 Districts Table")
        district_crimes = filtered_df.groupby('district_name')[selected_crimes].sum()
        district_crimes['Total'] = district_crimes.sum(axis=1)
        top_districts = district_crimes[['Total']].nlargest(10, 'Total')
        top_districts['Rank'] = range(1, len(top_districts) + 1)
        top_districts = top_districts[['Rank', 'Total']]
        
        st.dataframe(
            top_districts.style.format({'Total': '{:,.0f}'}),
            use_container_width=True
        )

with tab3:
    st.markdown("### Crime Type Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = plot_distribution(filtered_df, selected_crimes)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Crime Type Rankings")
        crime_totals = filtered_df[selected_crimes].sum().sort_values(ascending=False).head(10)
        
        crime_df = pd.DataFrame({
            'Crime Type': crime_totals.index,
            'Total Cases': crime_totals.values,
            'Percentage': (crime_totals.values / crime_totals.sum() * 100)
        })
        crime_df['Rank'] = range(1, len(crime_df) + 1)
        crime_df = crime_df[['Rank', 'Crime Type', 'Total Cases', 'Percentage']]
        
        st.dataframe(
            crime_df.style.format({
                'Total Cases': '{:,.0f}',
                'Percentage': '{:.1f}%'
            }).background_gradient(subset=['Total Cases'], cmap='YlOrRd'),
            use_container_width=True,
            height=400
        )

with tab4:
    st.markdown("### Detailed Statistics Summary")
    
    # Summary report
    summary_df = create_summary_report(
        filtered_df,
        selected_crimes,
        state=", ".join(selected_states) if len(selected_states) <= 3 else f"{len(selected_states)} states"
    )
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("#### Summary Report")
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("#### State Comparison")
        if len(selected_states) > 1:
            state_comparison = filtered_df.groupby('state_name')[selected_crimes].sum()
            state_comparison['Total'] = state_comparison.sum(axis=1)
            state_comparison = state_comparison[['Total']].sort_values('Total', ascending=False)
            
            fig = px.bar(
                state_comparison.reset_index(),
                x='state_name',
                y='Total',
                title='Crime Distribution Across Selected States',
                labels={'state_name': 'State', 'Total': 'Total Crimes'},
                color='Total',
                color_continuous_scale='Reds'
            )
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Select multiple states to see comparison")

st.divider()

# ==================================================
# EXPORT SECTION
# ==================================================
st.subheader("📥 Export Data")

col1, col2, col3 = st.columns(3)

with col1:
    export_to_csv(
        filtered_df[['state_name', 'district_name', 'year'] + selected_crimes],
        filename=f"crime_data_{'-'.join(selected_states[:2])}_{year_range[0]}-{year_range[1]}.csv"
    )

with col2:
    # Export summary
    export_to_csv(
        summary_df,
        filename=f"summary_report_{year_range[0]}-{year_range[1]}.csv"
    )

with col3:
    # Export yearly statistics
    yearly_export = filtered_df.groupby('year')[selected_crimes].sum()
    yearly_export['Total'] = yearly_export.sum(axis=1)
    export_to_csv(
        yearly_export,
        filename=f"yearly_stats_{year_range[0]}-{year_range[1]}.csv"
    )

# ==================================================
# FOOTER
# ==================================================
st.divider()
st.caption(f"Dashboard | Analyzing {len(filtered_df)} records across {len(selected_states)} state(s)")
