
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from datetime import datetime
import streamlit as st

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("https://cdn.vectorstock.com/i/500p/97/15/karachi-light-streak-skyline-vector-22829715.jpg");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """,
    unsafe_allow_html=True
)


st.set_page_config(page_title="Pearls' - Karachi AQI ", layout="wide")

# Load data
df = pd.read_csv("data/karachi_daily_aqi_weather.csv")
df['date'] = pd.to_datetime(df['date'])

# Load insights
with open("outputs/eda/insights.json") as f:
    insights = json.load(f)

# Load prediction results
pred_df = pd.read_csv("outputs/predictions/next_3_days.csv")
pred_df['Date'] = pd.to_datetime(pred_df['Date'])

# Load current AQI
with open("outputs/current_aqi.json") as f:
    current_data = json.load(f)
    current_aqi = current_data["aqi"]  # 🛠️ Fix: add the correct key from your JSON

# Create browser-style tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Overview", "🧭 WHO Analysis", "📈 Monthly Trends", "💨 Pollutant Breakdown", "🕒 Logs"])

# ---------------------- Tab 1: Overview ----------------------
with tab1:
    st.title("📊 Karachi AQI Dashboard – Overview")

    st.subheader("Current AQI Gauge")
    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=current_aqi,
        title={'text': "Current AQI"},
        gauge={
            'axis': {'range': [0, 500]},
            'bar': {'color': "black"},
            'steps': [
                {'range': [0, 50], 'color': "green"},
                {'range': [51, 100], 'color': "yellow"},
                {'range': [101, 150], 'color': "orange"},
                {'range': [151, 200], 'color': "red"},
                {'range': [201, 300], 'color': "purple"},
                {'range': [301, 500], 'color': "maroon"},
            ],
        }
    ))
    st.plotly_chart(gauge)

    st.subheader("📅 AQI Forecast for Next 3 Days")
    fig_pred = px.line(pred_df, x='Date', y='Predicted_AQI', markers=True, title="Next 3-Day AQI Forecast")

    st.plotly_chart(fig_pred, use_container_width=True)

    st.subheader("🕒 AQI Over Time")
    st.image("outputs/eda/aqi_over_time.png", use_column_width=True)

    st.subheader("🧠 General AQI Insights")
    for insight in [
        f"📊 Average AQI: {insights['average_aqi']:.2f}",
        f"🔻 Minimum AQI observed: {insights['min_aqi']:.2f}",
        f"🔺 Maximum AQI observed: {insights['max_aqi']:.2f}",
        f"📈 Median AQI: {insights['median_aqi']:.2f}",
        f"📉 Standard Deviation: {insights['standard_deviation']:.2f}",
        f"🧭 AQI on weekdays: {insights['weekday_aqi']:.2f}",
        f"🛌 AQI on weekends: {insights['weekend_aqi']:.2f}",
        f"☣️ Most critical pollutant: {insights['most_critical_pollutant']}",
        f"📌 Avg concentration of {insights['most_critical_pollutant']}: {insights['average_concentration']:.2f}",
        f"🚨 % of days AQI exceeded WHO thresholds: {insights['who_exceedance_percent']}%",
        f"❄️ Winter AQI: {insights['seasonal_avg_aqi']['Winter']:.2f}",
        f"🌸 Spring AQI: {insights['seasonal_avg_aqi']['Spring']:.2f}",
        f"☀️ Summer AQI: {insights['seasonal_avg_aqi']['Summer']:.2f}",
        f"🍂 Autumn AQI: {insights['seasonal_avg_aqi']['Autumn']:.2f}",
        f"🔥 Extreme AQI Days: {insights['extreme_days_count']}"
    ]:
        st.markdown(f"- {insight}")


# -----------------------------------------------------
# 🧭 Tab 2: WHO Analysis
# -----------------------------------------------------
with tab2:
    st.header("WHO Guideline Comparison")

    pollutants = ['PM2.5', 'PM10', 'NO2', 'O3', 'CO', 'SO2']
    avg_values = df[pollutants].mean().round(2)

    # WHO safe limits (µg/m³ or ppm equivalent for 24hr averages)
    who_limits = {
        'PM2.5': 15,
        'PM10': 45,
        'NO2': 25,
        'O3': 100,
        'CO': 4.0,
        'SO2': 40
    }

    st.markdown("### 📋 Comparison with WHO Safe Limits")
    for pollutant in pollutants:
        avg = avg_values[pollutant]
        limit = who_limits[pollutant]
        ratio = round(avg / limit, 1)
        status = "✅ Safe" if avg <= limit else "⚠️ Exceeds"
        st.markdown(f"**{pollutant}** — Avg: **{avg} µg/m³**, WHO Limit: **{limit}**, Status: **{status}** ({ratio}x)")

    st.markdown("### 📊 Visual Comparison")

# -----------------------------------------------------
# 📈 Tab 3: Monthly Trends
# -----------------------------------------------------
with tab3:
    st.header("Monthly AQI Trends")
    df['month'] = df['date'].dt.month_name()
    monthly_avg = df.groupby('month')['AQI'].mean().reindex([
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ])
    fig = px.bar(monthly_avg, x=monthly_avg.index, y=monthly_avg.values, labels={'x': 'Month', 'y': 'Average AQI'})
    st.plotly_chart(fig)

    st.subheader("Seasonal Insights")
    for i, insight in enumerate(insights["monthly"], 1):
        st.markdown(f"**{i}.** {insight}")

# -----------------------------------------------------
# 💨 Tab 4: Pollutant Breakdown
# -----------------------------------------------------
with tab4:
    st.header("Pollutant Contribution in Karachi")

    # Most Critical Pollutant
    most_critical = avg_values.idxmax()
    max_value = avg_values.max()

    st.markdown(f"""
        ### ☣️ Most Critical Pollutant
        The most dominant pollutant in Karachi is:
        🔴 **{most_critical}** — with an average concentration of **{max_value} µg/m³**
    """)

    # Pie chart
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(
        avg_values,
        labels=avg_values.index,
        autopct='%1.1f%%',
        colors=plt.cm.Reds(np.linspace(0.3, 1, len(avg_values)))
    )
    ax.set_title("Contribution of Pollutants in Karachi Air")
    st.pyplot(fig)

# -----------------------------------------------------
# 🕒 Tab 5: Logs
# -----------------------------------------------------
with tab5:
    st.header("System Logs")
    st.markdown(f"**Last AQI Data Update:** {df['date'].max().strftime('%Y-%m-%d')}")
    st.markdown(f"**Last Model Prediction Run:** {pred_df['date'].max().strftime('%Y-%m-%d')}")

    st.subheader("Model Update Logs")
    for i, log in enumerate(insights["logs"], 1):
        st.markdown(f"**{i}.** {log}")

# ------------------------------
# Footer
# ------------------------------

st.markdown("---")

st.caption("""
🔗 **About This Project**

Built with ❤️ using **Streamlit** by **Sheema Masood** — AI Engineer & Data Scientist.

🚀 **Internship Project**: Submitted as part of the **AI Internship Program at 10Pearls, Pakistan** in **August 2025**.

🔍 **Connect with Me:**
- [LinkedIn](https://www.linkedin.com/in/sheema-masood/)
- [GitHub](https://github.com/sheemamasood381/)
- [Kaggle](https://www.kaggle.com/sheemamasood)
""")
