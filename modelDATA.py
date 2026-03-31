"""
Astana US Embassy — dataset builder
Merges raw station AQI data with daily weather from Open-Meteo archive.
No feature engineering. Output is a clean, analysis-ready CSV for model training.

Run:
    pip install requests pandas numpy
    python build_dataset.py
"""

import requests
import numpy as np
import pandas as pd

INPUT_CSV  = "astanaUS.csv"
OUTPUT_CSV = "astana_emb_dataset.csv"
LAT        =  51.125286
LON        =  71.467220
TIMEZONE   = "Asia/Almaty"


# ── 1. Load station data ──────────────────────────────────────────────────────

df = pd.read_csv(INPUT_CSV)
df.columns = df.columns.str.strip()

df["date"] = pd.to_datetime(
    df["date"].astype(str).str.strip(), format="%Y/%m/%d", errors="coerce"
)

for col in ["pm25", "pm10", "o3", "no2", "so2", "co"]:
    df[col] = pd.to_numeric(
        df[col].astype(str).str.strip().replace("", np.nan), errors="coerce"
    )

# o3 has zero valid readings — drop it
df = df.drop(columns=["o3"])

df = df.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)

# Reindex to full daily calendar so gaps appear as explicit NaN rows.
# The raw file is missing 86 date rows entirely (largest gap: 49 days).
full_idx = pd.date_range(df["date"].min(), df["date"].max(), freq="D")
df = (
    df.set_index("date")
    .reindex(full_idx)
    .rename_axis("date")
    .reset_index()
)

print(f"Station rows : {len(df)}")
print(f"Date range   : {df['date'].min().date()} -> {df['date'].max().date()}")
print(f"pm25 valid   : {df['pm25'].notna().sum()} / {len(df)}")


# ── 2. Fetch weather from Open-Meteo archive (free, no key) ──────────────────

start = df["date"].min().strftime("%Y-%m-%d")
end   = df["date"].max().strftime("%Y-%m-%d")
print(f"\nFetching weather {start} -> {end} ...")

resp = requests.get(
    "https://archive-api.open-meteo.com/v1/archive",
    params={
        "latitude":   LAT,
        "longitude":  LON,
        "start_date": start,
        "end_date":   end,
        "hourly": ",".join([
            "temperature_2m",
            "relative_humidity_2m",
            "dew_point_2m",
            "wind_speed_10m",
            "wind_gusts_10m",
            "wind_direction_10m",
            "surface_pressure",
            "precipitation",
            "cloudcover",
            "shortwave_radiation",
        ]),
        "timezone": TIMEZONE,
    },
    timeout=120,
)
resp.raise_for_status()
h = resp.json()["hourly"]

hourly = pd.DataFrame({
    "time":         pd.to_datetime(h["time"]),
    "temp":         h["temperature_2m"],
    "humidity":     h["relative_humidity_2m"],
    "dew_point":    h["dew_point_2m"],
    "wind_speed":   h["wind_speed_10m"],
    "wind_gust":    h["wind_gusts_10m"],
    "wind_dir":     h["wind_direction_10m"],
    "pressure":     h["surface_pressure"],
    "precip":       h["precipitation"],
    "cloud":        h["cloudcover"],
    "radiation":    h["shortwave_radiation"],
})
hourly["date"] = hourly["time"].dt.normalize()

# Aggregate hourly -> daily
weather = hourly.groupby("date").agg(
    temp_mean         =("temp",          "mean"),
    temp_min          =("temp",          "min"),
    temp_max          =("temp",          "max"),
    humidity_mean     =("humidity",      "mean"),
    dew_point_mean    =("dew_point",     "mean"),
    wind_speed_mean   =("wind_speed",    "mean"),
    wind_speed_max    =("wind_speed",    "max"),
    wind_gust_max     =("wind_gust",     "max"),
    wind_dir_mean     =("wind_dir",      "mean"),
    pressure_mean     =("pressure",      "mean"),
    precip_sum        =("precip",        "sum"),
    cloud_mean        =("cloud",         "mean"),
    radiation_mean    =("radiation",     "mean"),
).reset_index()

print(f"Weather rows : {len(weather)}")


# ── 3. Merge and save ─────────────────────────────────────────────────────────

out = df.merge(weather, on="date", how="left")
out = out.sort_values("date").reset_index(drop=True)

out.to_csv(OUTPUT_CSV, index=False)

print(f"\nSaved : {OUTPUT_CSV}")
print(f"Shape : {out.shape}")
print(f"\nColumns:\n{out.columns.tolist()}")
print(f"\nSample:\n{out.head(3).to_string()}")