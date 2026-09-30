import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry

cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session,retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

url = "https://api.open-meteo.com/v1/forecast"

params = {
    "latitude": 63.43,
    "longitude": 10.39,
    "daily": ["sunrise", "sunset"],
    "hourly": ["apparent_temperature", "cloud_cover", "wind_speed_10m", "wind_direction_10m", "rain", "weather_code", "visibility"],
    "timezone": "Europe/Oslo"
}
responses = openmeteo.weather_api(url, params=params)

response = responses[0]
print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
print(f"Timezone: {response.Timezone()}")

hourly = response.Hourly()
hourly_apparent_temperature = hourly.Variables(0).ValuesAsNumpy()
hourly_cloud_cover = hourly.Variables(1).ValuesAsNumpy()
hourly_wind_speed_10m = hourly.Variables(2).ValuesAsNumpy()
hourly_wind_direction_10m = hourly.Variables(3).ValuesAsNumpy()
hourly_rain = hourly.Variables(4).ValuesAsNumpy()
hourly_weather_code = hourly.Variables(5).ValuesAsNumpy()
hourly_visibility = hourly.Variables(6).ValuesAsNumpy()

hourly_data = {
    "date": pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    ).tz_convert(response.Timezone().decode())
}

hourly_data["apparent_temperature"] = hourly_apparent_temperature
hourly_data["cloud_cover"] = hourly_cloud_cover
hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
hourly_data["wind_direction_10m"] = hourly_wind_direction_10m
hourly_data["rain"] = hourly_rain
hourly_data["weather_code"] = hourly_weather_code
hourly_data["visibility"] = hourly_visibility

hourly_dataframe = pd.DataFrame(data=hourly_data)
print(f"\nHourly data\n {hourly_dataframe}")

daily = response.Daily()

daily_data = {
    "date": pd.date_range(
        start=pd.to_datetime(daily.Time(), unit="s", utc=True),
        end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=daily.Interval()),
        inclusive="left",
    ).tz_convert(response.Timezone().decode()),
    "sunrise": pd.to_datetime(
        daily.Variables(0).ValuesInt64AsNumpy(),
        unit="s",
        utc=True,
    ).tz_convert(response.Timezone().decode()),
    "sunset": pd.to_datetime(
        daily.Variables(1).ValuesInt64AsNumpy(),
        unit="s",
        utc=True,
    ).tz_convert(response.Timezone().decode()),
}

daily_dataframe = pd.DataFrame(daily_data)
print(f"\nDaily data\n{daily_dataframe}")