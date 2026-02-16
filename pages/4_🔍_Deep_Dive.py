"""
Deep Dive Analysis Page - Detailed Crime Analysis and Comparisons
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Import custom modules
from data_loader import load_data, validate_data
from visualizations import plot_correlation_heatmap, plot_heatmap_by_district
from utils.export_utils import export_to_csv, create_crime_type_summary
from utils import format_number, apply_custom_styling

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="Deep Dive Analysis | CrimeScope",
    page_icon="🔍",
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
st.title("🔍 Deep Dive Crime Analysis")
st.markdown("Detailed breakdowns, correlations, and comparative analysis")
st.divider()

# ==================================================
# SIDEBAR FILTERS
# ==================================================
with st.sidebar:
    st.title("🔍 Analysis Settings")
    
    # Analysis Type
    analysis_type = st.selectbox(
        "Analysis Type",
        ["Crime Type Analysis", "State Comparison", "District Comparison", "Correlation Analysis"]
    )
    
    st.divider()
    
    # Year Range
    year_min = int(df["year"].min())
    year_max = int(df["year"].max())
    year_range = st.slider(
        "📅 Year Range",
        year_min,
        year_max,
        (year_min, year_max)
    )
    
    # Additional filters based on analysis type
    if analysis_type in ["State Comparison", "District Comparison"]:
        states = sorted(df["state_name"].unique())
        selected_states = st.multiselect(
            "📍 Select States",
            options=states,
            default=states[:3],
            max_selections=5
        )
        
        if not selected_states:
            selected_states = [states[0]]
    else:
        selected_states = df["state_name"].unique().tolist()
    
    st.divider()
    
    # Crime Types Selection
    st.subheader("🚨 Crime Types")
    top_n_crimes = st.slider("Top N Crime Types", 5, 20, 10)
    selected_crimes = df[crime_columns].sum().nlargest(top_n_crimes).index.tolist()

# ==================================================
# FILTER DATA
# ==================================================
filtered_df = df[
    (df["state_name"].isin(selected_states)) &
    (df["year"] >= year_range[0]) &
    (df["year"] <= year_range[1])
].copy()

# ==================================================
# ANALYSIS SECTIONS
# ==================================================

if analysis_type == "Crime Type Analysis":
    st.subheader("📊 Crime Type Deep Dive")
    
    # Crime type summary
    crime_summary = create_crime_type_summary(filtered_df, selected_crimes)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Crime Type Rankings")
        st.dataframe(
            crime_summary.style.format({
                'Total Cases': '{:,.0f}',
                'Percentage': '{:.2f}%'
            }).background_gradient(subset=['Total Cases'], cmap='YlOrRd'),
            use_container_width=True,
            height=400
        )
        
        # Quick stats
        st.markdown("### Quick Statistics")
        total_crimes = int(filtered_df[selected_crimes].sum().sum())
        st.metric("Total Crimes", format_number(total_crimes))
        st.metric("Crime Types Analyzed", len(selected_crimes))
        st.metric("Records", format_number(len(filtered_df)))
    
    with col2:
        st.markdown("### Crime Type Distribution")
        
        # Horizontal bar chart
        crime_totals = filtered_df[selected_crimes].sum().sort_values(ascending=True)
        
        fig = px.bar(
            x=crime_totals.values,
            y=crime_totals.index,
            orientation='h',
            title='Crime Type Comparison',
            labels={'x': 'Total Cases', 'y': 'Crime Type'},
            color=crime_totals.values,
            color_continuous_scale='Reds',
            text=[f"{x:,.0f}" for x in crime_totals.values]
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(showlegend=False, height=600)
        st.plotly_chart(fig, use_container_width=True)
    
    # Trend over years for each crime type
    st.divider()
    st.markdown("### Crime Type Trends Over Time")
    
    # Select specific crime types to compare
    compare_crimes = st.multiselect(
        "Select crime types to compare trends",
        options=selected_crimes,
        default=selected_crimes[:5],
        max_selections=7
    )
    
    if compare_crimes:
        yearly_crime_data = filtered_df.groupby('year')[compare_crimes].sum()
        
        fig = go.Figure()
        
        for crime in compare_crimes:
            fig.add_trace(go.Scatter(
                x=yearly_crime_data.index,
                y=yearly_crime_data[crime],
                mode='lines+markers',
                name=crime,
                line=dict(width=2),
                marker=dict(size=8)
            ))
        
        fig.update_layout(
            title='Crime Type Trends Comparison',
            xaxis_title='Year',
            yaxis_title='Number of Cases',
            hovermode='x unified',
            height=500,
            legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02)
        )
        
        st.plotly_chart(fig, use_container_width=True)

elif analysis_type == "State Comparison":
    st.subheader("🗺️ State-by-State Comparison")
    
    # State comparison metrics
    state_crimes = filtered_df.groupby('state_name')[selected_crimes].sum()
    state_crimes['Total'] = state_crimes.sum(axis=1)
    state_crimes = state_crimes.sort_values('Total', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### State Rankings")
        
        ranking_df = state_crimes[['Total']].reset_index()
        ranking_df['Rank'] = range(1, len(ranking_df) + 1)
        ranking_df.columns = ['State', 'Total Crimes', 'Rank']
        ranking_df = ranking_df[['Rank', 'State', 'Total Crimes']]
        
        st.dataframe(
            ranking_df.style.format({'Total Crimes': '{:,.0f}'}).background_gradient(
                subset=['Total Crimes'], cmap='Reds'
            ),
            use_container_width=True,
            height=400
        )
    
    with col2:
        st.markdown("### State Crime Distribution")
        
        fig = px.pie(
            values=state_crimes['Total'],
            names=state_crimes.index,
            title='Crime Distribution Across States',
            hole=0.4
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed comparison chart
    st.divider()
    st.markdown("### Detailed State Comparison")
    
    # Select top crime types for comparison
    top_crimes_for_comparison = state_crimes.drop('Total', axis=1).sum().nlargest(10).index.tolist()
    
    state_comparison_data = state_crimes[top_crimes_for_comparison]
    
    fig = px.bar(
        state_comparison_data,
        barmode='group',
        title='State Comparison by Crime Type',
        labels={'value': 'Number of Cases', 'variable': 'Crime Type'},
        height=500
    )
    fig.update_layout(xaxis_title='State', yaxis_title='Number of Cases')
    st.plotly_chart(fig, use_container_width=True)
    
    # Heatmap
    st.markdown("### State-Crime Type Heatmap")
    
    fig = px.imshow(
        state_comparison_data.T,
        labels=dict(x="State", y="Crime Type", color="Count"),
        title='Crime Intensity Heatmap',
        aspect='auto',
        color_continuous_scale='YlOrRd'
    )
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)

elif analysis_type == "District Comparison":
    st.subheader("🏘️ District-Level Analysis")
    
    # Top districts
    district_crimes = filtered_df.groupby(['state_name', 'district_name'])[selected_crimes].sum()
    district_crimes['Total'] = district_crimes.sum(axis=1)
    top_districts = district_crimes.nlargest(20, 'Total').reset_index()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Top 20 Districts")
        
        ranking_df = top_districts[['state_name', 'district_name', 'Total']].copy()
        ranking_df['Rank'] = range(1, len(ranking_df) + 1)
        ranking_df.columns = ['State', 'District', 'Total Crimes', 'Rank']
        ranking_df = ranking_df[['Rank', 'District', 'State', 'Total Crimes']]
        
        st.dataframe(
            ranking_df.style.format({'Total Crimes': '{:,.0f}'}).background_gradient(
                subset=['Total Crimes'], cmap='Reds'
            ),
            use_container_width=True,
            height=600
        )
    
    with col2:
        st.markdown("### District Crime Comparison")
        
        fig = px.bar(
            top_districts,
            x='Total',
            y='district_name',
            orientation='h',
            color='state_name',
            title='Top 20 Districts by Crime Count',
            labels={'Total': 'Total Crimes', 'district_name': 'District', 'state_name': 'State'},
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # District heatmap
    st.divider()
    st.markdown("### District-Crime Type Heatmap")
    
    if len(selected_crimes) >= 2:
        fig = plot_heatmap_by_district(filtered_df, selected_crimes)
        st.plotly_chart(fig, use_container_width=True)

elif analysis_type == "Correlation Analysis":
    st.subheader("🔗 Crime Type Correlation Analysis")
    
    if len(selected_crimes) >= 2:
        st.markdown("### Correlation Matrix")
        st.caption("Explore relationships between different crime types")
        
        fig = plot_correlation_heatmap(filtered_df, selected_crimes)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        
        # Correlation insights
        st.divider()
        st.markdown("### Correlation Insights")
        
        corr_matrix = filtered_df[selected_crimes].corr()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Highest Positive Correlations")
            
            # Get top positive correlations
            upper_tri = np.triu(np.ones_like(corr_matrix), k=1).astype(bool)
            corr_df = corr_matrix.where(upper_tri).stack().reset_index()
            corr_df.columns = ['Crime Type 1', 'Crime Type 2', 'Correlation']
            top_positive = corr_df.nlargest(10, 'Correlation')
            
            st.dataframe(
                top_positive.style.format({'Correlation': '{:.3f}'}).background_gradient(
                    subset=['Correlation'], cmap='Greens'
                ),
                use_container_width=True
            )
        
        with col2:
            st.markdown("#### Highest Negative Correlations")
            
            # Get top negative correlations
            top_negative = corr_df.nsmallest(10, 'Correlation')
            
            st.dataframe(
                top_negative.style.format({'Correlation': '{:.3f}'}).background_gradient(
                    subset=['Correlation'], cmap='Reds_r'
                ),
                use_container_width=True
            )
    else:
        st.warning("⚠️ Select at least 2 crime types for correlation analysis")

st.divider()

# ==================================================
# EXPORT SECTION
# ==================================================
st.subheader("📥 Export Analysis Data")

if analysis_type == "Crime Type Analysis":
    export_to_csv(
        crime_summary,
        filename=f"crime_type_analysis_{year_range[0]}-{year_range[1]}.csv"
    )
elif analysis_type == "State Comparison":
    export_data = state_crimes.reset_index()
    export_to_csv(
        export_data,
        filename=f"state_comparison_{year_range[0]}-{year_range[1]}.csv"
    )
elif analysis_type == "District Comparison":
    export_to_csv(
        top_districts,
        filename=f"district_comparison_{year_range[0]}-{year_range[1]}.csv"
    )
elif analysis_type == "Correlation Analysis":
    if len(selected_crimes) >= 2:
        corr_export = corr_matrix.reset_index()
        export_to_csv(
            corr_export,
            filename=f"correlation_matrix_{year_range[0]}-{year_range[1]}.csv"
        )

# ==================================================
# FOOTER
# ==================================================
st.divider()
st.caption(f"Deep Dive Analysis | {analysis_type} | {len(filtered_df)} records analyzed")
