import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Weather Time",
    layout="wide"
)

# ---------------- SESSION STATE INIT ----------------
st.session_state.setdefault("ui_mode", "Laptop")
st.session_state.setdefault("continent", "Asia")
st.session_state.setdefault("city", "Colombo, Sri Lanka")
st.session_state.setdefault("unit", "Celsius")  # New: Temperature Unit
st.session_state.setdefault("show_hourly", True)
st.session_state.setdefault("show_daily", True)
st.session_state.setdefault("splash_done", False)
st.session_state.setdefault("last_ui_mode", st.session_state.ui_mode)
st.session_state.setdefault("favorite_cities", [])

# ---------------- SPLASH SCREEN ----------------
def show_splash():
    splash_html = """
    <style>
    .splash {
        position: fixed;
        inset: 0;
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: white;
        z-index: 9999;
        animation: fadeOut 1s ease-in-out forwards;
        animation-delay: 2.5s;
    }
    @keyframes fadeOut { to { opacity: 0; visibility: hidden; } }
    .icon { font-size: 90px; animation: float 2s ease-in-out infinite; }
    @keyframes float {0% {transform: translateY(0);} 50% {transform: translateY(-15px);} 100% {transform: translateY(0);} }
    .title { font-size: 38px; font-weight: bold; }
    .subtitle { opacity: 0.8; }
    </style>
    <div class="splash">
        <div class="icon">🌦</div>
        <div class="title">Weather Time</div>
        <div class="subtitle">Preparing your view...</div>
    </div>
    """
    placeholder = st.empty()
    placeholder.markdown(splash_html, unsafe_allow_html=True)
    time.sleep(2.5)
    placeholder.empty()

# Trigger splash
if not st.session_state.splash_done or st.session_state.ui_mode != st.session_state.last_ui_mode:
    show_splash()
    st.session_state.splash_done = True
    st.session_state.last_ui_mode = st.session_state.ui_mode

# ---------------- HEADER ----------------
st.title("🌦 Weather Time")
st.caption("Your personal real-time weather assistant")
st.markdown("---")
st.caption("Version 1.2")

# ---------------- UI MODE ----------------
st.sidebar.markdown("### 📱 UI Mode")
new_ui = st.sidebar.radio(
    "Select UI Mode",
    ["Laptop", "Mobile"],
    index=["Laptop", "Mobile"].index(st.session_state.ui_mode)
)
if new_ui != st.session_state.ui_mode:
    st.session_state.ui_mode = new_ui
    st.session_state.splash_done = False
    st.rerun()

show_sidebar = st.session_state.ui_mode == "Laptop"

# ---------------- TEMPERATURE UNIT ----------------
st.sidebar.markdown("### 🌡 Temperature Unit")
unit = st.sidebar.radio("Select Unit", ["Celsius", "Fahrenheit"], index=["Celsius","Fahrenheit"].index(st.session_state.unit))
st.session_state.unit = unit

def convert_temp(celsius):
    if st.session_state.unit == "Celsius":
        return celsius
    else:
        return round((celsius * 9/5) + 32, 1)

# ---------------- CONTINENTS ----------------
continents = {
    "Custom Coordinates": {"Custom Coordinates": (0.0, 0.0)},
    "North America": {"New York, USA": (40.7128, -74.0060), "Toronto, Canada": (43.6532, -79.3832), "Los Angeles, USA": (34.0522, -118.2437)},
    "Europe": {"London, UK": (51.5074, -0.1278), "Berlin, Germany": (52.52, 13.41), "Paris, France": (48.8566, 2.3522)},
    "Asia": {"Tokyo, Japan": (35.6895, 139.6917), "Delhi, India": (28.6139, 77.2090), "Colombo, Sri Lanka": (6.9271, 79.8612)},
    "Africa": {"Cairo, Egypt": (30.0444, 31.2357), "Lagos, Nigeria": (6.5244, 3.3792)}
}

