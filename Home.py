import streamlit as st
import requests
import pandas as pd
from numpy.random import default_rng as rng
import plotly.express as px
import os

st.set_page_config(
    page_title="Weather Time",
    page_icon="🌦",
    layout="wide"
)

st.write("✅ APP STARTED")
#st.write(os.listdir())


st.title("🌦 Weather Time")
st.caption("Your personal real-time weather assistant")

#st.sidebar.markdown("---")
st.sidebar.caption("Weather Time v0.5 | Built with Streamlit")
st.sidebar.caption("Data provided by Open-Meteo API")

lat = st.sidebar.number_input("Latitude", value=0.0)
long = st.sidebar.number_input("Longitude", value=0.0)

st.sidebar.markdown("### 🌍 Select a City")

cities = {
    "Select a city": (0.0, 0.0),
    "New York, USA": (40.7128, -74.0060),
    "London, UK": (51.5074, -0.1278),
    "Berlin, Germany": (52.52, 13.41),
    "Tokyo, Japan": (35.6895, 139.6917),
    "Colombo, Sri Lanka": (6.9271, 79.8612)
}

selected_city = st.sidebar.selectbox("Choose a city", list(cities.keys()))

if selected_city != "Select a city":
    lat, long = cities[selected_city]

if lat == 0.0 and long == 0.0:
    st.warning("⚠ Please select a city or enter valid coordinates.")
    st.stop()



url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&daily=temperature_2m_max,weather_code,temperature_2m_min,apparent_temperature_max,sunrise,apparent_temperature_min,sunset,daylight_duration,sunshine_duration,uv_index_max,uv_index_clear_sky_max,wind_speed_10m_max,wind_gusts_10m_max,wind_direction_10m_dominant,shortwave_radiation_sum,et0_fao_evapotranspiration,rain_sum,showers_sum,snowfall_sum,precipitation_sum,precipitation_hours,precipitation_probability_max&hourly=temperature_2m,rain,showers,snowfall,soil_temperature_0cm,relative_humidity_2m,dew_point_2m,apparent_temperature,precipitation_probability,precipitation,snow_depth,soil_temperature_6cm,soil_temperature_18cm,soil_temperature_54cm,soil_moisture_0_to_1cm,soil_moisture_1_to_3cm,soil_moisture_3_to_9cm,soil_moisture_9_to_27cm,soil_moisture_27_to_81cm,wind_speed_10m,weather_code,pressure_msl,surface_pressure,wind_speed_120m,wind_speed_80m,wind_speed_180m,cloud_cover,wind_direction_10m,cloud_cover_low,wind_direction_80m,cloud_cover_mid,wind_direction_120m,cloud_cover_high,wind_direction_180m,visibility,wind_gusts_10m,evapotranspiration,temperature_80m,et0_fao_evapotranspiration,temperature_120m,vapour_pressure_deficit,temperature_180m&current=temperature_2m,relative_humidity_2m,is_day,wind_speed_10m,rain,showers,snowfall,apparent_temperature,precipitation,wind_direction_10m,wind_gusts_10m,cloud_cover,weather_code,pressure_msl,surface_pressure&timezone=auto"
#https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&daily=temperature_2m_max,weather_code,temperature_2m_min,apparent_temperature_max,sunrise,apparent_temperature_min,sunset,daylight_duration,sunshine_duration,uv_index_max,uv_index_clear_sky_max,wind_speed_10m_max,wind_gusts_10m_max,wind_direction_10m_dominant,shortwave_radiation_sum,et0_fao_evapotranspiration,rain_sum,showers_sum,snowfall_sum,precipitation_sum,precipitation_hours,precipitation_probability_max&hourly=temperature_2m,rain,showers,snowfall,soil_temperature_0cm,relative_humidity_2m,dew_point_2m,apparent_temperature,precipitation_probability,precipitation,snow_depth,soil_temperature_6cm,soil_temperature_18cm,soil_temperature_54cm,soil_moisture_0_to_1cm,soil_moisture_1_to_3cm,soil_moisture_3_to_9cm,soil_moisture_9_to_27cm,soil_moisture_27_to_81cm,wind_speed_10m,weather_code,pressure_msl,surface_pressure,wind_speed_120m,wind_speed_80m,wind_speed_180m,cloud_cover,wind_direction_10m,cloud_cover_low,wind_direction_80m,cloud_cover_mid,wind_direction_120m,cloud_cover_high,wind_direction_180m,visibility,wind_gusts_10m,evapotranspiration,temperature_80m,et0_fao_evapotranspiration,temperature_120m,vapour_pressure_deficit,temperature_180m&current=temperature_2m,relative_humidity_2m,is_day,wind_speed_10m,rain,showers,snowfall,apparent_temperature,precipitation,wind_direction_10m,wind_gusts_10m,cloud_cover,weather_code,pressure_msl,surface_pressure&timezone=auto

