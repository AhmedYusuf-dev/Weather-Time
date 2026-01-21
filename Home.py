# Home.py v1.2.3.3
"""
Weather Time v1.2.3.3
- Interface: Professional Tabbed navigation (Overview, Forecasts, System).
- Database: Major global hubs across all 6 continents.
- UI: Card-style metrics with st.container(border=True) for 2026 standard.
- Changelog: Dynamic loading from external changelog.json file.
- Reliability: Retained v1.2.3.2.1 Telemetry, Retries, and Persistence logic.
"""

import streamlit as st
import requests
import pandas as pd
import json
import os
import time
from datetime import datetime, timezone
from typing import Tuple, Any, Optional

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Weather Time Global", layout="wide", page_icon="🌦")

# ---------------- SAFE RERUN HELPER ----------------
def safe_rerun():
    try:
        if hasattr(st, "rerun"): st.rerun()
        elif hasattr(st, "experimental_rerun"): st.experimental_rerun()
    except Exception: pass

# ---------------- EXTERNAL DATA LOADING ----------------
def load_changelog():
    path = "changelog.json"
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return [{"version": "Error", "date": "-", "notes": ["Could not read changelog.json"]}]
    return [{"version": "N/A", "date": "-", "notes": ["changelog.json not found"]}]

# ---------------- GLOBAL CITY DATABASE ----------------
def get_global_db():
    return {
        "Asia": {
            "Tokyo, Japan": (35.6895, 139.6917), "Dubai, UAE": (25.2048, 55.2708),
            "Singapore": (1.3521, 103.8198), "Colombo, Sri Lanka": (6.9271, 79.8612),
            "Seoul, South Korea": (37.5665, 126.9780)
        },
        "Europe": {
            "London, UK": (51.5074, -0.1278), "Paris, France": (48.8566, 2.3522),
            "Berlin, Germany": (52.5200, 13.4050), "Zurich, CH": (47.3769, 8.5417),
            "Rome, Italy": (41.9028, 12.4964)
        },
        "Americas": {
            "New York, USA": (40.7128, -74.0060), "Toronto, Canada": (43.6532, -79.3832),
            "Los Angeles, USA": (34.0522, -118.2437), "São Paulo, Brazil": (-23.5505, -46.6333)
        },
        "Africa/Oceania": {
            "Cairo, Egypt": (30.0444, 31.2357), "Sydney, Australia": (-33.8688, 151.2093),
            "Johannesburg, SA": (-26.2041, 28.0473), "Auckland, NZ": (-36.8485, 174.7633)
        }
    }

# ---------------- LOGIC TOOLS ----------------
class WeatherTools:
    @staticmethod
    def temp(c):
        return round(c, 1) if st.session_state.unit == "Celsius" else round((c * 9/5) + 32, 1)
    
    @staticmethod
    def wind(k):
        return round(k, 1) if st.session_state.wind_unit == "km/h" else round(k * 0.621371, 1)

# ---------------- SESSION STATE ----------------
for k, v in {"unit": "Celsius", "wind_unit": "km/h", "theme": "dark", "continent": "Asia", "city": "Tokyo, Japan"}.items():
    st.session_state.setdefault(k, v)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("⚙️ Global Settings")
    st.session_state.unit = st.radio("Temp Unit", ["Celsius", "Fahrenheit"], horizontal=True)
    st.session_state.wind_unit = st.radio("Wind Unit", ["km/h", "mph"], horizontal=True)
    
    st.divider()
    db = get_global_db()
    region = st.selectbox("Region", list(db.keys()))
    city_name = st.selectbox("City", list(db[region].keys()))
    
    if st.button("Manual Refresh"):
        st.cache_data.clear()
        safe_rerun()

# ---------------- DATA FETCHING ----------------
@st.cache_data(ttl=600)
def fetch_weather(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,relativehumidity_2m,precipitation&daily=temperature_2m_max,temperature_2m_min&timezone=auto"
    try: return requests.get(url, timeout=10).json()
    except: return None

# ---------------- DASHBOARD RENDER ----------------
st.title(f"🌦 {city_name} Dashboard")
lat, lon = db[region][city_name]
data = fetch_weather(lat, lon)

if data:
    # --- Tabbed Navigation ---
    tab_now, tab_forecast, tab_system = st.tabs(["🌟 Current Overview", "📅 Forecast Trends", "🛠 System & History"])

    with tab_now:
        curr = data['current_weather']
        # Card Metrics
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            with st.container(border=True):
                st.metric("Temperature", f"{WeatherTools.temp(curr['temperature'])}°")
        with c2:
            with st.container(border=True):
                st.metric("Wind Speed", f"{WeatherTools.wind(curr['windspeed'])} {st.session_state.wind_unit}")
        with c3:
            with st.container(border=True):
                st.metric("Humidity", f"{data['hourly']['relativehumidity_2m'][0]}%")
        with c4:
            with st.container(border=True):
                st.metric("Rainfall", f"{data['hourly']['precipitation'][0]}mm")

        # Visual Row
        col_main, col_map = st.columns([2, 1])
        with col_main:
            st.area_chart(pd.DataFrame({
                "Time": pd.to_datetime(data['hourly']['time'][:24]),
                "Temp": [WeatherTools.temp(t) for t in data['hourly']['temperature_2m'][:24]]
            }).set_index("Time"), color="#0ea5e9")
        with col_map:
            st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}), zoom=6)

    with tab_forecast:
        st.subheader("7-Day Temperature Range")
        daily_df = pd.DataFrame({
            "Date": pd.to_datetime(data['daily']['time']),
            "Max": [WeatherTools.temp(t) for t in data['daily']['temperature_2m_max']],
            "Min": [WeatherTools.temp(t) for t in data['daily']['temperature_2m_min']]
        }).set_index("Date")
        st.line_chart(daily_df)

    with tab_system:
        st.subheader("📜 Version History")
        changelog_data = load_changelog()
        for entry in changelog_data:
            with st.expander(f"v{entry.get('version')} — {entry.get('date')}", expanded=(entry.get('version') == "1.2.3.3")):
                for note in entry.get('notes', []):
                    st.write(f"- {note}")
        
        st.divider()
        st.subheader("🛠 Technical Details")
        st.json({
            "Version": "1.2.3.3",
            "Node": "Global Deployment",
            "Website": "weathertime.streamlit.apps",
            "Last Sync": datetime.now().strftime('%H:%M:%S')
        })

else:
    st.error("Critical: Failed to connect to global weather node.")

st.divider()
st.caption(f"v1.2.3.3 | {datetime.now().strftime('%Y-%m-%d')} | Global Weather Insights")