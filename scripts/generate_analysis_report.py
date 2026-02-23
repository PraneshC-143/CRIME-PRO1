import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime

# Optional ML for predictive analysis if scikit-learn is available
try:
    from sklearn.linear_model import LinearRegression
    has_sklearn = True
except ImportError:
    has_sklearn = False

def run_analysis_and_generate_html():
    print("Starting specialized analysis for CrimeScope...")
    
    # 1. Dataset Analysis & Preprocessing
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "districtwise-ipc-crimes.xlsx")
    
    if not os.path.exists(data_path):
        print(f"Error: Could not find data file at {data_path}")
        return
        
    print("Loading dataset...")
    df = pd.read_excel(data_path, sheet_name="districtwise-ipc-crimes")
    
    # Preprocessing
    cols_to_drop = ["id", "state_code", "district_code"]
    df.drop(columns=[col for col in cols_to_drop if col in df.columns], inplace=True)
    df["year"] = df["year"].astype(int)
    
    crime_cols = df.select_dtypes(include="number").columns.drop("year", errors='ignore')
    df[crime_cols] = df[crime_cols].fillna(0)
    df["total_crimes"] = df[crime_cols].sum(axis=1)
    
    # 2. Statistical Analysis
    print("Performing statistical analysis...")
    yearly_totals = df.groupby("year")["total_crimes"].sum().reset_index()
    
    # YoY Growth
    yearly_totals["yoy_growth"] = yearly_totals["total_crimes"].pct_change() * 100
    
    # State-wise severity
    state_totals = df.groupby("state_name")["total_crimes"].sum().sort_values(ascending=False).reset_index()
    top_states = state_totals.head(5)
    
    # Dominant crime type overall
    crime_totals = df[crime_cols].sum().sort_values(ascending=False).reset_index()
    crime_totals.columns = ["Crime Type", "Total"]
    top_crimes = crime_totals.head(5)
    
    # 3. Predictive Analysis (Simple linear regression or moving average)
    print("Running predictive analysis for 2024...")
    years = yearly_totals["year"].values
    totals = yearly_totals["total_crimes"].values
    
    prediction_2024 = 0
    prediction_method = "Simple Moving Average"
    
    if has_sklearn and len(years) >= 3:
        model = LinearRegression()
        model.fit(years.reshape(-1, 1), totals)
        predicted_vals = model.predict(np.array([[2024]]))
        prediction_2024 = int(max(0, predicted_vals[0]))
        prediction_method = "Linear Regression"
        trend_status = "Increasing" if model.coef_[0] > 0 else "Decreasing"
    else:
        # Fallback to moving average of last 3 years
        if len(totals) >= 3:
            prediction_2024 = int(np.mean(totals[-3:]))
        else:
            prediction_2024 = int(np.mean(totals)) if len(totals) > 0 else 0
        trend_status = "Unknown"
        if len(totals) >= 2:
            trend_status = "Increasing" if totals[-1] > totals[-2] else "Decreasing"

    # 4. Generate HTML Report
    print("Generating HTML report...")
    
    # Format the stats for HTML insertion
    top_states_html = ""
    for _, row in top_states.iterrows():
        top_states_html += f'''
        <div class="flex items-center justify-between py-2 border-b border-white/10 last:border-0">
            <span class="text-sm font-medium">{row["state_name"]}</span>
            <span class="text-sm font-bold text-red-400">{int(row["total_crimes"]):,}</span>
        </div>
        '''
        
    top_crimes_html = ""
    for _, row in top_crimes.iterrows():
        top_crimes_html += f'''
        <div class="flex items-center justify-between py-2 border-b border-white/10 last:border-0">
            <span class="text-sm font-medium capitalize">{str(row["Crime Type"]).replace('_', ' ')}</span>
            <span class="text-sm font-bold text-orange-400">{int(row["Total"]):,}</span>
        </div>
        '''
        
    yearly_html = ""
    for _, row in yearly_totals.iterrows():
        yoy = row["yoy_growth"]
        yoy_str = f'<span class="text-{"red" if yoy > 0 else "emerald"}-400 font-medium">{"▴" if yoy > 0 else "▾"} {abs(yoy):.1f}%</span>' if pd.notna(yoy) else '<span class="text-gray-500">-</span>'
        
        yearly_html += f'''
        <tr class="hover:bg-white/5 transition-colors">
            <td class="px-4 py-3 text-sm">{int(row["year"])}</td>
            <td class="px-4 py-3 text-sm font-bold">{int(row["total_crimes"]):,}</td>
            <td class="px-4 py-3 text-sm">{yoy_str}</td>
        </tr>
        '''

    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>CrimeScope | Detailed Analysis Report</title>
    
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

    <!-- Tailwind -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    fontFamily: {{ sans: ['Inter', 'ui-sans-serif', 'system-ui'] }},
                    boxShadow: {{
                        glow: '0 10px 35px rgba(220,38,38,0.18), 0 0 0 1px rgba(255,255,255,0.06) inset',
                        glass: '0 12px 40px rgba(0,0,0,0.28)'
                    }}
                }}
            }}
        }}
    </script>

    <style>
        :root {{
            --bg0: #070A1A;
            --bg1: #0B1026;
            --text: rgba(255, 255, 255, .86);
            --muted: rgba(255, 255, 255, .66);
            --stroke: rgba(255, 255, 255, .12);
            --stroke2: rgba(255, 255, 255, .18);
        }}
        body {{
            font-family: 'Inter', sans-serif;
            color: var(--text);
            background: linear-gradient(180deg, var(--bg0), var(--bg1));
            min-height: 100vh;
        }}
        .glass {{
            background: linear-gradient(135deg, rgba(255, 255, 255, .05), rgba(255, 255, 255, .02));
            border: 1px solid var(--stroke);
            backdrop-filter: blur(14px);
            border-radius: 1.5rem;
        }}
        .brand-text {{
            background: linear-gradient(to right, #fca5a5, #ef4444);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
    </style>
</head>
<body class="p-6 md:p-12">
    <div class="max-w-7xl mx-auto">
        
        <!-- Header -->
        <header class="flex flex-col md:flex-row items-start md:items-center justify-between mb-8 pb-6 border-b border-white/10">
            <div>
                <h1 class="text-3xl font-bold tracking-tight brand-text">Crime Data Analysis Report</h1>
                <p class="text-sm mt-2 text-white/60">Automated Statistical & Predictive Insights (Generated on {datetime.now().strftime("%Y-%m-%d %H:%M")})</p>
            </div>
            <div class="mt-4 md:mt-0">
                <a href="index.html" class="inline-flex items-center gap-2 bg-white/10 hover:bg-white/15 border border-white/20 px-4 py-2 rounded-xl transition-all font-medium text-sm text-white/90">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
                    Back to Dashboard
                </a>
            </div>
        </header>

        <!-- Top Insights -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div class="glass p-6 shadow-glow">
                <h3 class="text-sm font-semibold text-white/50 uppercase tracking-wider">Total Crimes Recorded</h3>
                <div class="text-4xl font-bold mt-2 text-white/90">{int(yearly_totals["total_crimes"].sum()):,}</div>
                <p class="text-xs text-white/40 mt-3">From {df["year"].min()} to {df["year"].max()}</p>
            </div>
            
            <div class="glass p-6 text-center">
                <h3 class="text-sm font-semibold text-white/50 uppercase tracking-wider">2024 Prediction</h3>
                <div class="text-4xl font-bold mt-2 text-red-400">{prediction_2024:,}</div>
                <p class="text-xs text-white/40 mt-3">Using {prediction_method}</p>
            </div>
            
            <div class="glass p-6">
                <h3 class="text-sm font-semibold text-white/50 uppercase tracking-wider">Overall Trend</h3>
                <div class="flex items-center gap-3 mt-2">
                    <div class="text-4xl font-bold {"text-red-400" if trend_status == "Unknown" or trend_status == "Increasing" else "text-emerald-400"}">
                        {trend_status}
                    </div>
                    {"""<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-red-400"><path d="M23 6l-9.5 9.5-5-5L1 18"/></svg>""" if trend_status == "Unknown" or trend_status == "Increasing" else """<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-emerald-400"><path d="M23 18l-9.5-9.5-5 5L1 6"/></svg>"""}
                </div>
            </div>
        </div>

        <!-- Detailed Breakdown -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            
            <!-- Left Column -->
            <div class="space-y-6">
                <div class="glass p-6">
                    <h2 class="text-lg font-bold mb-4 flex items-center gap-2">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
                        Most Impacted States
                    </h2>
                    <div class="flex flex-col">
                        {top_states_html}
                    </div>
                </div>

                <div class="glass p-6">
                    <h2 class="text-lg font-bold mb-4 flex items-center gap-2">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20v-6M6 20V10M18 20V4"/></svg>
                        Dominant Crime Categories
                    </h2>
                    <div class="flex flex-col">
                        {top_crimes_html}
                    </div>
                </div>
            </div>

            <!-- Right Column -->
            <div class="glass p-6">
                <h2 class="text-lg font-bold mb-4">Historical Year-over-Year Growth</h2>
                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse">
                        <thead>
                            <tr class="border-b border-white/20 text-white/50 text-xs uppercase tracking-wider">
                                <th class="px-4 py-3 font-semibold">Year</th>
                                <th class="px-4 py-3 font-semibold">Total Crimes</th>
                                <th class="px-4 py-3 font-semibold">YoY Change</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-white/10">
                            {yearly_html}
                        </tbody>
                    </table>
                </div>
                
                <div class="mt-6 pt-6 border-t border-white/10">
                    <h3 class="text-sm font-semibold text-white/50 mb-3">Model Information</h3>
                    <p class="text-sm text-white/70 leading-relaxed text-justify">
                        Data preprocessing dropped missing values and identifier columns (e.g., state_code, district_code). 
                        Numerical features corresponding to crime categories were aggregated to measure gross occurrences per locale. 
                        The predictive projection leverages '{prediction_method}' based on historical frequency records.
                    </p>
                </div>
            </div>

        </div>
    </div>
</body>
</html>'''

    output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "CrimeScope-Web", "analysis.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"Successfully written analysis report to {output_path}")

if __name__ == "__main__":
    run_analysis_and_generate_html()
