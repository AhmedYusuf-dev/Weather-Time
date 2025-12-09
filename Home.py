import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Weather Time",
    page_icon="🌦",
    layout="wide"
)

st.title("🌦 Weather Time")
st.caption("Your personal real-time weather assistant")
st.sidebar.caption("Weather Time v1.0 | Built with Streamlit")
st.sidebar.caption("Data provided by Open-Meteo API")

# --- CONTINENT & CITY SELECTION ---
st.sidebar.markdown("### 🌍 Select a Continent & City or Enter Coordinates")

continents = {
    "Custom Coordinates": {"Custom Coordinates": (0.0, 0.0)},
    "North America": {
        "New York, USA": (40.7128, -74.0060),
        "Toronto, Canada": (43.6532, -79.3832),
        "Los Angeles, USA": (34.0522, -118.2437),
    },
    "Europe": {
        "London, UK": (51.5074, -0.1278),
        "Berlin, Germany": (52.52, 13.41),
        "Paris, France": (48.8566, 2.3522),
        "Moscow, Russia": (55.7558, 37.6173),
    },
    "Asia": {
        "Tokyo, Japan": (35.6895, 139.6917),
        "Beijing, China": (39.9042, 116.4074),
        "Delhi, India": (28.6139, 77.2090),
        "Colombo, Sri Lanka": (6.9271, 79.8612),
        "Bangkok, Thailand": (13.7563, 100.5018),
    },
    "Australia & Oceania": {
        "Sydney, Australia": (-33.8688, 151.2093),
        "Auckland, New Zealand": (-36.8485, 174.7633),
    },
    "South America": {
        "Rio de Janeiro, Brazil": (-22.9068, -43.1729),
        "Buenos Aires, Argentina": (-34.6037, -58.3816),
        "Santiago, Chile": (-33.4489, -70.6693),
    },
    "Africa": {
        "Cairo, Egypt": (30.0444, 31.2357),
        "Lagos, Nigeria": (6.5244, 3.3792),
        "Johannesburg, South Africa": (-26.2041, 28.0473),
    }
}

selected_continent = st.sidebar.selectbox("Select Continent", list(continents.keys()))
cities = continents[selected_continent]
selected_city = st.sidebar.selectbox("Select City", list(cities.keys()))

if selected_city == "Custom Coordinates":
    lat = st.sidebar.number_input("Latitude", value=0.0, format="%.6f")
    long = st.sidebar.number_input("Longitude", value=0.0, format="%.6f")
else:
    lat, long = cities[selected_city]

if lat == 0.0 and long == 0.0:
    st.warning("⚠ Please select a city or enter valid coordinates.")
    st.stop()

# --- CACHE API RESPONSE ---
@st.cache_data(ttl=600)
def fetch_weather(lat, long):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&daily=temperature_2m_max,temperature_2m_min,uv_index_max,sunrise,sunset,daylight_duration&hourly=temperature_2m,rain,wind_speed_10m,relativehumidity_2m,apparent_temperature,pressure_msl,cloudcover&current_weather=true&timezone=auto"
    return requests.get(url).json()

Weather_data = fetch_weather(lat, long)
if "current_weather" not in Weather_data:
    st.warning("⚠ Weather data not available.")
    st.stop()

# --- CURRENT METRICS ---
st.subheader("🌟 Current Weather Metrics")
curr = Weather_data["current_weather"]
col1, col2, col3, col4 = st.columns(4)
col1.metric("🌡 Temperature", f"{curr['temperature']} ℃")
col2.metric("💨 Wind Speed", f"{curr['windspeed']} Km/h")
col3.metric("💧 Humidity", f"{Weather_data['hourly']['relativehumidity_2m'][0]}%")
col4.metric("🌧 Rain", f"{Weather_data['hourly']['rain'][0]} mm")

# --- MORE METRICS TOGGLE ---
if st.sidebar.checkbox("Show More Features"):
    st.subheader("📈 Additional Weather Metrics")
    col5, col6, col7, col8 = st.columns(4)
    col5.metric("🧭 Wind Direction", f"{curr['winddirection']} °")
    col6.metric("🌍 Timezone", f"{Weather_data['timezone']}")
    col7.metric("🌞 Sunrise", Weather_data['daily']['sunrise'][0].split("T")[1])
    col8.metric("🌅 Sunset", Weather_data['daily']['sunset'][0].split("T")[1])
    st.metric("UV Index", Weather_data['daily']['uv_index_max'][0])
    st.metric("Pressure", Weather_data['hourly']['pressure_msl'][0])
    st.metric("Cloud Cover", Weather_data['hourly']['cloudcover'][0])
    st.write(f"🌞 Daylight Duration: {Weather_data['daily']['daylight_duration'][0]}")

# --- HOURLY DATAFRAME ---
hourly_df = pd.DataFrame({
    "datetime": pd.to_datetime(Weather_data["hourly"]["time"]),
    "Temperature": Weather_data["hourly"]["temperature_2m"],
    "Apparent Temp": Weather_data["hourly"]["apparent_temperature"],
    "Rain": Weather_data["hourly"]["rain"],
    "Wind Speed": Weather_data["hourly"]["wind_speed_10m"],
    "Humidity": Weather_data["hourly"]["relativehumidity_2m"],
})

