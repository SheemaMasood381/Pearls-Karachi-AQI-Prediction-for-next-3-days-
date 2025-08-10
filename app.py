
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import streamlit as st
from src.predict import predict_next_3_days
from datetime import datetime, timedelta
import plotly.io as pio
import plotly.express as px
from src.create_lime import generate_lime


# ------------------------------
# Background (Light Overlay)
# ------------------------------
# Set page config
st.set_page_config(layout="wide", page_title="Pearls' Karachi AQI Predictor", page_icon="📍")

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("https://static.vecteezy.com/system/resources/thumbnails/017/648/539/small_2x/karachi-pakistan-city-map-in-retro-style-in-golden-color-outline-map-vector.jpg");
        
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    .main > div {{
        background-color: rgba(255, 255, 255, 0.5);
        padding: 3rem;
        border-radius: 10px;
    }}

    /* Global text color override */
    html, body, [class*="css"] {{
        color: black !important;
    }}

    /* Metric label (pollutant names) styling */
    [data-testid="stMetricLabel"] > div {{
        color: black !important;
        font-weight: 1000 !important;
        font-size: 2.0rem !important;  /* increase size */}}

    /* Reduce spacing between pollutant label and value */
    [data-testid="stMetric"] {{
        padding: 0rem !important;
        margin-bottom: 1rem !important;
    }}


    /* Metric value styling */
    [data-testid="stMetricValue"] > div {{
        color: black !important;
        font-weight: 500 !important;
        font-size: 1.5rem !important;
    }}

    </style>
    """,
    unsafe_allow_html=True
)

# ------------------------------
# Header
# ------------------------------
st.markdown(
    """
    <div style='text-align: center; color: black; margin-top: -0.1rem; margin-bottom: -0.1rem;'>
        <h1 style='margin: -0.1;'>📍 Pearls' Karachi Air Quality Index</h1>
        <hr style='border: 3px double black; width: 60%; margin: -0.1rem auto 0;'>
    </div>
    """,
    unsafe_allow_html=True
)

pio.templates.default = "plotly_white"
# ------------------------------
# Load data
# ------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("processed_data/daily_karachi_preprocessed.csv")
    df["date"] = pd.to_datetime(df["date"])
    return df

df = load_data()
# ------------------------------
# Create tabs
#--------------------------

# Inject CSS to customize tab font/color/size
st.markdown("""
<style>
/* Center the tab list */
div[data-baseweb="tab-list"] {
    justify-content: center !important;
}

/* Style each tab */
button[data-baseweb="tab"] {
    font-size: 32px !important;     /* Bigger font size */
    color: black !important;        /* Black font color */
    font-weight: bold !important;   /* Bold text */
    font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)


# Create tabs
tabs = st.tabs(["📊 Overview", "📈 AQI Trends", "💨 Pollutants & Lime Features Contributions", "🧠 General Insights", "🕒 Logs"])

