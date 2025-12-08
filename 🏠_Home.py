import streamlit as st
import requests
import pandas as pd
from numpy.random import default_rng as rng

st.set_page_config(
    page_title="Weather Time",
    page_icon="🌦",
    layout="wide"
)

st.title("🌦 Weather Time")
st.caption("Your personal real-time weather assistant")

#st.sidebar.markdown("---")
st.sidebar.caption("Weather Time v1.0.1 | Built with Streamlit")
st.sidebar.caption("Data provided by Open-Meteo API")

lat = st.sidebar.number_input("latitude")
long = st.sidebar.number_input("longitude")
city = st.sidebar.text_input("Enter City Name (Optional)")
url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&daily=temperature_2m_max,weather_code,temperature_2m_min,apparent_temperature_max,sunrise,apparent_temperature_min,sunset,daylight_duration,sunshine_duration,uv_index_max,uv_index_clear_sky_max,wind_speed_10m_max,wind_gusts_10m_max,wind_direction_10m_dominant,shortwave_radiation_sum,et0_fao_evapotranspiration,rain_sum,showers_sum,snowfall_sum,precipitation_sum,precipitation_hours,precipitation_probability_max&hourly=temperature_2m,rain,showers,snowfall,soil_temperature_0cm,relative_humidity_2m,dew_point_2m,apparent_temperature,precipitation_probability,precipitation,snow_depth,soil_temperature_6cm,soil_temperature_18cm,soil_temperature_54cm,soil_moisture_0_to_1cm,soil_moisture_1_to_3cm,soil_moisture_3_to_9cm,soil_moisture_9_to_27cm,soil_moisture_27_to_81cm,wind_speed_10m,weather_code,pressure_msl,surface_pressure,wind_speed_120m,wind_speed_80m,wind_speed_180m,cloud_cover,wind_direction_10m,cloud_cover_low,wind_direction_80m,cloud_cover_mid,wind_direction_120m,cloud_cover_high,wind_direction_180m,visibility,wind_gusts_10m,evapotranspiration,temperature_80m,et0_fao_evapotranspiration,temperature_120m,vapour_pressure_deficit,temperature_180m&current=temperature_2m,relative_humidity_2m,is_day,wind_speed_10m,rain,showers,snowfall,apparent_temperature,precipitation,wind_direction_10m,wind_gusts_10m,cloud_cover,weather_code,pressure_msl,surface_pressure&timezone=auto"
#https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&daily=temperature_2m_max,weather_code,temperature_2m_min,apparent_temperature_max,sunrise,apparent_temperature_min,sunset,daylight_duration,sunshine_duration,uv_index_max,uv_index_clear_sky_max,wind_speed_10m_max,wind_gusts_10m_max,wind_direction_10m_dominant,shortwave_radiation_sum,et0_fao_evapotranspiration,rain_sum,showers_sum,snowfall_sum,precipitation_sum,precipitation_hours,precipitation_probability_max&hourly=temperature_2m,rain,showers,snowfall,soil_temperature_0cm,relative_humidity_2m,dew_point_2m,apparent_temperature,precipitation_probability,precipitation,snow_depth,soil_temperature_6cm,soil_temperature_18cm,soil_temperature_54cm,soil_moisture_0_to_1cm,soil_moisture_1_to_3cm,soil_moisture_3_to_9cm,soil_moisture_9_to_27cm,soil_moisture_27_to_81cm,wind_speed_10m,weather_code,pressure_msl,surface_pressure,wind_speed_120m,wind_speed_80m,wind_speed_180m,cloud_cover,wind_direction_10m,cloud_cover_low,wind_direction_80m,cloud_cover_mid,wind_direction_120m,cloud_cover_high,wind_direction_180m,visibility,wind_gusts_10m,evapotranspiration,temperature_80m,et0_fao_evapotranspiration,temperature_120m,vapour_pressure_deficit,temperature_180m&current=temperature_2m,relative_humidity_2m,is_day,wind_speed_10m,rain,showers,snowfall,apparent_temperature,precipitation,wind_direction_10m,wind_gusts_10m,cloud_cover,weather_code,pressure_msl,surface_pressure&timezone=auto

Weather = requests.get(url)
Weather_data = Weather.json()

def get_weather_data(url):
    return requests.get(url).json()

Weather_data = get_weather_data(url)

try:
    Weather = requests.get(url)
    Weather_data = Weather.json()
except:
    st.error("⚠ Failed to fetch weather data. Check your internet or coordinates.")
    st.stop()

col1, col2, col3, col4, = st.columns(4)
col1.metric("Temperature",f"{Weather_data['current']['temperature_2m']} ℃")
col2.metric("Wind",f"{Weather_data['current']['wind_speed_10m']} Km/h")
col3.metric("Humidity",f"{Weather_data['current']['relative_humidity_2m']}%")
col4.metric("Now Rain",f"{Weather_data['current']['rain']}")

Metrics_on = st.sidebar.toggle("Show More Features")

if Metrics_on:
    col5, col6 = st.columns(2)
    col5.metric("Wind Direction",f"{Weather_data['current']['wind_direction_10m']} °")
    col6.metric("Time Zone",f"{Weather_data['timezone']}")

temperature_data = {"y":Weather_data['hourly']['temperature_2m'], "x":Weather_data['hourly']['time']}

Temp_df = pd.DataFrame(temperature_data)

rain_data = {"y":Weather_data['hourly']['rain'], "x":Weather_data['hourly']['time']}

rain_df = pd.DataFrame(rain_data)

wind_data = {"y":Weather_data['hourly']['wind_speed_10m'], "x":Weather_data['hourly']['time']}

wind_df = pd.DataFrame(wind_data)

tab1, tab2, = st.tabs(["Hourly Charts", "Daily Chart",])
tab1.line_chart(Temp_df,x_label="Date and Time",y_label="Temperature", y="y", x="x")
tab1.bar_chart(rain_df,x_label="Date and Time",y_label="milimeter", y="y", x="x")
tab1.line_chart(wind_df,x_label="Date and Time",y_label="Speed(Km/h)", y="y", x="x")
tab2.title ("Coming Soon")




