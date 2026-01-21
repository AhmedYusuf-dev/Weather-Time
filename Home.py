# Home.py v1.2.3.4.1
"""
Weather Time v1.2.3.4.1
- Fix: NameError (os) and KeyError (hourly/current) resolved.
- UI: Card-style metrics with Glassmorphism and professional Tab navigation.
- Charts: Integrated Plotly Radar and Area charts for deep analytics.
- Intelligence: Real-time AQI, PM2.5, and Pollen tracking.
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import json
from datetime import datetime

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Weather Time Pro", layout="wide", page_icon="🌦")

# ---------------- CUSTOM CSS (UI IMPROVEMENTS) ----------------
def apply_ui_design():
    st.markdown("""
        <style>
        /* Card Styling */
        div[data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        /* Tab Styling */
        .stTabs [data-baseweb="tab-list"] { gap: 10px; }
        .stTabs [data-baseweb="tab"] {
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 8px 8px 0 0;
            padding: 10px 20px;
        }
        </style>
    """, unsafe_allow_html=True)

# ---------------- LOGIC TOOLS ----------------
class WeatherConverter:
    @staticmethod
    def temp(c):
        if c is None: return "N/A"
        return round(c, 1) if st.session_state.get('unit') == "Celsius" else round((c * 9/5) + 32, 1)

@st.cache_data(ttl=600)
def fetch_weather_intel(lat, lon):
    # FIXED: Added explicit hourly and current parameters to prevent KeyErrors
    w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,relativehumidity_2m,precipitation&daily=uv_index_max&timezone=auto"
    a_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=european_aqi,pollen_birch,pollen_grass&hourly=pm10,pm2_5&timezone=auto"
    try:
        w_res = requests.get(w_url).json()
        a_res = requests.get(a_url).json()
        return w_res, a_res
    except: return None, None

def get_radar_chart(temp, hum, wind, uv, rain):
    categories = ['Temp', 'Humidity', 'Wind', 'UV Index', 'Rain']
    # Normalizing 0-100 for visual consistency
    values = [min(temp*2, 100), hum, min(wind*2, 100), min(uv*10, 100), min(rain*10, 100)]
    fig = go.Figure(data=go.Scatterpolar(r=values, theta=categories, fill='toself', marker=dict(color='#0ea5e9')))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, height=350,
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
    return fig

# ---------------- SIDEBAR & SEARCH ----------------
apply_ui_design()
with st.sidebar:
    st.title("🌐 Weather Time")
    query = st.text_input("Global Search", placeholder="London, Kandy, New York...", value="Colombo")
    st.divider()
    st.session_state.unit = st.radio("Temp Unit", ["Celsius", "Fahrenheit"], horizontal=True)
    if st.button("Refresh Cache"): st.cache_data.clear()

def geocode(q):
    try:
        res = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={q}&count=1").json()
        return res["results"][0] if "results" in res else None
    except: return None

loc = geocode(query)
if loc:
    lat, lon, city_display = loc['latitude'], loc['longitude'], f"{loc['name']}, {loc.get('country','')}"
else:
    lat, lon, city_display = 6.9271, 79.8612, "Colombo, Sri Lanka"

# ---------------- DASHBOARD ----------------
w_data, a_data = fetch_weather_intel(lat, lon)

if w_data and a_data:
    # DEFENSIVE CODING: Using .get() prevents KeyError crashes
    curr_w = w_data.get('current_weather', {})
    curr_a = a_data.get('current', {})
    hourly_a = a_data.get('hourly', {})

    st.title(f"🌍 {city_display}")
    
    t1, t2, t3, t4 = st.tabs(["🚀 Live Dashboard", "📊 Analytics", "🧪 Air Quality", "🛠 System"])

    with t1:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Temperature", f"{WeatherConverter.temp(curr_w.get('temperature'))}°")
        c2.metric("AQI (Europe)", f"{curr_a.get('european_aqi', 'N/A')}")
        c3.metric("Rainfall", f"{w_data['hourly']['precipitation'][0]}mm")
        c4.metric("Humidity", f"{w_data['hourly']['relativehumidity_2m'][0]}%")

        col_radar, col_map = st.columns([1, 1])
        with col_radar:
            st.subheader("5-Factor Intelligence")
            st.plotly_chart(get_radar_chart(curr_w.get('temperature', 20), 
                                             w_data['hourly']['relativehumidity_2m'][0], 
                                             curr_w.get('windspeed', 0), 
                                             w_data['daily']['uv_index_max'][0], 
                                             w_data['hourly']['precipitation'][0]), use_container_width=True)
        with col_map:
            st.subheader("📍 Interactive Map")
            st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}), zoom=9)

    with t2:
        st.subheader("24-Hour Interactive Trend")
        df_trends = pd.DataFrame({
            "Time": pd.to_datetime(w_data['hourly']['time'][:24]),
            "Temp": [WeatherConverter.temp(t) for t in w_data['hourly']['temperature_2m'][:24]]
        })
        fig = px.area(df_trends, x="Time", y="Temp", color_discrete_sequence=['#0ea5e9'])
        st.plotly_chart(fig, use_container_width=True)

    with t3:
        st.subheader("🌫 Pollutant Trends")
        if hourly_a:
            df_aqi = pd.DataFrame({
                "Time": pd.to_datetime(hourly_a.get('time', [])[:48]),
                "PM2.5": hourly_a.get('pm2_5', [])[:48],
                "PM10": hourly_a.get('pm10', [])[:48]
            }).set_index("Time")
            st.line_chart(df_aqi)
        
        st.subheader("🍃 Live Pollen Tracker")
        st.write(f"**Birch Pollen:** {curr_a.get('pollen_birch', 0)} | **Grass Pollen:** {curr_a.get('pollen_grass', 0)}")

    with t4:
        st.subheader("📜 Dynamic Changelog")
        if os.path.exists("changelog.json"):
            with open("changelog.json", "r") as f:
                ch_data = json.load(f)
                for entry in ch_data:
                    with st.expander(f"v{entry['version']} - {entry['date']}"):
                        for note in entry['notes']: st.write(f"- {note}")

else:
    st.error("Intelligence synchronization failed. Verify API availability.")

st.caption(f"v1.2.3.4.1 | {datetime.now().strftime('%Y-%m-%d')} | Weather Time Intelligence")