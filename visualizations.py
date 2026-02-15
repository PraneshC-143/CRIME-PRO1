import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import pandas as pd


def plot_top_districts(data, top_n=10):
    """Plot top districts by total crime count"""
    district_crimes = data.groupby('district_name')['crime_sum'].sum().nlargest(top_n).sort_values()
    
    fig = px.bar(
        x=district_crimes.values,
        y=district_crimes.index,
        orientation='h',
        title=f'Top {top_n} Districts by Crime Count',
        labels={'x': 'Total Crimes', 'y': 'District'},
        color=district_crimes.values,
        color_continuous_scale='Reds'
    )
    fig.update_layout(showlegend=False, height=500)
    return fig


def plot_crime_trend(data, crime_types):
    """Plot crime trend over time"""
    yearly_data = data.groupby('year')[crime_types].sum()
    
    fig = go.Figure()
    for crime in crime_types:
        fig.add_trace(go.Scatter(
            x=yearly_data.index,
            y=yearly_data[crime],
            mode='lines+markers',
            name=crime
        ))
    
    fig.update_layout(
        title='Crime Trend Over Years',
        xaxis_title='Year',
        yaxis_title='Number of Crimes',
        hovermode='x unified',
        height=500
    )
    return fig


def plot_distribution(data, crime_types):
    """Plot distribution of crime types"""
    crime_totals = data[crime_types].sum().sort_values(ascending=False)
    
    fig = px.pie(
        values=crime_totals.values,
        names=crime_totals.index,
        title='Distribution of Crime Types',
        hole=0.4
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=500)
    return fig


def plot_correlation_heatmap(data, crime_types):
    """Plot correlation heatmap of crime types"""
    if len(crime_types) < 2:
        st.warning("Need at least 2 crime types for correlation")
        return None
    
    corr_matrix = data[crime_types].corr()
    
    fig = px.imshow(
        corr_matrix,
        text_auto='.2f',
        aspect='auto',
        title='Crime Type Correlation Heatmap',
        color_continuous_scale='RdBu_r',
        zmin=-1,
        zmax=1
    )
    fig.update_layout(height=600)
    return fig


def plot_heatmap_by_district(data, crime_types):
    """Plot heatmap of crimes by district"""
    top_districts = data.groupby('district_name')['crime_sum'].sum().nlargest(15).index
    district_data = data[data['district_name'].isin(top_districts)]
    
    heatmap_data = district_data.groupby('district_name')[crime_types].sum()
    
    fig = px.imshow(
        heatmap_data.T,
        labels=dict(x='District', y='Crime Type', color='Count'),
        title='Crime Heatmap: Top 15 Districts',
        aspect='auto',
        color_continuous_scale='YlOrRd'
    )
    fig.update_layout(height=600)
    return fig


def plot_crime_hotspots(data, crime_types):
    """Plot geographic distribution of crimes"""
    district_crimes = data.groupby(['state_name', 'district_name'])[crime_types].sum().sum(axis=1).reset_index()
    district_crimes.columns = ['State', 'District', 'Total_Crimes']
    district_crimes = district_crimes.sort_values('Total_Crimes', ascending=False).head(20)
    
    fig = px.treemap(
        district_crimes,
        path=['State', 'District'],
        values='Total_Crimes',
        title='Crime Hotspots: Geographic Distribution',
        color='Total_Crimes',
        color_continuous_scale='Reds'
    )
    fig.update_layout(height=600)
    return fig