try:
    Weather_data = requests.get(url).json()

    # ✅ CHECK if "current" exists BEFORE using it
    if "current" not in Weather_data:
        st.warning("⚠ Please select a city or enter valid coordinates.")
        st.stop()
except:
    st.error("⚠ Failed to fetch weather data. Check your internet or location.")
    st.stop()

Metrics_on = st.toggle("Show More Features")

col1, col2 = st.columns(2)

col1.metric("🌡 Temperature", f"{Weather_data['current']['temperature_2m']} ℃")
col2.metric("💨 Wind", f"{Weather_data['current']['wind_speed_10m']} Km/h")

col3, col4 = st.columns(2)

col3.metric("💧 Humidity", f"{Weather_data['current']['relative_humidity_2m']}%")
col4.metric("🌧 Rain Now", f"{Weather_data['current']['rain']} mm")

if Metrics_on:
    col5, col6 = st.columns(2)
    col5.metric("🧭 Wind Direction", f"{Weather_data['current']['wind_direction_10m']} °")
    col6.metric("🌍 Time Zone", f"{Weather_data['timezone']}")

Temp_df = pd.DataFrame({
    "Time": Weather_data['hourly']['time'],
    "Temperature": Weather_data['hourly']['temperature_2m']
})

Rain_df = pd.DataFrame({
    "Time": Weather_data['hourly']['time'],
    "Rain": Weather_data['hourly']['rain']
})

Wind_df = pd.DataFrame({
    "Time": Weather_data['hourly']['time'],
    "Wind Speed": Weather_data['hourly']['wind_speed_10m']
})



tab1, tab2 = st.tabs(["📊 Hourly Charts", "📅 Daily Chart"])

with tab1:

    hourly_df = pd.DataFrame({
    "datetime": Weather_data["hourly"]["time"],
    "Temperature": Weather_data["hourly"]["temperature_2m"],
    "Rain": Weather_data["hourly"]["rain"],
    "Wind Speed": Weather_data["hourly"]["wind_speed_10m"],
    })

# Convert to datetime
    hourly_df["datetime"] = pd.to_datetime(hourly_df["datetime"])

# --- HOURLY FILTER SECTION ---
    st.subheader("⏱ Select Time Range")

    min_time = hourly_df["datetime"].min()
    max_time = hourly_df["datetime"].max()

    colA, colB = st.columns(2)

# Start
    start_date = colA.date_input("Start Date", value=hourly_df["datetime"].min().date())
    start_time = colA.time_input("Start Time", value=hourly_df["datetime"].min().time())
    start_datetime = pd.to_datetime(f"{start_date} {start_time}")

# End
    end_date = colB.date_input("End Date", value=hourly_df["datetime"].max().date())
    end_time = colB.time_input("End Time", value=hourly_df["datetime"].max().time())
    end_datetime = pd.to_datetime(f"{end_date} {end_time}")

# --- Filter DataFrame ---
    hourly_filtered = hourly_df[
    (hourly_df["datetime"] >= start_datetime) &
    (hourly_df["datetime"] <= end_datetime)
    ]

# --- Show warning if no data ---
    if hourly_filtered.empty:
        st.warning("⚠ No data available for the selected date/time range. Please select a valid range.")
    else:
        st.subheader("🌡 Temperature")
        st.line_chart(hourly_filtered, x="datetime", y="Temperature")

        st.subheader("🌧 Rain")
        st.bar_chart(hourly_filtered, x="datetime", y="Rain")

        st.subheader("💨 Wind Speed")
        st.line_chart(hourly_filtered, x="datetime", y="Wind Speed")

with tab2:
    st.title("🚧 Coming Soon")
    st.write("Daily weather forecast will be added here, And More features will be added soon.")
    st.subheader("🌡 Daily Temperature Range")


    daily_df = pd.DataFrame({
    "date": Weather_data["daily"]["time"],
    "temp_max": Weather_data["daily"]["temperature_2m_max"],
    "temp_min": Weather_data["daily"]["temperature_2m_min"],
    })

    daily_df["date"] = pd.to_datetime(daily_df["date"])

    start_date = st.date_input(
    "Start Date",
    value=daily_df["date"].min(),
    min_value=daily_df["date"].min(),
    max_value=daily_df["date"].max()
    )

    end_date = st.date_input(
    "End Date",
    value=daily_df["date"].max(),
    min_value=daily_df["date"].min(),
    max_value=daily_df["date"].max()
    )

    daily_filtered = daily_df[
        (daily_df["date"] >= pd.to_datetime(start_date)) &
        (daily_df["date"] <= pd.to_datetime(end_date))
    ]

    if daily_filtered.empty:
        st.warning("⚠ No data available for the selected date range. Please select a valid range.")
    else:
        fig = px.area(
            daily_filtered,
            x="date",
            y=["temp_min", "temp_max"],
            labels={"value": "Temperature (°C)", "date": "Date"},
            title="Daily Temperature Range",
        )
    st.plotly_chart(fig, use_container_width=True)