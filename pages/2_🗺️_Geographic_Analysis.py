"""
Geographic Analysis Page - Interactive Maps and Regional Insights
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Import custom modules
from data_loader import load_data, validate_data
from utils.map_generator import (
    create_choropleth_map,
    create_bubble_map,
    create_state_heatmap,
    create_treemap,
    create_sunburst
)
from utils.export_utils import export_to_csv
from utils import format_number, apply_custom_styling

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="Geographic Analysis | CrimeScope",
    page_icon="🗺️",
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
st.title("🗺️ Geographic Crime Analysis")
st.markdown("Interactive maps and visualizations showing regional crime distribution")
st.divider()

# ==================================================
# SIDEBAR FILTERS
# ==================================================
with st.sidebar:
    st.title("🔍 Geographic Filters")
    
    # Year Selection
    years = sorted(df["year"].unique(), reverse=True)
    selected_year = st.selectbox(
        "📅 Select Year",
        options=years,
        help="Choose a specific year for analysis"
    )
    
    # Crime Type Selection
    st.divider()
    st.subheader("🚨 Crime Types")
    
    crime_selection_mode = st.radio(
        "Selection Mode",
        ["All Crimes", "Top Crimes", "Custom Selection"]
    )
    
    if crime_selection_mode == "All Crimes":
        selected_crimes = list(crime_columns)
    elif crime_selection_mode == "Top Crimes":
        top_n = st.slider("Number of top crimes", 5, 20, 10)
        selected_crimes = df[crime_columns].sum().nlargest(top_n).index.tolist()
    else:
        top_crimes = df[crime_columns].sum().nlargest(20).index.tolist()
        selected_crimes = st.multiselect(
            "Choose crime types",
            options=top_crimes,
            default=top_crimes[:5]
        )
    
    if not selected_crimes:
        selected_crimes = [crime_columns[0]]
    
    # Visualization Options
    st.divider()
    st.subheader("🎨 Display Options")
    
    color_scheme = st.selectbox(
        "Color Scheme",
        ["Reds", "YlOrRd", "OrRd", "RdYlGn_r", "Plasma"]
    )

# ==================================================
# FILTER DATA
# ==================================================
filtered_df = df[df["year"] == selected_year].copy()

# ==================================================
# KEY METRICS FOR SELECTED YEAR
# ==================================================
st.subheader(f"📊 Key Metrics for {selected_year}")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_crimes = int(filtered_df[selected_crimes].sum().sum())
    st.metric(
        label="Total Crimes",
        value=format_number(total_crimes)
    )

with col2:
    states_count = filtered_df["state_name"].nunique()
    st.metric(
        label="States",
        value=states_count
    )

with col3:
    districts_count = filtered_df["district_name"].nunique()
    st.metric(
        label="Districts",
        value=districts_count
    )

with col4:
    # Most affected state
    state_crimes = filtered_df.groupby('state_name')[selected_crimes].sum().sum(axis=1)
    most_affected = state_crimes.idxmax()
    st.metric(
        label="Most Affected State",
        value=most_affected[:12] + "..." if len(most_affected) > 12 else most_affected
    )

st.divider()

# ==================================================
# MAIN VISUALIZATIONS
# ==================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "🗺️ Choropleth Map",
    "🎯 Treemap",
    "☀️ Sunburst",
    "📊 State Heatmap"
])

with tab1:
    st.markdown("### Crime Distribution by State")
    st.caption("Interactive choropleth map showing crime intensity across Indian states")
    
    try:
        fig = create_choropleth_map(
            filtered_df,
            selected_crimes,
            title=f"Crime Distribution Across India - {selected_year}"
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning(f"Map visualization unavailable. Showing alternative visualization.")
        
        # Alternative: Bar chart by state
        state_crimes = filtered_df.groupby('state_name')[selected_crimes].sum().sum(axis=1)
        state_crimes = state_crimes.sort_values(ascending=True).tail(20)
        
        fig = px.bar(
            x=state_crimes.values,
            y=state_crimes.index,
            orientation='h',
            title=f'Top 20 States by Crime Count - {selected_year}',
            labels={'x': 'Total Crimes', 'y': 'State'},
            color=state_crimes.values,
            color_continuous_scale=color_scheme
        )
        fig.update_layout(showlegend=False, height=600)
        st.plotly_chart(fig, use_container_width=True)
    
    # Top states table
    st.markdown("#### Top 10 States")
    state_crimes_df = filtered_df.groupby('state_name')[selected_crimes].sum()
    state_crimes_df['Total'] = state_crimes_df.sum(axis=1)
    top_states = state_crimes_df[['Total']].nlargest(10, 'Total')
    top_states['Rank'] = range(1, len(top_states) + 1)
    top_states = top_states[['Rank', 'Total']]
    
    st.dataframe(
        top_states.style.format({'Total': '{:,.0f}'}).background_gradient(
            subset=['Total'], cmap='Reds'
        ),
        use_container_width=True
    )

with tab2:
    st.markdown("### Hierarchical Treemap View")
    st.caption("Explore crime distribution by state and district")
    
    fig = create_treemap(
        filtered_df,
        selected_crimes,
        title=f"Crime Distribution Treemap - {selected_year}"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("💡 Click on a state to drill down into districts. Click outside to zoom out.")

with tab3:
    st.markdown("### Sunburst Chart")
    st.caption("Radial visualization of hierarchical crime data")
    
    fig = create_sunburst(
        filtered_df,
        selected_crimes,
        title=f"Crime Distribution Sunburst - {selected_year}"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("💡 Click on segments to zoom in and explore specific regions.")

with tab4:
    st.markdown("### State-wise Crime Type Heatmap")
    st.caption("Correlation between states and crime types")
    
    fig = create_state_heatmap(filtered_df, selected_crimes, top_n=20)
    st.plotly_chart(fig, use_container_width=True)
    
    # Crime type distribution
    st.markdown("#### Crime Type Distribution")
    crime_totals = filtered_df[selected_crimes].sum().sort_values(ascending=False).head(15)
    
    fig = px.pie(
        values=crime_totals.values,
        names=crime_totals.index,
        title='Top 15 Crime Types Distribution',
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.get(color_scheme, px.colors.sequential.Reds)
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ==================================================
# REGIONAL COMPARISON
# ==================================================
st.subheader("📊 Regional Deep Dive")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Top 15 Districts")
    
    district_crimes = filtered_df.groupby(['state_name', 'district_name'])[selected_crimes].sum().sum(axis=1)
    top_districts = district_crimes.nlargest(15).reset_index()
    top_districts.columns = ['State', 'District', 'Total Crimes']
    
    fig = px.bar(
        top_districts,
        x='Total Crimes',
        y='District',
        orientation='h',
        title='Top 15 Districts by Crime Count',
        color='Total Crimes',
        color_continuous_scale=color_scheme,
        hover_data=['State']
    )
    fig.update_layout(showlegend=False, height=500)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### State Distribution (Percentage)")
    
    state_crimes = filtered_df.groupby('state_name')[selected_crimes].sum().sum(axis=1)
    top_10_states = state_crimes.nlargest(10)
    others = state_crimes.sum() - top_10_states.sum()
    
    # Add "Others" category
    if others > 0:
        top_10_states = pd.concat([top_10_states, pd.Series({'Others': others})])
    
    fig = px.bar(
        x=top_10_states.values,
        y=top_10_states.index,
        orientation='h',
        title='State-wise Crime Distribution (Top 10 + Others)',
        labels={'x': 'Total Crimes', 'y': 'State'},
        color=top_10_states.values,
        color_continuous_scale=color_scheme
    )
    fig.update_layout(showlegend=False, height=500)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ==================================================
# EXPORT SECTION
# ==================================================
st.subheader("📥 Export Geographic Data")

col1, col2 = st.columns(2)

with col1:
    # Export state-level data
    state_export = filtered_df.groupby('state_name')[selected_crimes].sum()
    state_export['Total'] = state_export.sum(axis=1)
    export_to_csv(
        state_export.reset_index(),
        filename=f"state_crimes_{selected_year}.csv"
    )

with col2:
    # Export district-level data
    district_export = filtered_df.groupby(['state_name', 'district_name'])[selected_crimes].sum()
    district_export['Total'] = district_export.sum(axis=1)
    export_to_csv(
        district_export.reset_index(),
        filename=f"district_crimes_{selected_year}.csv"
    )

# ==================================================
# FOOTER
# ==================================================
st.divider()
st.caption(f"Geographic Analysis | Year: {selected_year} | {len(filtered_df)} districts analyzed")
