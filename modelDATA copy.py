import requests
import numpy as np
import pandas as pd

INPUT_CSV = "Kazakhstan_astana.csv"
OUTPUT_CSV = "astana_dataset.csv"
LAT = 51.125286
LON = 71.467220
TIMEZONE = "Asia/Almaty"

DROP_ALWAYS = {"co2", "o3"}
POLLUTANT_COLS = ["pm25", "pm10", "no2", "no", "so2", "co", "h2s", "tsp"]
OPEN_METEO_URL = "https://archive-api.open-meteo.com/v1/archive"


def circular_mean_deg(series: pd.Series) -> float:
    vals = pd.to_numeric(series, errors="coerce").dropna().to_numpy(dtype=float)
    if len(vals) == 0:
        return np.nan
    rad = np.deg2rad(vals)
    s = np.sin(rad).mean()
    c = np.cos(rad).mean()
    ang = np.rad2deg(np.arctan2(s, c))
    return (ang + 360.0) % 360.0


def compute_streak(binary_series: pd.Series) -> pd.Series:
    arr = binary_series.fillna(0).astype(int).to_numpy()
    out = np.zeros(len(arr), dtype=int)
    cnt = 0
    for i, v in enumerate(arr):
        if v == 1:
            cnt += 1
        else:
            cnt = 0
        out[i] = cnt
    return pd.Series(out, index=binary_series.index)


def days_since_last_event(binary_series: pd.Series) -> pd.Series:
    arr = binary_series.fillna(0).astype(int).to_numpy()
    out = np.full(len(arr), np.nan, dtype=float)
    last_idx = None
    for i, v in enumerate(arr):
        if v == 1:
            last_idx = i
            out[i] = 0.0
        elif last_idx is not None:
            out[i] = float(i - last_idx)
    return pd.Series(out, index=binary_series.index)


df = pd.read_csv(INPUT_CSV)
df.columns = df.columns.str.strip()

if "date" not in df.columns:
    raise ValueError("Column 'date' not found in input CSV.")

df["date"] = pd.to_datetime(df["date"].astype(str).str.strip(), errors="coerce")
if df["date"].notna().sum() == 0:
    raise ValueError("All values in 'date' became NaT. Check source CSV date format.")

existing_pollutants = [c for c in POLLUTANT_COLS if c in df.columns]
for col in existing_pollutants:
    df[col] = pd.to_numeric(df[col].astype(str).str.strip(), errors="coerce")

drop_cols = [c for c in DROP_ALWAYS if c in df.columns]
if drop_cols:
    df = df.drop(columns=drop_cols)

df = (
    df.dropna(subset=["date"])
      .sort_values("date")
      .drop_duplicates(subset=["date"], keep="last")
      .reset_index(drop=True)
)

start_dt = df["date"].min()
end_dt = df["date"].max()
if pd.isna(start_dt) or pd.isna(end_dt):
    raise ValueError("Parsed dates are invalid after cleaning.")

full_idx = pd.date_range(start=start_dt, end=end_dt, freq="D")
df = (
    df.set_index("date")
      .reindex(full_idx)
      .rename_axis("date")
      .reset_index()
)

print(f"Station rows : {len(df)}")
print(f"Date range   : {df['date'].min().date()} -> {df['date'].max().date()}")
if "pm25" in df.columns:
    print(f"pm25 valid   : {df['pm25'].notna().sum()} / {len(df)}")

start = df["date"].min().strftime("%Y-%m-%d")
end = df["date"].max().strftime("%Y-%m-%d")

print(f"\nFetching weather {start} -> {end} ...")

