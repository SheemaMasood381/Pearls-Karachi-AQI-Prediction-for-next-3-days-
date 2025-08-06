# src/eda.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json

def run_eda(df, output_dir="outputs/eda"):
    print("Saving charts to:", os.path.abspath(output_dir))
    os.makedirs(output_dir, exist_ok=True)
    # ------------------ Plot: AQI Over Time ------------------
    plt.figure(figsize=(12, 4))
    plt.plot(df['date'], df['AQI'], color='blue', label='AQI')
    plt.axhspan(0, 50, color='green', alpha=0.1, label='Good')
    plt.axhspan(51, 100, color='yellow', alpha=0.1, label='Moderate')
    plt.axhspan(101, 150, color='orange', alpha=0.1, label='Unhealthy for Sensitive')
    plt.axhspan(151, 200, color='red', alpha=0.1, label='Unhealthy')
    plt.axhspan(201, 300, color='purple', alpha=0.1, label='Very Unhealthy')
    plt.legend()
    plt.title('AQI Over Time with WHO Thresholds')
    plt.ylabel('AQI')
    plt.tight_layout()
    plt.savefig(f"{output_dir}/aqi_over_time.png")
    plt.close()

    # ------------------ Plot: Monthly AQI ------------------
    df['month'] = df['date'].dt.month
    monthly_avg = df.groupby('month')['AQI'].mean()
    plt.figure(figsize=(10, 5))
    monthly_avg.plot(kind='bar', color='teal')
    plt.title("Average AQI by Month")
    plt.xlabel("Month")
    plt.ylabel("Mean AQI")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/monthly_avg.png")
    plt.close()

        # ------------------ Plot: Monthly Average of Pollutants ------------------
    pollutants = ['PM2.5', 'PM10', 'NO2', 'SO2', "O3", 'CO']
    monthly_pollutants = df.groupby('month')[pollutants].mean()

    plt.figure(figsize=(12, 6))
    monthly_pollutants.plot(kind='bar', ax=plt.gca())
    plt.title("Monthly Average of Pollutants")
    plt.xlabel("Month")
    plt.ylabel("Mean Concentration")
    plt.grid(True, axis='y')
    plt.legend(title='Pollutants')
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/monthly_avg_pollutants.png")
    plt.close()


    # ------------------ Plot: Pollutant Contribution Pie ------------------
    pollutants = ['PM2.5', 'PM10', 'NO2', 'O3', 'CO', 'SO2']
    avg_values = df[pollutants].mean()
    plt.figure(figsize=(6, 6))
    plt.pie(avg_values, labels=pollutants, autopct='%1.1f%%',
            colors=plt.cm.Reds(np.linspace(0.3, 1, len(pollutants))))
    plt.title('Pollutant Contribution in Karachi Air')
    plt.tight_layout()
    plt.savefig(f"{output_dir}/pollutant_pie.png")
    plt.close()

    # ------------------ Plot: Pollutant Distributions ------------------
    plt.figure(figsize=(14, 8))
    for i, col in enumerate(pollutants):
        plt.subplot(2, 3, i+1)
        sns.histplot(df[col], kde=True, color='teal')
        plt.title(f'{col} Distribution')
    plt.tight_layout()
    plt.savefig(f"{output_dir}/pollutant_distributions.png")
    plt.close()

    # ------------------ Plot: Correlation Heatmap ------------------
    corr = df.drop(columns='date').corr()
    plt.figure(figsize=(12, 8))
    sns.heatmap(corr, annot=True, cmap='Blues', fmt=".2f", square=True)
    plt.title("Correlation Heatmap")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/correlation_heatmap.png")
    plt.close()

    # ------------------ Plot: AQI vs Temperature ------------------
        # ------------------ Combined Plot: AQI vs Temperature, Humidity, Precipitation ------------------
    fig, axes = plt.subplots(1, 3, figsize=(18, 5), sharey=True)

    # AQI vs Temperature
    sns.scatterplot(data=df, x='Temperature', y='AQI', hue='month', palette='viridis', ax=axes[0])
    axes[0].set_title("AQI vs Temperature")
    axes[0].set_xlabel("Temperature")
    axes[0].set_ylabel("AQI")

    # AQI vs Humidity
    sns.scatterplot(data=df, x='Humidity', y='AQI', hue='month', palette='viridis', ax=axes[1])
    axes[1].set_title("AQI vs Humidity")
    axes[1].set_xlabel("Humidity")
    axes[1].set_ylabel("")  # To avoid duplicate AQI labels

    # AQI vs Precipitation
    sns.scatterplot(data=df, x='Precipitation', y='AQI', hue='month', palette='viridis', ax=axes[2])
    axes[2].set_title("AQI vs Precipitation")
    axes[2].set_xlabel("Precipitation")
    axes[2].set_ylabel("")

    # Common formatting
    handles, labels = axes[2].get_legend_handles_labels()
    fig.legend(handles, labels, title='Month', loc='upper center', ncol=12)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(f"{output_dir}/aqi_vs_weather_factors.png")
    plt.close()


    
    # ------------------ Plot: Average Pollutant Levels ------------------
    avg_concentrations = avg_values.sort_values(ascending=False)
    most_critical = avg_concentrations.idxmax()
    most_value = avg_concentrations.max()

    plt.figure(figsize=(10, 5))
    avg_concentrations.plot(kind='bar', color='skyblue', edgecolor='black')
    plt.title('Average Pollutant Levels')
    plt.axhline(y=most_value, color='red', linestyle='--', label=f'{most_critical} (highest)')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{output_dir}/pollutant_avg_levels.png")
    plt.close()

   # ------------------ WHO Limit Comparison (Bar + Radar Merged Inline) ------------------
    print("\n📊 WHO Air Quality Limit Comparison for Karachi")
    print("=" * 60)

    who_limits = pd.Series({
        'PM2.5': 15,
        'PM10': 45,
        'NO2': 25,
        'O3': 100,
        'CO': 4000,
        'SO2': 40
    })

    karachi_avg = df[pollutants].mean()
    karachi_ratio = karachi_avg / who_limits
    who_ratio = pd.Series([1.0] * len(pollutants), index=pollutants)

    angles = np.linspace(0, 2 * np.pi, len(pollutants), endpoint=False).tolist()
    angles += angles[:1]
    karachi_plot = karachi_ratio.tolist() + karachi_ratio.tolist()[:1]
    who_plot = who_ratio.tolist() + who_ratio.tolist()[:1]

    fig = plt.figure(figsize=(16, 7))

    # Bar chart
    ax1 = fig.add_subplot(1, 2, 1)
    x = np.arange(len(pollutants))
    width = 0.35
    ax1.bar(x - width/2, karachi_avg[pollutants], width, label='Karachi Avg', color='salmon')
    ax1.bar(x + width/2, who_limits[pollutants], width, label='WHO Limit', color='seagreen')
    ax1.set_xticks(x)
    ax1.set_xticklabels(pollutants)
    ax1.set_ylabel('Concentration (µg/m³)')
    ax1.set_title('Karachi vs WHO: Avg Pollutant Levels')
    ax1.legend()

    # Radar chart
    ax2 = fig.add_subplot(1, 2, 2, polar=True)
    ax2.plot(angles, karachi_plot, color='crimson', linewidth=2, label='Karachi Avg / WHO')
    ax2.fill(angles, karachi_plot, color='crimson', alpha=0.25)
    ax2.plot(angles, who_plot, color='green', linewidth=2, label='WHO Safe Limit')
    ax2.fill(angles, who_plot, color='green', alpha=0.15)
    ax2.set_thetagrids(np.degrees(angles[:-1]), pollutants)
    ax2.set_title('Risk Ratio (Karachi Avg / WHO)', fontsize=13)
    ax2.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))

    plt.tight_layout()
    plt.savefig(f"{output_dir}/who_comparison_charts.png")
    plt.close()

    # ------------------ Save Summary & Insights ------------------
    df['weekday'] = df['date'].dt.weekday
    df['is_weekend'] = df['weekday'].isin([5, 6])
    df['season'] = df['date'].dt.month.map(lambda m: (
        'Winter' if m in [12, 1, 2] else
        'Spring' if m in [3, 4, 5] else
        'Summer' if m in [6, 7, 8] else
        'Autumn'))

    insights = {
        "average_aqi": round(df['AQI'].mean(), 2),
        "median_aqi": round(df['AQI'].median(), 2),
        "standard_deviation": round(df['AQI'].std(), 2),
        "max_aqi": round(df['AQI'].max(), 2),
        "min_aqi": round(df['AQI'].min(), 2),
        "weekday_aqi": round(df[df['is_weekend'] == False]['AQI'].mean(), 2),
        "weekend_aqi": round(df[df['is_weekend'] == True]['AQI'].mean(), 2),
        "most_critical_pollutant": most_critical,
        "average_concentration": round(most_value, 2),
        "who_exceedance_percent": round((df['AQI'] > 100).mean() * 100, 2),
        "seasonal_avg_aqi": df.groupby("season")['AQI'].mean().to_dict(),
        "extreme_days_count": int((df['AQI'] > 150).sum())
    }

    with open(f"{output_dir}/insights.json", "w") as f:
        json.dump(insights, f, indent=4)

    print(f"✅ EDA completed. Results saved in: {output_dir}/")


if __name__ == "__main__":
    df = pd.read_csv("data/karachi_daily_aqi_weather.csv", parse_dates=["date"])
    run_eda(df)