# ---------------- LOCATION SELECT ----------------
def safe_city_index(city, cities_list):
    return cities_list.index(city) if city in cities_list else 0

if show_sidebar:
    st.sidebar.markdown("### 🌍 Location")
    st.session_state.continent = st.sidebar.selectbox(
        "Select Continent",
        list(continents.keys()),
        index=safe_city_index(st.session_state.continent, list(continents.keys()))
    )
    cities = list(continents[st.session_state.continent].keys())
    st.session_state.city = st.sidebar.selectbox(
        "Select City",
        cities,
        index=safe_city_index(st.session_state.city, cities)
    )
    st.sidebar.subheader("⭐ Favorite Cities")
    col1, col2 = st.columns(2)
    with col1:
        city_input = st.sidebar.text_input("Add a city", "")
    with col2:
        if st.sidebar.button("Add to Favorites") and city_input.strip():
            st.session_state.favorite_cities.append(city_input.strip())
    if st.session_state.favorite_cities:
        st.sidebar.write(", ".join(st.session_state.favorite_cities))
else:
    st.subheader("🌍 Location")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.continent = st.selectbox(
            "Continent",
            list(continents.keys()),
            index=safe_city_index(st.session_state.continent, list(continents.keys())),
            label_visibility="collapsed"
        )
    cities = list(continents[st.session_state.continent].keys())
    with col2:
        st.session_state.city = st.selectbox(
            "City",
            cities,
            index=safe_city_index(st.session_state.city, cities),
            label_visibility="collapsed"
        )

    st.subheader("⭐ Favorite Cities")
    col1, col2 = st.columns(2)
    with col1:
        city_input = st.text_input("Add a city", "")
    with col2:
        if st.button("Add to Favorites") and city_input.strip():
            st.session_state.favorite_cities.append(city_input.strip())
    if st.session_state.favorite_cities:
        st.write(", ".join(st.session_state.favorite_cities))


# ---------------- COORDINATES ----------------
if st.session_state.city == "Custom Coordinates":
    lat = st.number_input("Latitude", value=0.0, format="%.6f")
    lon = st.number_input("Longitude", value=0.0, format="%.6f")
else:
    lat, lon = continents[st.session_state.continent][st.session_state.city]

if lat == 0.0 and lon == 0.0:
    st.warning("⚠ Please select valid coordinates or city.")
    st.stop()

# ---------------- WEATHER API ----------------
@st.cache_data(ttl=600)
def fetch_weather(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&"
        "current_weather=true&hourly=temperature_2m,precipitation,wind_speed_10m,relativehumidity_2m&"
        "daily=temperature_2m_max,temperature_2m_min,uv_index_max,precipitation_sum&timezone=auto"
    )
    return requests.get(url, timeout=10).json()

with st.spinner("🌦 Fetching weather data..."):
    data = fetch_weather(lat, lon)

curr = data.get("current_weather", {})
hourly = data.get("hourly", {})
daily = data.get("daily", {})

# ---------------- SAFE HELPER ----------------
def safe(lst, i=0, d=0):
    try: return lst[i]
    except: return d

# ---------------- METRICS ----------------
temperature_c = curr.get("temperature")
temperature = convert_temp(temperature_c)
wind = curr.get("windspeed")
rain_now = safe(hourly.get("precipitation"))
uv_today = safe(daily.get("uv_index_max"))

st.info("🧠 AI Weather Summary: " + ("🌧 Rain expected. " if rain_now>0 else "☀️ No rain. ") + ("🔥 Hot. " if temperature_c and temperature_c>30 else ""))

st.subheader("🌟 Current Weather")
c1, c2, c3, c4 = st.columns(4)
unit_symbol = "°C" if st.session_state.unit=="Celsius" else "°F"
c1.metric("🌡 Temp", f"{temperature} {unit_symbol}")
c2.metric("💨 Wind", f"{wind} km/h")
c3.metric("💧 Humidity", f"{safe(hourly.get('relativehumidity_2m'))}%")
c4.metric("🌧 Rain", f"{rain_now} mm")