daily_vars = [
    "temperature_2m_mean",
    "temperature_2m_max",
    "temperature_2m_min",
    "relative_humidity_2m_mean",
    "relative_humidity_2m_max",
    "relative_humidity_2m_min",
    "dew_point_2m_mean",
    "dew_point_2m_max",
    "dew_point_2m_min",
    "surface_pressure_mean",
    "surface_pressure_max",
    "surface_pressure_min",
    "wind_speed_10m_mean",
    "wind_speed_10m_max",
    "wind_speed_10m_min",
    "wind_gusts_10m_mean",
    "wind_gusts_10m_max",
    "wind_gusts_10m_min",
    "wind_direction_10m_dominant",
    "precipitation_sum",
    "precipitation_hours",
    "snowfall_sum",
    "shortwave_radiation_sum",
    "cloud_cover_mean",
    "cloud_cover_max",
    "cloud_cover_min",
    "vapour_pressure_deficit_max",
    "wet_bulb_temperature_2m_mean",
    "wet_bulb_temperature_2m_max",
    "wet_bulb_temperature_2m_min",
    "soil_temperature_0_to_7cm_mean",
    "soil_temperature_7_to_28cm_mean",
    "soil_temperature_28_to_100cm_mean",
    "soil_moisture_0_to_7cm_mean",
    "soil_moisture_7_to_28cm_mean",
    "soil_moisture_28_to_100cm_mean",
    "weather_code"
]

hourly_vars = [
    "wind_direction_10m",
    "wind_speed_10m",
    "wind_gusts_10m",
    "surface_pressure",
    "precipitation",
    "snowfall",
    "cloud_cover",
    "shortwave_radiation",
    "vapour_pressure_deficit",
    "boundary_layer_height",
    "is_day"
]

resp = requests.get(
    OPEN_METEO_URL,
    params={
        "latitude": LAT,
        "longitude": LON,
        "start_date": start,
        "end_date": end,
        "daily": ",".join(daily_vars),
        "hourly": ",".join(hourly_vars),
        "timezone": TIMEZONE
    },
    timeout=180
)
resp.raise_for_status()
payload = resp.json()

daily_json = payload.get("daily", {})
hourly_json = payload.get("hourly", {})

if "time" not in daily_json:
    raise ValueError("Open-Meteo daily response does not contain 'time'.")
if "time" not in hourly_json:
    raise ValueError("Open-Meteo hourly response does not contain 'time'.")

daily = pd.DataFrame({"date": pd.to_datetime(daily_json["time"])})

daily_name_map = {
    "temperature_2m_mean": "temp_mean",
    "temperature_2m_max": "temp_max",
    "temperature_2m_min": "temp_min",
    "relative_humidity_2m_mean": "humidity_mean",
    "relative_humidity_2m_max": "humidity_max",
    "relative_humidity_2m_min": "humidity_min",
    "dew_point_2m_mean": "dew_point_mean",
    "dew_point_2m_max": "dew_point_max",
    "dew_point_2m_min": "dew_point_min",
    "surface_pressure_mean": "pressure_mean",
    "surface_pressure_max": "pressure_max",
    "surface_pressure_min": "pressure_min",
    "wind_speed_10m_mean": "wind_speed_mean",
    "wind_speed_10m_max": "wind_speed_max",
    "wind_speed_10m_min": "wind_speed_min",
    "wind_gusts_10m_mean": "wind_gust_mean",
    "wind_gusts_10m_max": "wind_gust_max",
    "wind_gusts_10m_min": "wind_gust_min",
    "wind_direction_10m_dominant": "wind_dir_dominant",
    "precipitation_sum": "precip_sum",
    "precipitation_hours": "precip_hours",
    "snowfall_sum": "snowfall_sum",
    "shortwave_radiation_sum": "radiation_sum",
    "cloud_cover_mean": "cloud_mean",
    "cloud_cover_max": "cloud_max",
    "cloud_cover_min": "cloud_min",
    "vapour_pressure_deficit_max": "vpd_max",
    "wet_bulb_temperature_2m_mean": "wet_bulb_mean",
    "wet_bulb_temperature_2m_max": "wet_bulb_max",
    "wet_bulb_temperature_2m_min": "wet_bulb_min",
    "soil_temperature_0_to_7cm_mean": "soil_temp_0_7_mean",
    "soil_temperature_7_to_28cm_mean": "soil_temp_7_28_mean",
    "soil_temperature_28_to_100cm_mean": "soil_temp_28_100_mean",
    "soil_moisture_0_to_7cm_mean": "soil_moisture_0_7_mean",
    "soil_moisture_7_to_28cm_mean": "soil_moisture_7_28_mean",
    "soil_moisture_28_to_100cm_mean": "soil_moisture_28_100_mean",
    "weather_code": "weather_code"
}

