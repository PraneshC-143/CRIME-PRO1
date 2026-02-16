"""
CrimeScope: Interactive IPC Crime Intelligence Dashboard
Main Landing Page - Executive Overview
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Import custom modules
from config import PAGE_TITLE, PAGE_LAYOUT, PAGE_ICON
from data_loader import load_data, validate_data
from utils.kpi_calculator import (
    calculate_total_crimes,
    calculate_crime_rate,
    get_most_affected_state,
    get_highest_crime_category,
    calculate_yoy_growth,
    get_top_states_ranking,
    get_trend_indicator
)
from utils import format_number, apply_custom_styling


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
# HERO SECTION
# ==================================================
st.markdown("""
<div style='text-align: center; padding: 2rem 0;'>
    <h1 style='color: #1f77b4; font-size: 3rem; margin-bottom: 0.5rem;'>
        📊 CrimeScope
    </h1>
    <h3 style='color: #666; font-weight: 300; margin-top: 0;'>
        Interactive IPC Crime Intelligence Dashboard
    </h3>
    <p style='color: #888; font-size: 1.1rem; margin-top: 1rem;'>
        Professional Analytics Platform for District-wise Crime Analysis in India
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()


# ==================================================
# EXECUTIVE SUMMARY - KPI CARDS
# ==================================================
st.subheader("📈 Executive Summary")
st.caption("Key Performance Indicators at a Glance")

# Calculate KPIs
total_crimes_kpi = calculate_total_crimes(df, crime_columns)
crime_rate_kpi = calculate_crime_rate(df, crime_columns)
most_affected_kpi = get_most_affected_state(df, crime_columns)
highest_crime_kpi = get_highest_crime_category(df, crime_columns)
yoy_growth_kpi = calculate_yoy_growth(df, crime_columns)

# Display KPIs in columns
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    icon, label, color = get_trend_indicator(
        total_crimes_kpi['value'],
        total_crimes_kpi['value'] - total_crimes_kpi['change']
    )
    st.metric(
        label="Total Crimes",
        value=format_number(total_crimes_kpi['value']),
        delta=f"{total_crimes_kpi['pct_change']:+.1f}% YoY",
        delta_color="inverse"
    )

with col2:
    st.metric(
        label="Crime Rate",
        value=f"{crime_rate_kpi['value']:.1f}",
        help=f"Per {format_number(crime_rate_kpi['per'])} population (estimated)"
    )

with col3:
    st.metric(
        label="Most Affected State",
        value=most_affected_kpi['state'][:15] + "..." if len(most_affected_kpi['state']) > 15 else most_affected_kpi['state'],
        delta=format_number(most_affected_kpi['crimes']) + " crimes"
    )

with col4:
    crime_name = highest_crime_kpi['category'][:20] + "..." if len(highest_crime_kpi['category']) > 20 else highest_crime_kpi['category']
    st.metric(
        label="Highest Crime Type",
        value=crime_name,
        delta=format_number(highest_crime_kpi['count']) + " cases"
    )

with col5:
    trend_icon = "📈" if yoy_growth_kpi['rate'] > 0 else "📉" if yoy_growth_kpi['rate'] < 0 else "➡️"
    st.metric(
        label="YoY Growth Rate",
        value=f"{yoy_growth_kpi['rate']:+.1f}%",
        delta=f"{yoy_growth_kpi['trend'].title()}",
        delta_color="inverse" if yoy_growth_kpi['rate'] > 0 else "normal"
    )

st.divider()


# ==================================================
# KEY METRICS SUMMARY
# ==================================================
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🎯 Quick Insights")
    
    # Top 5 States Ranking
    top_states = get_top_states_ranking(df, crime_columns, top_n=5)
    
    st.markdown("### 🏆 Top 5 States by Crime Count")
    
    # Create a styled table
    for idx, row in top_states.iterrows():
        rank_emoji = "🥇" if row['Rank'] == 1 else "🥈" if row['Rank'] == 2 else "🥉" if row['Rank'] == 3 else f"{row['Rank']}."
        col_a, col_b, col_c = st.columns([0.3, 2, 1])
        with col_a:
            st.markdown(f"**{rank_emoji}**")
        with col_b:
            st.markdown(f"**{row['State']}**")
        with col_c:
            st.markdown(f"`{format_number(row['Total Crimes'])}` crimes")

with col2:
    st.subheader("📊 Data Coverage")
    
    # Data coverage metrics
    coverage_data = {
        'Metric': [
            '📅 Years Covered',
            '🗺️ States',
            '🏘️ Districts',
            '📋 Crime Types',
            '📈 Total Records'
        ],
        'Value': [
            f"{int(df['year'].min())} - {int(df['year'].max())}",
            f"{df['state_name'].nunique()}",
            f"{df['district_name'].nunique()}",
            f"{len(crime_columns)}",
            f"{format_number(len(df))}"
        ]
    }
    
    for metric, value in zip(coverage_data['Metric'], coverage_data['Value']):
        st.markdown(f"**{metric}:** {value}")