# ----------- =====
# TAB 0: Overview 
# ----------------
with tabs[0]:
    latest_row = df.sort_values("date").iloc[-1]
    forecast_df = predict_next_3_days()

    st.markdown(f"<h3 style='text-align: center; color: black;'>Date: {latest_row['date'].strftime('%d %B %Y')}</h3>", unsafe_allow_html=True)

    col1, col2 = st.columns([1.5, 2])

    with col1:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=latest_row['AQI'],
            title={'text': "Current AQI", 'font': {'size': 30, 'color': 'black'}},
            gauge={
                'axis': {'range': [0, 500], 'tickwidth': 3, 'tickcolor': "black"},
                'bar': {'color': "seagreen"},
                'steps': [
                    {'range': [0, 50], 'color': "#58f3de"},
                    {'range': [51, 100], 'color': "#8ae467"},
                    {'range': [101, 150], 'color': "#ecc757"},
                    {'range': [151, 200], 'color': "#f3a571"},
                    {'range': [201, 300], 'color': "#f17c7c"},
                    {'range': [301, 500], 'color': "#f873fa"},
                ],
            }
        ))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "black"}, margin=dict(t=1, b=1))
        st.plotly_chart(fig, use_container_width=True)

    def get_aqi_category_message(aqi):
        if aqi <= 50:
            return "🌿 The air is fresh and healthy. It's a great day to be outdoors!"
        elif aqi <= 100:
            return "😊 Air quality is acceptable, but a few pollutants may be a concern for some sensitive individuals."
        elif aqi <= 150:
            return "😐 The air is a bit polluted. People with respiratory issues should limit outdoor activity."
        elif aqi <= 200:
            return "😷 Unhealthy for sensitive groups — avoid strenuous activities outdoors."
        elif aqi <= 300:
            return "🚫 The air is unhealthy. It's best to stay indoors if possible."
        else:
            return "☠️ Hazardous air quality! Everyone should avoid outdoor exposure."

    aqi_message = get_aqi_category_message(latest_row["AQI"])
    st.markdown(f"""
    <div style='
        background-color: #f0f0f0;
        padding: -0.2rem;
        border: 1px solid #888;
        border-radius: 12px;
        margin-top: -0.5rem;
        font-size: 2.0rem;
        color: black;
        font-weight: 600;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
    '>
        {aqi_message}
    </div>
    """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div style='text-align: center;'>
                <h2 style='
                    color: black;
                    font-weight: 700;
                    margin-top: -0.2rem;
                    margin-bottom: -0.3rem;
                '>
                    📋 Today's Pollutants & Weather
                </h2>
            </div>
        """, unsafe_allow_html=True)

        pollutants = ["PM2.5", "PM10", "NO2", "SO2", "O3", "CO","Temperature", "Humidity", "Precipitation"]
        metrics_per_row = 3
        for i in range(0, len(pollutants), metrics_per_row):
            cols = st.columns(metrics_per_row)
            for j in range(metrics_per_row):
                if i + j < len(pollutants):
                    col = cols[j]
                    label = pollutants[i + j]
                    value = latest_row[label]
                    unit = (
                        " µg/m³" if label in ["PM2.5", "PM10", "NO2", "SO2", "CO", "O3"]
                        else "%" if label == "Humidity"
                        else "°C" if label == "Temperature"
                        else "mm"
                    )
                    col.markdown(
                        f"""
                        <div style='text-align: center; padding: 0.2rem 0;'>
                            <div style='font-size: 1.6rem; font-weight: 700; color: black;'>{label}</div>
                            <div style='font-size: 1.4rem; font-weight: 500; color: black; margin-top: 0.2rem;'>{value:.1f}{unit}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

    st.markdown("<hr style='border: 1px solid black;'>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: black;'>|| Next 3-Day AQI Forecast||</h1>", unsafe_allow_html=True)
    forecast_cols = st.columns(3)

    def get_aqi_category_name(aqi):
        if aqi <= 50:
            return "🌿 Very Good"
        elif aqi <= 100:
            return "😊 Good"
        elif aqi <= 150:
            return "😐 Moderate"
        elif aqi <= 200:
            return "😷 Unhealthy for Sensitive"
        elif aqi <= 300:
            return "🚫 Unhealthy"
        else:
            return "☠️ Hazardous"

    for i, col in enumerate(forecast_cols):
        date = pd.to_datetime(forecast_df.loc[i, "Date"]).strftime("%d %b %Y")
        aqi_value = forecast_df.loc[i, "Predicted_AQI"]
        category = get_aqi_category_name(aqi_value)
        col.markdown(f"""
            <div style='
                background-color: #ffffffaa;
                padding: 1.2rem;
                border-radius: 12px;
                border: 2px solid #888;
                text-align: center;
                box-shadow: 2px 2px 6px rgba(0,0,0,0.1);
            '>
                <div style='font-size: 2rem; font-weight: 600;color :black;'>{date}</div>
                <div style='font-size: 3rem; font-weight: bold; color: black;'>{aqi_value:.0f}</div>
                <div style='font-size: 1.5rem;font-weight: bold; color: black;'>{category}</div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("<hr style='border: 1px solid black;'>", unsafe_allow_html=True)

# ----------- 
# TAB 1: AQI Trends 
# ----------- 

with tabs[1]:
    st.markdown(f"<h1 style='text-align: center; color: black;'>||Karachi AQI & Pollutants Over Time||</h1>", unsafe_allow_html=True)

    # -------------------------
    # Time Filter Title Styling
    # -------------------------
    st.markdown("""
        <style>
            .title-center {
                text-align: center;
                font-size: 24px;
                font-weight: bold;
                color: black;
                margin-bottom: 20px;
            }
            .stButton > button {
                background-color: white;
                color: black;
                font-size: 16px !important;
                font-weight: bold;
                width: 100%;
                border: 1px solid #cccccc;
            }
            .stButton > button:hover {
                background-color: #f0f0f0;
            }
        </style>
    """, unsafe_allow_html=True)

    # -------------------------
    # Title
    # -------------------------
    st.markdown('<div class="title-center">📈 Select Time Range</div>', unsafe_allow_html=True)

    # -------------------------
    # Time Filter Buttons
    # -------------------------
    col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1])
    time_filter = None

    with col1:
        if st.button("7 Days"):
            time_filter = 7
    with col2:
        if st.button("Last Month"):
            time_filter = 30
    with col3:
        if st.button("90 Days"):
            time_filter = 90
    with col4:
        if st.button("6 Months"):
            time_filter = 180
    with col5:
        if st.button("Last Year"):
            time_filter = 365
    with col6:
        if st.button("All Data"):
            time_filter = None  # No filter — show all data

    #-------
    latest_date = df["date"].max()

    if time_filter:
        filtered_df = df[df["date"] >= latest_date - pd.Timedelta(days=time_filter)]
    else:
        filtered_df = df.copy()

    # Create the figure
    fig = go.Figure()

    # AQI Limit Bands (source: EPA)
    aqi_bands = [
        {"min": 0, "max": 50, "color": "#00e400",'label': 'Good'},
        {"min": 51, "max": 100, "color": "#ffff00", 'label': 'Moderate'},
        {"min": 101, "max": 150, "color": "#ff7e00", 'label': 'Unhealthy for Sensitive Groups'},
        {"min": 151, "max": 200, "color": "#ff0000", 'label': 'Unhealthy'},
        {"min": 201, "max": 300, "color": "#8f3f97", 'label': 'Very Unhealthy'},
        {"min": 301, "max": 500, "color": "#7e0023", 'label': 'Hazardous'},
    ]

    
    for band in aqi_bands:
        fig.add_shape(
            type="rect",
            xref="paper",  # span entire x-axis
            yref="y",
            x0=0,
            x1=1,
            y0=band['min'],
            y1=band['max'],
            fillcolor=band['color'],
            opacity=0.1,
            layer="below",
            line_width=0,
        )
        fig.add_annotation(
            xref="paper",
            yref="y",
            x=1.01,
            y=(band['min'] + band['max']) / 2,
            text=band['label'],
            showarrow=False,
            font=dict(color=band['color'], size=12),
            bgcolor="rgba(255,255,255,0.6)"
        )

    # Add AQI line chart
    fig.add_trace(go.Scatter(
        x=filtered_df["date"],
        y=filtered_df["AQI"],
        mode="lines+markers",
        line=dict(color="#3a0ca3", width=4),
        marker=dict(size=6),
        name="AQI"
    ))

    # ✅ Update layout with plotly_white template
    fig.update_layout(
        template="plotly_white",  # ✅ Force white theme
        height=800,
        title=dict(
            text="📈 AQI Trends Over Time",
            font=dict(size=24, color="black"),
            x=0.5
        ),
        xaxis=dict(
            title=dict(text="Date", font=dict(color="black", size=18)),
            showgrid=True,
            gridcolor="lightgrey",
            tickfont=dict(color="black")
        ),
        yaxis=dict(
            title=dict(text="Air Quality Index (AQI)", font=dict(color="black", size=18)),
            showgrid=True,
            gridcolor="lightgrey",
            tickfont=dict(color="black"),
            range=[0, 500]
        ),
        font=dict(
            family="Arial",
            size=16,
            color="black"
        ),
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(t=60, b=40, l=60, r=30),
        hoverlabel=dict(
            font=dict(color='black', size=14),
            bgcolor="white"
        )
    )

    # Show in Streamlit
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("<hr style='border: 1px solid black;'>", unsafe_allow_html=True)

    # --------------------------------------
    # 💨 Pollutants Over Time (Multi-line)
    # ------------------------------------
     # -------------------------
    # CSS for Title + Buttons
    # -------------------------
    st.markdown("""
        <style>
            .title-center {
                text-align: center;
                font-size: 24px;
                font-weight: bold;
                color: black;
                margin-bottom: 20px;
            }
            .stButton > button {
                background-color: white;
                color: black;
                font-size: 16px !important;
                font-weight: bold;
                width: 100%;
                border: 1px solid #cccccc;
            }
            .stButton > button:hover {
                background-color: #f0f0f0;
            }
        </style>
    """, unsafe_allow_html=True)

    # -------------------------
    # View Mode Title
    # -------------------------
    st.markdown('<div class="title-center">💨 View Pollutants as Concentration or Percentage</div>', unsafe_allow_html=True)

    # -------------------------
    # Pollutant View Mode Buttons
    # -------------------------
    col1, col2 = st.columns([1, 1])
    view_mode = "Concentration (μg/m³)"  # default

    with col1:
        if st.button("Concentration (μg/m³)"):
            view_mode = "Concentration (μg/m³)"
    with col2:
        if st.button("Percentage (%)"):
            view_mode = "Percentage (%)"

    pollutants = ['PM2.5', 'PM10', 'NO2', 'O3', 'CO', 'SO2']

    if view_mode == "Concentration (μg/m³)":
        fig = px.line(df, x="date", y=pollutants,
                      labels={"value": "Concentration (μg/m³)", "variable": "Pollutant", "date": "Date"},
                      title="Pollutant Concentrations Over Time")

    else:  # Percentage view
        df_pct = df.copy()
        df_pct["Total"] = df_pct[pollutants].sum(axis=1)
        for col in pollutants:
            df_pct[col] = (df_pct[col] / df_pct["Total"]) * 100

        fig = px.line(df_pct, x="date", y=pollutants,
                      labels={"value": "Percentage (%)", "variable": "Pollutant", "date": "Date"},
                      title="Pollutant Percentage Contribution Over Time")

    
    # Apply black color to all text elements
    if view_mode == "Concentration (μg/m³)":
        fig = px.line(
            df,
            x="date",
            y=pollutants,
            labels={"value": "Concentration (μg/m³)", "variable": "Pollutant", "date": "Date"},
            title="Pollutant Concentrations Over Time"
        )

    else:  # Percentage view
        df_pct = df.copy()
        df_pct["Total"] = df_pct[pollutants].sum(axis=1)
        for col in pollutants:
            df_pct[col] = (df_pct[col] / df_pct["Total"]) * 100

        fig = px.line(
            df_pct,
            x="date",
            y=pollutants,
            labels={"value": "Percentage (%)", "variable": "Pollutant", "date": "Date"},
            title="Pollutant Percentage Contribution Over Time"
        )

    # ✅ Apply font and axis color styling here
    fig.update_layout(
        template="plotly_white",
        height=800,
        paper_bgcolor="white",
        plot_bgcolor="white",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.12,
            xanchor="right",
            x=1,
            font=dict(
                size=20,
                color="black"
            )),
        title=dict(
            font=dict(size=24, color="black"),
            x=0.5
        ),
        xaxis=dict(
            title=dict(text="Date", font=dict(color="black", size=24)),
            tickfont=dict(color="black")
        ),
        yaxis=dict(
            title=dict(
                text="Concentration (μg/m³)" if view_mode == "Concentration (μg/m³)" else "Percentage (%)",
                font=dict(color="black", size=24)
            ),
            tickfont=dict(color="black")
        ),
        font=dict(color="black")
    )

    fig.update_traces(line=dict(width=2))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("<hr style='border: 1px solid black;'>", unsafe_allow_html=True)
    
# -------------------
# TAB 2: Pollutants 
# --------------------- #
with tabs[2]:
    st.markdown(f"<h1 style='text-align: center; color: black;'>||Pollutants Contributions||</h1>", unsafe_allow_html=True)

    # Load data and define pollutants
    df = load_data()
    pollutants = ['PM2.5', 'PM10', 'NO2', 'O3', 'CO', 'SO2']

    # WHO safe limits
    who_limits = pd.Series({
        'PM2.5': 15,
        'PM10': 45,
        'NO2': 25,
        'O3': 100,
        'CO': 4000,
        'SO2': 40
    })

    # Prepare Karachi average and risk ratio
    karachi_avg = df[pollutants].mean()
    karachi_ratio = karachi_avg / who_limits
    who_ratio = pd.Series([1.0] * len(pollutants), index=pollutants)

    # Radar chart values
    karachi_plot = karachi_ratio.tolist() + [karachi_ratio.tolist()[0]]
    who_plot = who_ratio.tolist() + [who_ratio.tolist()[0]]
    pollutants_labels = pollutants + [pollutants[0]]

    # Create radar chart
    radar_fig = go.Figure()
    radar_fig.add_trace(go.Scatterpolar(
        r=karachi_plot,
        theta=pollutants_labels,
        fill='toself',
        name='Karachi Avg / WHO',
        line_color='crimson'
    ))
    radar_fig.add_trace(go.Scatterpolar(
        r=who_plot,
        theta=pollutants_labels,
        fill='toself',
        name='WHO Safe Limit',
        line_color='seagreen'
    ))
    radar_fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, max(karachi_ratio.max(), 1.5)], tickfont_color='black'),
            angularaxis=dict(tickfont_color='black')
        ),
        template="plotly_white",
        height=800,
        paper_bgcolor="white",
        plot_bgcolor="white",
        title=dict(text="📊 Risk Ratio (Karachi Pollutants Avg vs WHO)", font=dict(size=24, color="black")),
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.12, xanchor="right", x=1,
            font=dict(size=20, color="black")
        )
    )
    # Define darker custom colors for pollutants
    custom_colors = {
    'PM2.5': "#B80606",
    'PM10': "#cf0000eb",
    'NO2': "#ce0606",
    'O3': "#e61919",
    'CO': "#770d0d",
    'SO2': "#f77474"  
    }


    # Pie chart for average composition
    pie_fig = px.pie(values=karachi_avg, names=pollutants,color=pollutants,
                     title="Overall Karachi Pollutant Composition (Avg)",
                     color_discrete_map=custom_colors,
                     hole=0.2)
    pie_fig.update_layout(title_font_color="black", title_font_size=20,height=800,
                          legend=dict(orientation="h", yanchor="bottom", y=-0.12, xanchor="right", x=1,
                                      font=dict(color='black', size=20)),
                          font=dict(color="black"), paper_bgcolor="white")

    # Display side-by-side
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(pie_fig, use_container_width=True)
    with col2:
        st.plotly_chart(radar_fig, use_container_width=True)

    # Divider
    st.markdown("<hr style='border: 1px solid black;'>", unsafe_allow_html=True)

    # ================== LIME Explanation ==================
    st.markdown("<h1 style='text-align: center; color: black;'>|| LIME Features' Contributions||</h1", unsafe_allow_html=True)
    html_path, csv_path, png_path = generate_lime()

    lime_df = pd.read_csv(csv_path)

        # Plotly Horizontal Bar for LIME
    fig_lime = px.bar(
        lime_df,
        x="Contribution",
        y="Feature",
        orientation="h",
        color="Contribution",
        color_continuous_scale=px.colors.diverging.RdBu,
        title="LIME Features' Contributions",
     )

    # ✅ Apply same styling as reference chart
    fig_lime.update_layout(
        template="plotly_white",
        height=800,
        paper_bgcolor="white",
        plot_bgcolor="white",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.12,
            xanchor="right",
            x=1,
            font=dict(size=24, color="black")
        ),
        title=dict(
            font=dict(size=24, color="black"),
            x=0.5
        ),
        xaxis=dict(
            title=dict(text="Contribution to Prediction", font=dict(color="black", size=24)),
            tickfont=dict(color="black")
        ),
        yaxis=dict(
            title=dict(text="Feature", font=dict(color="black", size=24)),
            tickfont=dict(color="black")
        ),
        font=dict(color="black")
    )
    st.plotly_chart(fig_lime, use_container_width=True)

        # Download buttons
    st.download_button("📄 Download LIME CSV", data=open(csv_path, "rb"), file_name="lime_explanation.csv")
    st.download_button("🌐 View Full HTML", data=open(html_path, "rb"), file_name="lime_explanation.html")

#-----------
# Tab 3: General INsights
# -----------
with tabs[3]:
    st.markdown("<h1 style='text-align: center; color: black;'>🧠 General Insights</h1>", unsafe_allow_html=True)

    # ========== PRE-CALCULATE values before using ==========
    df['weekday'] = df['date'].dt.weekday
    df['is_weekend'] = df['weekday'].isin([5, 6])
    weekend_aqi = df.groupby('is_weekend')['AQI'].mean()
    weekday_aqi_val = round(weekend_aqi[False], 2)
    weekend_aqi_val = round(weekend_aqi[True], 2)

    def get_season(month):
        if month in [12, 1, 2]: return 'Winter'
        elif month in [3, 4, 5]: return 'Spring'
        elif month in [6, 7, 8]: return 'Summer'
        else: return 'Autumn'

    df['season'] = df['date'].dt.month.map(get_season)
    seasonal_aqi = df.groupby('season')['AQI'].mean().sort_values()
    worst_season = seasonal_aqi.idxmax()
    worst_season_aqi = round(seasonal_aqi.max(), 2)

    extreme_days = df[df['AQI'] > 150]
    exceed_pct = round((df['AQI'] > 100).mean() * 100, 2)
    exceed_count = (df['AQI'] > 100).sum()

    worst_day = df.loc[df['AQI'].idxmax()]
    most_critical_pollutant = df.drop(columns=['date', 'AQI', 'weekday', 'is_weekend', 'season']).mean().idxmax()
    most_critical_pollutant_val = round(df[most_critical_pollutant].mean(), 2)

    with st.container():
        col1, col2, col3, col4, col5 = st.columns(5)

        card_style = "padding: 15px; border-radius: 12px; text-align: center; min-height: 180px; height: 100%;"

        with col1:
            st.markdown(f"""
                <div style="background-color: #e6f7ff; {card_style}">
                    <h5 style="color: #005580;">📆 Weekday vs Weekend</h5>
                    <p style="font-size: 15px; color: black;">
                        <b>Weekday AQI:</b> {weekday_aqi_val}<br>
                        <b>Weekend AQI:</b> {weekend_aqi_val}<br><br>
                        <i style="font-size:13px;">Almost equal</i>
                    </p>
                </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
                <div style="background-color: #fff0e6; {card_style}">
                    <h5 style="color: #b35900;">❄️ Worst Season</h5>
                    <p style="font-size: 20px; color: black;">
                        <b>{worst_season}</b><br>(AQI {worst_season_aqi})
                    </p>
                </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
                <div style="background-color: #ffe6cc; {card_style}">
                    <h5 style="color: #994d00;">🚨 Worst Day</h5>
                    <p style="font-size: 14px; line-height: 1.4; color: black;">
                        <b>Date:</b> {worst_day['date'].strftime('%d %b %Y')}<br>
                        <b>AQI:</b> {round(worst_day['AQI'], 2)}<br>
                        <b>PM2.5:</b> {round(worst_day['PM2.5'], 2)}<br>
                        <b>PM10:</b> {round(worst_day['PM10'], 2)}
                    </p>
                </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
                <div style="background-color: #e6ffe6; {card_style}">
                    <h5 style="color: #267326;">💨 Most Critical Pollutant</h5>
                    <p style="font-size: 16px; color: black;">
                        <b>{most_critical_pollutant}</b><br>(Avg: {most_critical_pollutant_val} μg/m³)
                    </p>
                </div>
            """, unsafe_allow_html=True)

        with col5:
            st.markdown(f"""
                <div style="background-color: #f9e6ff; {card_style}">
                    <h5 style="color: #800080;">⚠️ Above WHO Limit</h5>
                    <p style="font-size: 16px; color: black;">
                        <b>{exceed_count} days</b><br>
                        ({exceed_pct}% of total)<br><br>
                        AQI > 100
                    </p>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<hr style='border: 1px solid black;'>", unsafe_allow_html=True)


# --------------------
# Tab 4: 🕒 Logs
# ----------------------
with tabs[4]:
    st.markdown(f"<h2 style='text-align: center; color: black;'>|| Pipeline Logs & Meta Data ||</h2>", unsafe_allow_html=True)
    
    log_path = "lstm_model/update_log.txt"

    def load_logs(log_path):
        if not os.path.exists(log_path):
            return pd.DataFrame()
        with open(log_path, "r") as f:
            log_entries = [json.loads(line) for line in f.readlines()]
        return pd.DataFrame(log_entries)

    logs_df = load_logs(log_path)

    if logs_df.empty:
        st.info("No logs available yet. Train the model to generate logs.")
    else:
        logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'])
        logs_df = logs_df.sort_values(by="timestamp", ascending=False)

        latest = logs_df.iloc[0]

        st.markdown(f"""
            <hr>
            <h4 style="color:black;">🧾 Latest Update Summary</h4>
            <ul style="color:black; font-size:16px;">
                <li><strong>Status:</strong> {latest.get('status', 'N/A')}</li>
                <li><strong>Date:</strong> {latest.get('timestamp', 'N/A')}</li>
                <li><strong>MAE:</strong> {latest.get('MAE', 'N/A')}</li>
                <li><strong>RMSE:</strong> {latest.get('RMSE', 'N/A')}</li>
                <li><strong>R²:</strong> {latest.get('R2', 'N/A')}</li>
                <li><strong>Samples (Train/Test):</strong> {latest.get('train_samples', 'N/A')} / {latest.get('test_samples', 'N/A')}</li>
            </ul>
        """, unsafe_allow_html=True)

        st.markdown("<hr style='border: 1px solid black;'>", unsafe_allow_html=True)
        st.dataframe(logs_df, use_container_width=True)


#--------
# Footer
#--------


st.markdown(
    """
    <div style="border: 2px solid black; border-radius: 10px; padding: 20px; margin-top: 2rem; background-color: #f9f9f9;">
        <div style="text-align: center; font-size: 1.5rem; color: black;">
            Made with ❤️ by <strong>Sheema Masood</strong> — Data Scientist | AI Engineer <br/>
            <a href="https://www.linkedin.com/in/sheema-masood/" target="_blank">LinkedIn</a> |
            <a href="https://github.com/sheemamasood381/" target="_blank">GitHub</a> |
            <a href="https://www.kaggle.com/sheemamasood" target="_blank">Kaggle</a>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

