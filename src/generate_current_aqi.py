# generate_current_aqi.py

import pandas as pd
import json
import os

# Load the AQI dataset
df = pd.read_csv("data/karachi_daily_aqi_weather.csv")
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date")

# Get the latest AQI
latest = df.iloc[-1]
current_aqi = {
    "aqi": round(latest["AQI"], 2),
    "date": latest["date"].strftime("%Y-%m-%d")
}

# Save to JSON
os.makedirs("data", exist_ok=True)
with open("outputs/current_aqi.json", "w") as f:
    json.dump(current_aqi, f, indent=4)

print("✅ current_aqi.json generated successfully.")