# ---------------- CLOTHING ----------------
st.subheader("👕 Clothing Recommendation")
clothing = []
if temperature_c >= 32: clothing.append("🩳 Light clothing")
elif temperature_c >= 22: clothing.append("👕 Comfortable wear")
else: clothing.append("🧥 Jacket recommended")
if rain_now > 1: clothing.append("☔ Umbrella")
if wind > 25: clothing.append("🧢 Windbreaker")
if uv_today > 7: clothing.append("🕶 Sunscreen")
st.success(" • ".join(clothing))

# ---------------- PRECIPITATION ----------------
st.subheader("🌧 Precipitation Details")
rain_today = safe(daily.get("precipitation_sum", []))
p1, p2, p3 = st.columns(3)
p1.metric("Now", f"{rain_now} mm")
p2.metric("Today", f"{rain_today} mm")
if rain_now==0: intensity="☀️ No Rain"
elif rain_now<1: intensity="🌦 Light"
elif rain_now<5: intensity="🌧 Moderate"
else: intensity="⛈ Heavy"
p3.metric("Intensity", intensity)

# ---------------- DATAFRAMES ----------------
hourly_df = pd.DataFrame({
    "Time": pd.to_datetime(hourly.get("time", [])),
    "Temp": [convert_temp(t) for t in hourly.get("temperature_2m", [])],
    "Rain": hourly.get("precipitation", []),
    "Wind": hourly.get("wind_speed_10m", [])
})
daily_df = pd.DataFrame({
    "Date": pd.to_datetime(daily.get("time", [])),
    "Min Temp": [convert_temp(t) for t in daily.get("temperature_2m_min", [])],
    "Max Temp": [convert_temp(t) for t in daily.get("temperature_2m_max", [])],
    "UV": daily.get("uv_index_max", [])
})

# ---------------- CHART TOGGLES ----------------
if show_sidebar:
    st.sidebar.markdown("### 📊 Chart Controls")
    st.session_state.show_charts_on = st.sidebar.checkbox("Show Charts", value=True)
else:
    with st.expander("📊 Chart Controls"):
        st.session_state.show_charts_on = st.checkbox("Show Charts", value=True)

# ---------------- TABS ----------------
tab1, tab2, tab3 = st.tabs(["📊 Hourly Charts","📅 Daily Charts","⚠ Alerts & Tips"])

with tab1:
    st.subheader("📊 Hourly Temperature")
    if st.session_state.show_charts_on:
        st.line_chart(hourly_df.set_index("Time")[["Temp"]])
        st.subheader("🌧 Hourly Rainfall")
        st.bar_chart(hourly_df.set_index("Time")[["Rain"]])
        st.subheader("💨 Hourly Wind Speed")
        st.line_chart(hourly_df.set_index("Time")[["Wind"]])
    else: st.info("Hourly charts are hidden")

with tab2:
    st.subheader("📅 Daily Temperature")
    if st.session_state.show_charts_on:
        st.area_chart(daily_df.set_index("Date")[["Min Temp","Max Temp"]])
        st.subheader("☀️ Daily UV Index")
        st.bar_chart(daily_df.set_index("Date")[["UV"]])
    else: st.info("Daily charts are hidden")

with tab3:
    if uv_today>7: st.warning("☀️ High UV today")
    if temperature_c>35: st.warning("🔥 Extreme heat")
    if wind>30: st.warning("💨 Strong winds")
    st.markdown("### 💡 Tips")
    st.write("- Stay hydrated")
    st.write("- Dress smart")
    st.write("- Check updates hourly")

# ---------------- FAVORITE CITIES ----------------
st.subheader("⭐ Favorite Cities")
col1, col2 = st.columns(2)
with col1:
    city_input = st.text_input("Add a city", "")
with col2:
    if st.button("Add to Favorites") and city_input.strip():
        st.session_state.favorite_cities.append(city_input.strip())
if st.session_state.favorite_cities:
    st.write(", ".join(st.session_state.favorite_cities))
