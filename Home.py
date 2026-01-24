import streamlit as st
import requests
import os
import pandas as pd
import json
from datetime import datetime

# 1. PAGE CONFIG & UI
st.set_page_config(page_title="WeatherTime Pro", layout="wide", page_icon="🌍")

def apply_ui():
    css_path = os.path.join("assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

apply_ui()

# 2. MASTER STATE INIT
if "city_name" not in st.session_state: st.session_state.city_name = "Colombo"
if "weather_data" not in st.session_state: st.session_state.weather_data = None

# --- LOCAL INTELLIGENCE DATABASE (For Autocomplete) ---
# This list makes the dropdown "smart" instantly without waiting for an API
POPULAR_CITIES = [
    "Amsterdam, Netherlands", "Athens, Greece", "Austin, USA", "Abu Dhabi, UAE",
    "Bangkok, Thailand", "Beijing, China", "Berlin, Germany", "Boston, USA",
    "Cairo, Egypt", "Cape Town, South Africa", "Chicago, USA", "Colombo, Sri Lanka",
    "Delhi, India", "Dubai, UAE", "Dublin, Ireland",
    "Frankfurt, Germany", 
    "Galle, Sri Lanka", "Geneva, Switzerland",
    "Hong Kong", "Houston, USA",
    "Istanbul, Turkey",
    "Jakarta, Indonesia", 
    "Kandy, Sri Lanka", "Kyoto, Japan",
    "London, UK", "Los Angeles, USA", "Lisbon, Portugal",
    "Madrid, Spain", "Maranello, Italy", "Melbourne, Australia", "Mumbai, India", "Moscow, Russia",
    "New York, USA", "Nairobi, Kenya",
    "Osaka, Japan", "Oslo, Norway",
    "Paris, France", "Porscheplatz (Stuttgart), Germany",
    "Rome, Italy", "Rio de Janeiro, Brazil",
    "San Francisco, USA", "Seoul, South Korea", "Shanghai, China", "Singapore", "Stuttgart, Germany", "Sydney, Australia",
    "Tokyo, Japan", "Toronto, Canada",
    "Vancouver, Canada",
    "Zurich, Switzerland"
]

# 3. ADVANCED DATA ENGINE
def get_weather_intel(search_term):
    # Extract just the city name if "City, Country" is selected
    city = search_term.split(",")[0]
    
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        geo_res = requests.get(geo_url).json()
        if not geo_res.get("results"): return None
        
        loc = geo_res["results"][0]
        # Full Telemetry URL
        w_url = f"https://api.open-meteo.com/v1/forecast?latitude={loc['latitude']}&longitude={loc['longitude']}&current_weather=true&hourly=temperature_2m,relativehumidity_2m,apparent_temperature,pressure_msl,visibility,precipitation&daily=uv_index_max,sunrise,sunset&timezone=auto"
        
        return {
            "name": loc["name"], 
            "lat": loc["latitude"], 
            "lon": loc["longitude"], 
            "country": loc.get("country", ""),
            "data": requests.get(w_url).json()
        }
    except: return None

# 4. SIDEBAR NAVIGATION
with st.sidebar:
    st.markdown("## 🛰️ Global Search")
    
    # THE NEW AUTOCOMPLETE WIDGET
    # selectbox acts like a search bar. You type, it filters the list.
    selected_city = st.selectbox(
        "Select Node Location", 
        options=POPULAR_CITIES,
        index=POPULAR_CITIES.index("Colombo, Sri Lanka") if "Colombo, Sri Lanka" in POPULAR_CITIES else 0,
        placeholder="Type to search..."
    )
    
    # Custom Override: In case they want a city NOT in our list
    st.markdown("---")
    custom_search = st.text_input("Or type manual city:", placeholder="e.g. Jaffna")

    if st.button("Sync Data Node", use_container_width=True):
        # Prioritize manual text if typed, otherwise use the dropdown
        target = custom_search if custom_search else selected_city
        st.session_state.city_name = target
        st.rerun()

# 5. MAIN HUB LOGIC
payload = get_weather_intel(st.session_state.city_name)

if payload:
    st.session_state.weather_data = payload['data']
    st.session_state.loc_data = payload 
    w = payload['data']
    curr = w['current_weather']
    
    st.markdown(f'<h1 class="city-title">{payload["name"]}, {payload["country"]}</h1>', unsafe_allow_html=True)
    
    # EXPANDED METRICS
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("Feels Like", f"{w['hourly']['apparent_temperature'][0]}°C")
    with m2: st.metric("Pressure", f"{w['hourly']['pressure_msl'][0]} hPa")
    with m3: st.metric("Visibility", f"{w['hourly']['visibility'][0] / 1000} km")
    with m4: st.metric("Humidity", f"{w['hourly']['relativehumidity_2m'][0]}%")

    # GEOGRAPHIC SURVEILLANCE MAP
    st.markdown("---")
    st.subheader("📍 Geospatial Node")
    map_df = pd.DataFrame({'lat': [payload['lat']], 'lon': [payload['lon']]})
    st.map(map_df, zoom=10, size=20)

    # 24H TELEMETRY CHART
    st.markdown("---")
    st.subheader("📊 24-Hour Telemetry")
    df = pd.DataFrame({
        "Time": pd.to_datetime(w['hourly']['time'][:24]),
        "Actual": w['hourly']['temperature_2m'][:24],
        "Feels Like": w['hourly']['apparent_temperature'][:24]
    }).set_index("Time")
    st.area_chart(df, color=["#38bdf8", "#f472b6"])

else:
    st.error(f"Node connection to '{st.session_state.city_name}' failed.")

# CHANGELOG
st.markdown("---")
if os.path.exists("changelog.json"):
    with open("changelog.json", "r") as f:
        data = json.load(f)
        for entry in data:
            with st.expander(f"🚀 v{entry['version']} — {entry['date']}"):
                for n in entry['notes']: st.markdown(f"• {n}")

st.caption(f"v1.2.3.5.1 | Autocomplete Active | {datetime.now().strftime('%H:%M:%S')}")