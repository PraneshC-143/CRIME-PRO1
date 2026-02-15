import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Function to plot top districts based on crime count

def plot_top_districts(data, top_n=10):
    top_districts = data['district'].value_counts().nlargest(top_n)
    plt.figure(figsize=(10, 6))
    sns.barplot(x=top_districts.index, y=top_districts.values)
    plt.title('Top Districts by Crime Count')
    plt.xlabel('District')
    plt.ylabel('Number of Crimes')
    plt.xticks(rotation=45)
    plt.show()

# Function to plot crime trend over time

def plot_crime_trend(data):
    crime_trend = data.groupby('date').size()
    plt.figure(figsize=(10, 6))
    plt.plot(crime_trend.index, crime_trend.values)
    plt.title('Crime Trend Over Time')
    plt.xlabel('Date')
    plt.ylabel('Number of Crimes')
    plt.xticks(rotation=45)
    plt.show()

# Function to plot crime distribution

def plot_distribution(data, column):
    plt.figure(figsize=(10, 6))
    sns.histplot(data[column], bins=30, kde=True)
    plt.title(f'Distribution of {column}')
    plt.xlabel(column)
    plt.ylabel('Frequency')
    plt.show()

# Function to plot correlation heatmap

def plot_correlation_heatmap(data):
    plt.figure(figsize=(10, 8))
    correlation_matrix = data.corr()
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('Correlation Heatmap')
    plt.show()

# Function to plot heatmap by district

def plot_heatmap_by_district(data):
    heatmap_data = data.pivot_table(index='district', columns='crime_type', values='count', fill_value=0)
    plt.figure(figsize=(12, 8))
    sns.heatmap(heatmap_data, annot=True, cmap='Blues')
    plt.title('Heatmap of Crimes by District')
    plt.show()

# Function to plot crime hotspots

def plot_crime_hotspots(data):
    fig = px.density_mapbox(data, lat='latitude', lon='longitude', z='count', radius=10,
                            center=dict(lat=data['latitude'].mean(), lon=data['longitude'].mean()),
                            mapbox_style='open-street-map', zoom=10)
    fig.update_layout(title='Crime Hotspots')
    fig.show()