# --- DAILY DATAFRAME ---
daily_df = pd.DataFrame({
    "date": pd.to_datetime(Weather_data["daily"]["time"]),
    "Max Temp": Weather_data["daily"]["temperature_2m_max"],
    "Min Temp": Weather_data["daily"]["temperature_2m_min"],
    "UV Index": Weather_data["daily"]["uv_index_max"]
})

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["📊 Hourly Charts", "📅 Daily Charts", "🌈 Weather Insights"])

# --- HOURLY CHARTS ---
with tab1:
    st.subheader("⏱ Hourly Weather Charts")
    colA, colB = st.columns(2)
    start_dt = pd.to_datetime(f"{colA.date_input('Start Date', value=hourly_df['datetime'].min().date(), key='hourly_start')} {colA.time_input('Start Time', value=hourly_df['datetime'].min().time(), key='hourly_start_time')}")
    end_dt = pd.to_datetime(f"{colB.date_input('End Date', value=hourly_df['datetime'].max().date(), key='hourly_end')} {colB.time_input('End Time', value=hourly_df['datetime'].max().time(), key='hourly_end_time')}")
    hourly_filtered = hourly_df[(hourly_df["datetime"] >= start_dt) & (hourly_df["datetime"] <= end_dt)]

    if hourly_filtered.empty:
        st.warning("⚠ No data for the selected time range.")
    else:
        st.subheader("🌡 Temperature & Apparent Temperature")
        st.line_chart(hourly_filtered.set_index("datetime")[["Temperature", "Apparent Temp"]], height=300)

        st.subheader("🌧 Rainfall")
        st.bar_chart(hourly_filtered.set_index("datetime")[["Rain"]], height=250)

        st.subheader("💨 Wind Speed")
        st.line_chart(hourly_filtered.set_index("datetime")[["Wind Speed"]], height=250)

        st.subheader("💧 Humidity")
        st.line_chart(hourly_filtered.set_index("datetime")[["Humidity"]], height=250)

# --- DAILY CHARTS ---
with tab2:
    st.subheader("📅 Daily Weather Charts")
    start_day = st.date_input("Start Date", value=daily_df["date"].min().date(), key="daily_start")
    end_day = st.date_input("End Date", value=daily_df["date"].max().date(), key="daily_end")
    daily_filtered = daily_df[(daily_df["date"] >= pd.to_datetime(start_day)) & (daily_df["date"] <= pd.to_datetime(end_day))]

    if daily_filtered.empty:
        st.warning("⚠ No data for selected date range.")
    else:
        st.subheader("🌡 Temperature Range")
        st.area_chart(daily_filtered.set_index("date")[["Min Temp", "Max Temp"]], height=300)

        st.subheader("☀️ Daily UV Index")
        st.bar_chart(daily_filtered.set_index("date")[["UV Index"]], height=200)

        st.download_button(
            "⬇ Download Daily CSV",
            daily_filtered.to_csv(index=False).encode("utf-8"),
            file_name=f"{selected_city}_daily_weather.csv"
        )

# --- WEATHER INSIGHTS / ALERTS ---
with tab3:
    st.subheader("⚠ Weather Insights & Alerts")
    latest_temp = curr['temperature']
    latest_wind = curr['windspeed']
    latest_uv = Weather_data['daily']['uv_index_max'][0]

    if latest_uv > 7:
        st.warning("☀️ UV Alert: High UV index! Wear sunscreen.")
    if latest_temp > 35:
        st.warning("🔥 Heat Alert: Stay hydrated!")
    elif latest_temp < 5:
        st.warning("❄️ Cold Alert: Dress warmly!")
    if latest_wind > 30:
        st.warning("💨 Wind Alert: Strong winds, secure loose objects!")

    st.subheader("💡 Quick Weather Tips")
    if latest_temp > 25 and latest_uv > 5:
        st.write("- Wear sunscreen and light clothing.")
    elif latest_temp < 10:
        st.write("- Wear warm clothing and layers.")
    if latest_wind > 20:
        st.write("- Be cautious of high winds.")
    if Weather_data['hourly']['rain'][0] > 0:
        st.write("- Carry an umbrella or raincoat.")
    if latest_humidity := Weather_data['hourly']['relativehumidity_2m'][0] > 80:
        st.write("- High humidity: Stay cool and hydrated.")

    st.subheader("🌤 General Weather Safety Tips")
    st.write("- Check hourly updates for sudden weather changes.")
    st.write("- Follow local weather advisories for safety.")
    st.write("- Use weather apps for real-time notifications.")
    st.write("- Plan outdoor activities considering the weather forecast.")
    st.write("- Keep an eye on temperature fluctuations throughout the day.")
    st.write("- Dress appropriately for the weather conditions.")
    st.write("- Stay informed about weather patterns in your area.")
    st.write("- Take necessary precautions during extreme weather conditions.")
    st.write("- Ensure proper ventilation during high humidity conditions.")
    st.write("- Protect yourself from UV exposure during peak hours.")
    st.write("- Stay indoors during severe weather warnings.")
    st.write("- Regularly check weather updates before traveling.")
    st.write("- Maintain hydration in hot weather conditions.")
    st.write("- Use layered clothing to adapt to changing temperatures.")
