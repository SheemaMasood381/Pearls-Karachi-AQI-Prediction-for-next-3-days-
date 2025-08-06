import requests
import pandas as pd
from datetime import date, timedelta
import os
from tqdm import tqdm

LAT, LON = 24.8607, 67.0011
TIMEZONE = "Asia/Karachi"

def fetch_hourly_data(day):
    try:
        # AQI and pollutants
        air_url = (
            "https://air-quality-api.open-meteo.com/v1/air-quality"
            f"?latitude={LAT}&longitude={LON}"
            f"&start_date={day}&end_date={day}"
            "&hourly=us_aqi,pm2_5,pm10,nitrogen_dioxide,sulphur_dioxide,carbon_monoxide,ozone"
            f"&timezone={TIMEZONE}"
        )
        air_response = requests.get(air_url)
        if air_response.status_code != 200 or not air_response.text.strip():
            raise ValueError("Air API failed or returned empty")

        air_data = air_response.json()["hourly"]

        # Weather
        weather_url = (
            "https://archive-api.open-meteo.com/v1/archive"
            f"?latitude={LAT}&longitude={LON}"
            f"&start_date={day}&end_date={day}"
            "&hourly=temperature_2m,relative_humidity_2m,precipitation"
            f"&timezone={TIMEZONE}"
        )
        weather_response = requests.get(weather_url)
        if weather_response.status_code != 200 or not weather_response.text.strip():
            raise ValueError("Weather API failed or returned empty")

        weather_data = weather_response.json()["hourly"]

        df_air = pd.DataFrame(air_data)
        df_weather = pd.DataFrame(weather_data)
        df = pd.merge(df_air, df_weather, on="time")
        df["time"] = pd.to_datetime(df["time"])

        df = df.rename(columns={
            'us_aqi': 'AQI',
            'pm2_5': 'PM2.5',
            'pm10': 'PM10',
            'nitrogen_dioxide': 'NO2',
            'sulphur_dioxide': 'SO2',
            'carbon_monoxide': 'CO',
            'ozone': 'O3',
            'temperature_2m': 'Temperature',
            'relative_humidity_2m': 'Humidity',
            'precipitation': 'Precipitation'
        })

        return df

    except Exception as e:
        print(f"❌ Failed to fetch data for {day}: {e}")
        return None


def main():
    start = date(2023, 1, 1)
    today = date.today()
    all_data = []

    for single_day in tqdm(pd.date_range(start, today), desc="Fetching hourly data"):
        day_str = single_day.date().isoformat()
        df = fetch_hourly_data(day_str)
        if df is not None and not df.empty:
            all_data.append(df)

    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        final_df = final_df.sort_values("time")
        os.makedirs("data", exist_ok=True)
        final_df.to_csv("data/karachi_hourly_aqi_weather.csv", index=False)
        print("✅ Full hourly data saved to data/karachi_hourly_aqi_weather.csv")
    else:
        print("⚠️ No data fetched.")


if __name__ == "__main__":
    main()