st.divider()


# ==================================================
# TRENDS VISUALIZATION
# ==================================================
st.subheader("📈 Crime Trends Overview")

# Yearly trend
yearly_crimes = df.groupby('year')[crime_columns].sum().sum(axis=1).reset_index()
yearly_crimes.columns = ['Year', 'Total Crimes']

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=yearly_crimes['Year'],
    y=yearly_crimes['Total Crimes'],
    mode='lines+markers',
    name='Total Crimes',
    line=dict(color='#1f77b4', width=3),
    marker=dict(size=10, color='#1f77b4'),
    fill='tonexty',
    fillcolor='rgba(31, 119, 180, 0.1)'
))

fig.update_layout(
    title='Total Crimes Trend Over Years',
    xaxis_title='Year',
    yaxis_title='Total Crimes',
    hovermode='x unified',
    height=400,
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)


# ==================================================
# GEOGRAPHIC OVERVIEW
# ==================================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("🗺️ State-wise Distribution")
    
    # State distribution pie chart
    state_crimes = df.groupby('state_name')[crime_columns].sum().sum(axis=1).nlargest(10)
    
    fig = px.pie(
        values=state_crimes.values,
        names=state_crimes.index,
        title='Top 10 States Crime Distribution',
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Reds
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400, showlegend=False)
    
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🔍 Crime Categories")
    
    # Top crime types
    top_crimes = df[crime_columns].sum().nlargest(10).sort_values()
    
    fig = px.bar(
        x=top_crimes.values,
        y=top_crimes.index,
        orientation='h',
        title='Top 10 Crime Types',
        labels={'x': 'Total Cases', 'y': 'Crime Type'},
        color=top_crimes.values,
        color_continuous_scale='Reds'
    )
    
    fig.update_layout(height=400, showlegend=False)
    
    st.plotly_chart(fig, use_container_width=True)

st.divider()


# ==================================================
# NAVIGATION GUIDE
# ==================================================
st.subheader("🧭 Explore the Dashboard")
st.markdown("""
Navigate to different sections of the dashboard to explore in-depth analytics:
""")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### 📊 Dashboard
    Comprehensive overview with interactive KPI cards and detailed metrics.
    
    ### 🗺️ Geographic Analysis
    Interactive maps showing crime distribution across states and districts.
    """)

with col2:
    st.markdown("""
    ### 📈 Trends Analysis
    Time series visualizations, YoY comparisons, and trend patterns.
    
    ### 🔍 Deep Dive Analysis
    Detailed breakdowns by crime types, correlations, and comparisons.
    """)

with col3:
    st.markdown("""
    ### 🤖 Predictions & Forecasting
    Machine learning based predictions and future crime forecasting.
    
    ---
    
    💡 **Tip:** Use the sidebar to filter data by state, district, year, and crime types.
    """)

st.divider()


# ==================================================
# RECENT HIGHLIGHTS
# ==================================================
st.subheader("✨ Recent Highlights")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("""
    **📊 Latest Year Data**
    
    Data for year {latest_year} shows {trend} in total crime cases across India.
    """.format(
        latest_year=int(df['year'].max()),
        trend="an increase" if total_crimes_kpi['change'] > 0 else "a decrease"
    ))

with col2:
    st.success("""
    **🎯 Analysis Ready**
    
    {states} states and {districts} districts analyzed across {years} years of data.
    """.format(
        states=df['state_name'].nunique(),
        districts=df['district_name'].nunique(),
        years=int(df['year'].max()) - int(df['year'].min()) + 1
    ))

with col3:
    st.warning("""
    **⚡ Key Insight**
    
    {pct:.1f}% of total crimes concentrated in top 10 districts. Focus areas identified.
    """.format(
        pct=(df.groupby('district_name')[crime_columns].sum().sum(axis=1).nlargest(10).sum() / 
             df[crime_columns].sum().sum() * 100)
    ))


# ==================================================
# FOOTER
# ==================================================
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p><strong>CrimeScope</strong> - Professional Crime Intelligence Dashboard</p>
    <p>District-wise IPC Crime Analysis | Data: 2017-2022 | Last Updated: {date}</p>
    <p style='font-size: 0.9rem; color: #888;'>
        Built with Streamlit • Powered by Plotly • Data Analytics & ML
    </p>
</div>
""".format(date=datetime.now().strftime("%B %Y")), unsafe_allow_html=True)