for src, dst in daily_name_map.items():
    if src in daily_json:
        daily[dst] = pd.to_numeric(daily_json[src], errors="coerce")

hourly = pd.DataFrame({"time": pd.to_datetime(hourly_json["time"])})
hourly["date"] = hourly["time"].dt.normalize()

hourly_name_map = {
    "wind_direction_10m": "wind_dir_hourly",
    "wind_speed_10m": "wind_speed_hourly",
    "wind_gusts_10m": "wind_gust_hourly",
    "surface_pressure": "pressure_hourly",
    "precipitation": "precip_hourly",
    "snowfall": "snowfall_hourly",
    "cloud_cover": "cloud_hourly",
    "shortwave_radiation": "radiation_hourly",
    "vapour_pressure_deficit": "vpd_hourly",
    "boundary_layer_height": "pblh_hourly",
    "is_day": "is_day"
}

for src, dst in hourly_name_map.items():
    if src in hourly_json:
        hourly[dst] = pd.to_numeric(hourly_json[src], errors="coerce")

if {"wind_speed_hourly", "wind_dir_hourly"}.issubset(hourly.columns):
    theta = np.deg2rad(hourly["wind_dir_hourly"])
    hourly["u10_hourly"] = hourly["wind_speed_hourly"] * np.cos(theta)
    hourly["v10_hourly"] = hourly["wind_speed_hourly"] * np.sin(theta)
    hourly["calm_wind_flag_hourly"] = (hourly["wind_speed_hourly"] <= 2.0).astype(float)
else:
    hourly["u10_hourly"] = np.nan
    hourly["v10_hourly"] = np.nan
    hourly["calm_wind_flag_hourly"] = np.nan

hourly["low_rad_flag_hourly"] = np.where(pd.to_numeric(hourly.get("radiation_hourly"), errors="coerce") <= 50, 1.0, 0.0)
hourly["high_pressure_flag_hourly"] = np.where(pd.to_numeric(hourly.get("pressure_hourly"), errors="coerce") >= 1018, 1.0, 0.0)

grouped = hourly.groupby("date", as_index=False)

hourly_daily = grouped.agg(
    u10_mean=("u10_hourly", "mean"),
    v10_mean=("v10_hourly", "mean"),
    calm_wind_hours=("calm_wind_flag_hourly", "sum"),
    low_radiation_hours=("low_rad_flag_hourly", "sum"),
    high_pressure_hours=("high_pressure_flag_hourly", "sum"),
    pblh_mean=("pblh_hourly", "mean"),
    pblh_min=("pblh_hourly", "min"),
    pblh_max=("pblh_hourly", "max"),
    vpd_mean=("vpd_hourly", "mean"),
    cloud_hourly_mean=("cloud_hourly", "mean"),
    precip_hourly_sum=("precip_hourly", "sum"),
    snowfall_hourly_sum=("snowfall_hourly", "sum")
)

wind_dir_daily = (
    hourly.groupby("date")["wind_dir_hourly"]
    .apply(circular_mean_deg)
    .to_frame("wind_dir_circular_mean")
    .reset_index()
)

hourly_daily = hourly_daily.merge(wind_dir_daily, on="date", how="left")

weather = daily.merge(hourly_daily, on="date", how="left").sort_values("date").reset_index(drop=True)

weather["temp_range"] = weather["temp_max"] - weather["temp_min"]
weather["pressure_range"] = weather["pressure_max"] - weather["pressure_min"]
weather["humidity_range"] = weather["humidity_max"] - weather["humidity_min"]
weather["dew_point_depression"] = weather["temp_mean"] - weather["dew_point_mean"]
weather["heating_degree_days"] = np.maximum(0.0, 18.0 - weather["temp_mean"])
weather["gust_to_mean_ratio"] = weather["wind_gust_max"] / weather["wind_speed_mean"].replace(0, np.nan)
weather["wind_gust_excess"] = weather["wind_gust_max"] - weather["wind_speed_mean"]
weather["ventilation_proxy"] = weather["wind_speed_mean"] * weather["pblh_mean"]

