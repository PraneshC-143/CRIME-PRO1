"""
Trends Analysis Page - Time Series and Pattern Analysis
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Import custom modules
from data_loader import load_data, validate_data
from utils.export_utils import export_to_csv, create_yearly_summary
from utils import format_number, apply_custom_styling

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="Trends Analysis | CrimeScope",
    page_icon="📈",
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
st.title("📈 Crime Trends Analysis")
st.markdown("Analyze temporal patterns, year-over-year changes, and seasonal trends")
st.divider()

# ==================================================
# SIDEBAR FILTERS
# ==================================================
with st.sidebar:
    st.title("🔍 Analysis Filters")
    
    # State Selection
    states = ["All States"] + sorted(df["state_name"].unique())
    selected_state = st.selectbox(
        "📍 Select State",
        options=states,
        help="Choose a state or analyze all states"
    )
    
    # Crime Types
    st.divider()
    st.subheader("🚨 Crime Types")
    
    analysis_mode = st.radio(
        "Analysis Mode",
        ["Aggregate (Total)", "Individual Crime Types", "Compare Top Crimes"]
    )
    
    if analysis_mode == "Individual Crime Types":
        top_crimes = df[crime_columns].sum().nlargest(15).index.tolist()
        selected_crimes = st.multiselect(
            "Select crime types",
            options=top_crimes,
            default=top_crimes[:3],
            max_selections=5
        )
        if not selected_crimes:
            selected_crimes = [top_crimes[0]]
    elif analysis_mode == "Compare Top Crimes":
        top_n = st.slider("Number of crimes to compare", 3, 10, 5)
        selected_crimes = df[crime_columns].sum().nlargest(top_n).index.tolist()
    else:
        selected_crimes = list(crime_columns)
    
    # Visualization Options
    st.divider()
    st.subheader("📊 Chart Options")
    
    show_trend_line = st.checkbox("Show Trend Line", value=True)
    show_annotations = st.checkbox("Show Peak/Low Markers", value=False)

# ==================================================
# FILTER DATA
# ==================================================
if selected_state == "All States":
    filtered_df = df.copy()
else:
    filtered_df = df[df["state_name"] == selected_state].copy()

# ==================================================
# KEY METRICS
# ==================================================
st.subheader("📊 Trend Overview")

yearly_crimes = filtered_df.groupby('year')[selected_crimes].sum().sum(axis=1)
years = sorted(filtered_df['year'].unique())

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if len(years) > 0:
        first_year_crimes = int(yearly_crimes[years[0]])
        st.metric(
            label=f"Crimes in {years[0]}",
            value=format_number(first_year_crimes)
        )

with col2:
    if len(years) > 0:
        last_year_crimes = int(yearly_crimes[years[-1]])
        st.metric(
            label=f"Crimes in {years[-1]}",
            value=format_number(last_year_crimes)
        )

with col3:
    if len(years) > 1:
        overall_change = last_year_crimes - first_year_crimes
        overall_pct = (overall_change / first_year_crimes * 100) if first_year_crimes > 0 else 0
        st.metric(
            label="Overall Change",
            value=f"{overall_pct:+.1f}%",
            delta=f"{overall_change:+,}",
            delta_color="inverse"
        )

with col4:
    peak_year = int(yearly_crimes.idxmax())
    peak_crimes = int(yearly_crimes.max())
    st.metric(
        label="Peak Year",
        value=peak_year,
        delta=format_number(peak_crimes)
    )

with col5:
    avg_crimes = int(yearly_crimes.mean())
    st.metric(
        label="Average/Year",
        value=format_number(avg_crimes)
    )

st.divider()

# ==================================================
# MAIN VISUALIZATIONS
# ==================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Time Series",
    "📊 Year-over-Year",
    "📉 Growth Rates",
    "�� Statistical Analysis"
])

with tab1:
    st.markdown("### Crime Trends Over Time")
    
    # Prepare data
    if analysis_mode == "Aggregate (Total)":
        yearly_data = filtered_df.groupby('year')[selected_crimes].sum().sum(axis=1).reset_index()
        yearly_data.columns = ['Year', 'Total Crimes']
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=yearly_data['Year'],
            y=yearly_data['Total Crimes'],
            mode='lines+markers',
            name='Total Crimes',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=10),
            fill='tonexty',
            fillcolor='rgba(31, 119, 180, 0.1)'
        ))
        
        # Add trend line
        if show_trend_line and len(yearly_data) > 2:
            z = np.polyfit(yearly_data['Year'], yearly_data['Total Crimes'], 1)
            p = np.poly1d(z)
            fig.add_trace(go.Scatter(
                x=yearly_data['Year'],
                y=p(yearly_data['Year']),
                mode='lines',
                name='Trend Line',
                line=dict(color='red', width=2, dash='dash')
            ))
        
        # Add annotations for peak and low
        if show_annotations:
            max_idx = yearly_data['Total Crimes'].idxmax()
            min_idx = yearly_data['Total Crimes'].idxmin()
            
            fig.add_annotation(
                x=yearly_data.loc[max_idx, 'Year'],
                y=yearly_data.loc[max_idx, 'Total Crimes'],
                text=f"Peak: {format_number(int(yearly_data.loc[max_idx, 'Total Crimes']))}",
                showarrow=True,
                arrowhead=2,
                bgcolor="red",
                font=dict(color="white")
            )
            
            fig.add_annotation(
                x=yearly_data.loc[min_idx, 'Year'],
                y=yearly_data.loc[min_idx, 'Total Crimes'],
                text=f"Low: {format_number(int(yearly_data.loc[min_idx, 'Total Crimes']))}",
                showarrow=True,
                arrowhead=2,
                bgcolor="green",
                font=dict(color="white")
            )
        
        fig.update_layout(
            title=f'Total Crime Trend - {selected_state}',
            xaxis_title='Year',
            yaxis_title='Total Crimes',
            hovermode='x unified',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    else:
        # Multiple crime types
        yearly_data = filtered_df.groupby('year')[selected_crimes].sum()
        
        fig = go.Figure()
        
        for crime in selected_crimes:
            fig.add_trace(go.Scatter(
                x=yearly_data.index,
                y=yearly_data[crime],
                mode='lines+markers',
                name=crime,
                line=dict(width=2),
                marker=dict(size=8)
            ))
        
        fig.update_layout(
            title=f'Crime Type Trends - {selected_state}',
            xaxis_title='Year',
            yaxis_title='Number of Cases',
            hovermode='x unified',
            height=500,
            legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Yearly statistics table
    st.markdown("### Yearly Statistics Table")
    yearly_stats = create_yearly_summary(filtered_df, selected_crimes)
    
    st.dataframe(
        yearly_stats.style.format({
            'Total Crimes': '{:,.0f}',
            'YoY Change': '{:+.1f}%',
            'Absolute Change': '{:+,.0f}'
        }).background_gradient(subset=['Total Crimes'], cmap='YlOrRd'),
        use_container_width=True
    )

with tab2:
    st.markdown("### Year-over-Year Comparison")
    
    yearly_totals = filtered_df.groupby('year')[selected_crimes].sum().sum(axis=1)
    yoy_df = pd.DataFrame({
        'Year': yearly_totals.index,
        'Total Crimes': yearly_totals.values
    })
    
    # Calculate YoY change
    yoy_df['YoY Change'] = yoy_df['Total Crimes'].diff()
    yoy_df['YoY %'] = yoy_df['Total Crimes'].pct_change() * 100
    yoy_df['Change Type'] = yoy_df['YoY Change'].apply(
        lambda x: 'Increase' if x > 0 else 'Decrease' if x < 0 else 'No Change'
    )
    
    # Bar chart with YoY comparison
    fig = go.Figure()
    
    colors = ['red' if x > 0 else 'green' if x < 0 else 'gray' for x in yoy_df['YoY Change'].fillna(0)]
    
    fig.add_trace(go.Bar(
        x=yoy_df['Year'][1:],
        y=yoy_df['YoY Change'][1:],
        marker_color=colors[1:],
        name='YoY Change',
        text=[f"{x:+,.0f}" for x in yoy_df['YoY Change'][1:]],
        textposition='outside'
    ))
    
    fig.update_layout(
        title='Year-over-Year Change in Crimes',
        xaxis_title='Year',
        yaxis_title='Change in Number of Crimes',
        showlegend=False,
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # YoY percentage chart
    fig = px.bar(
        yoy_df[1:],
        x='Year',
        y='YoY %',
        color='Change Type',
        color_discrete_map={'Increase': 'red', 'Decrease': 'green', 'No Change': 'gray'},
        title='Year-over-Year Percentage Change',
        labels={'YoY %': 'Percentage Change (%)'},
        text=[f"{x:+.1f}%" for x in yoy_df['YoY %'][1:]]
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(height=400)
    
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("### Growth Rate Analysis")
    
    # Calculate compound annual growth rate (CAGR)
    if len(yearly_totals) >= 2:
        start_value = yearly_totals.iloc[0]
        end_value = yearly_totals.iloc[-1]
        num_years = len(yearly_totals) - 1
        
        cagr = (((end_value / start_value) ** (1 / num_years)) - 1) * 100 if start_value > 0 else 0
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.metric(
                label="Compound Annual Growth Rate (CAGR)",
                value=f"{cagr:+.2f}%",
                help="Average annual growth rate over the entire period"
            )
            
            # Additional metrics
            st.markdown("#### Growth Statistics")
            st.markdown(f"- **Highest YoY Growth:** {yoy_df['YoY %'].max():.2f}%")
            st.markdown(f"- **Lowest YoY Growth:** {yoy_df['YoY %'].min():.2f}%")
            st.markdown(f"- **Average YoY Growth:** {yoy_df['YoY %'].mean():.2f}%")
            st.markdown(f"- **Volatility (Std Dev):** {yoy_df['YoY %'].std():.2f}%")
        
        with col2:
            # Growth rate over time
            fig = px.line(
                yoy_df[1:],
                x='Year',
                y='YoY %',
                title='Growth Rate Trend',
                markers=True,
                labels={'YoY %': 'Growth Rate (%)'}
            )
            fig.add_hline(y=0, line_dash="dash", line_color="gray")
            fig.add_hline(y=cagr, line_dash="dot", line_color="red", annotation_text=f"CAGR: {cagr:.2f}%")
            fig.update_layout(height=400)
            
            st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.markdown("### Statistical Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Distribution Analysis")
        
        # Box plot
        fig = px.box(
            y=yearly_totals.values,
            title='Crime Distribution Across Years',
            labels={'y': 'Total Crimes'},
            points='all'
        )
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # Statistics
        st.markdown("#### Descriptive Statistics")
        stats_df = pd.DataFrame({
            'Metric': ['Mean', 'Median', 'Std Dev', 'Min', 'Max', 'Range'],
            'Value': [
                f"{yearly_totals.mean():,.0f}",
                f"{yearly_totals.median():,.0f}",
                f"{yearly_totals.std():,.0f}",
                f"{yearly_totals.min():,.0f}",
                f"{yearly_totals.max():,.0f}",
                f"{yearly_totals.max() - yearly_totals.min():,.0f}"
            ]
        })
        st.dataframe(stats_df, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("#### Moving Averages")
        
        # Calculate moving averages
        ma_df = pd.DataFrame({
            'Year': yearly_totals.index,
            'Actual': yearly_totals.values
        })
        
        if len(yearly_totals) >= 3:
            ma_df['MA-3'] = yearly_totals.rolling(window=3, center=True).mean()
        
        # Plot
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=ma_df['Year'],
            y=ma_df['Actual'],
            mode='lines+markers',
            name='Actual',
            line=dict(color='lightblue', width=2)
        ))
        
        if 'MA-3' in ma_df.columns:
            fig.add_trace(go.Scatter(
                x=ma_df['Year'],
                y=ma_df['MA-3'],
                mode='lines',
                name='3-Year Moving Average',
                line=dict(color='red', width=3)
            ))
        
        fig.update_layout(
            title='Crime Trends with Moving Average',
            xaxis_title='Year',
            yaxis_title='Total Crimes',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# ==================================================
# EXPORT SECTION
# ==================================================
st.subheader("📥 Export Trend Data")

export_to_csv(
    yearly_stats,
    filename=f"trends_analysis_{selected_state.replace(' ', '_')}_{years[0]}-{years[-1]}.csv"
)

# ==================================================
# FOOTER
# ==================================================
st.divider()
st.caption(f"Trends Analysis | {selected_state} | {len(years)} years analyzed")