weather["snow_flag"] = (weather["snowfall_sum"].fillna(0) > 0).astype(int)
weather["rain_flag"] = (weather["precip_sum"].fillna(0) > 0).astype(int)
weather["cloudy_day_flag"] = (weather["cloud_mean"] >= 80).astype(int)
weather["calm_day_flag"] = (weather["calm_wind_hours"] >= 12).astype(int)
weather["high_pressure_day_flag"] = (weather["high_pressure_hours"] >= 12).astype(int)

weather["pressure_change_1d"] = weather["pressure_mean"].diff(1)
weather["pressure_change_2d"] = weather["pressure_mean"].diff(2)
weather["pressure_change_3d"] = weather["pressure_mean"].diff(3)

weather["temp_change_1d"] = weather["temp_mean"].diff(1)
weather["temp_change_3d"] = weather["temp_mean"].diff(3)
weather["wind_change_1d"] = weather["wind_speed_mean"].diff(1)
weather["wind_change_3d"] = weather["wind_speed_mean"].diff(3)
weather["pblh_change_1d"] = weather["pblh_mean"].diff(1)
weather["ventilation_change_1d"] = weather["ventilation_proxy"].diff(1)

weather["precip_rolling_sum_3d"] = weather["precip_sum"].rolling(3, min_periods=1).sum()
weather["precip_rolling_sum_7d"] = weather["precip_sum"].rolling(7, min_periods=1).sum()
weather["snow_rolling_sum_3d"] = weather["snowfall_sum"].rolling(3, min_periods=1).sum()
weather["snow_rolling_sum_7d"] = weather["snowfall_sum"].rolling(7, min_periods=1).sum()
weather["cloud_rolling_mean_3d"] = weather["cloud_mean"].rolling(3, min_periods=1).mean()
weather["cloud_rolling_mean_7d"] = weather["cloud_mean"].rolling(7, min_periods=1).mean()
weather["radiation_rolling_mean_3d"] = weather["radiation_sum"].rolling(3, min_periods=1).mean()
weather["radiation_rolling_mean_7d"] = weather["radiation_sum"].rolling(7, min_periods=1).mean()
weather["vpd_rolling_mean_3d"] = weather["vpd_mean"].rolling(3, min_periods=1).mean()
weather["vpd_rolling_mean_7d"] = weather["vpd_mean"].rolling(7, min_periods=1).mean()

weather["days_since_last_precip"] = days_since_last_event(weather["rain_flag"])
weather["calm_wind_streak"] = compute_streak(weather["calm_day_flag"])
weather["high_pressure_streak"] = compute_streak(weather["high_pressure_day_flag"])

drop_weather_cols = []
if "wind_dir_dominant" in weather.columns:
    drop_weather_cols.append("wind_dir_dominant")
if "weather_code" in weather.columns and weather["weather_code"].nunique(dropna=True) <= 1:
    drop_weather_cols.append("weather_code")
if drop_weather_cols:
    weather = weather.drop(columns=drop_weather_cols)

out = (
    df.merge(weather, on="date", how="left")
      .sort_values("date")
      .reset_index(drop=True)
)

for c in ["pm10", "no2", "no", "so2", "co", "h2s", "tsp"]:
    if c in out.columns:
        out[c] = pd.to_numeric(out[c], errors="coerce")

out.to_csv(OUTPUT_CSV, index=False)

print(f"\nSaved : {OUTPUT_CSV}")
print(f"Shape : {out.shape}")

missing_summary = out.isna().mean().sort_values(ascending=False).reset_index()
missing_summary.columns = ["column", "missing_rate"]

print("\nTop missing columns:")
print(missing_summary.head(20).to_string(index=False))

print(f"\nColumns:\n{out.columns.tolist()}")
print(f"\nSample:\n{out.head(3).to_string()}")