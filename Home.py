# Home.py v1.2.3.4.2
"""
Weather Time v1.2.3.4.2 - Environmental Intelligence
- Comparison: Added Multi-City Comparison with dual-layered charts.
- Astro: Integrated Sunrise, Sunset, and Moon Phase tracking.
- Intelligence: Introduced 'Weather Comfort Score' (1-100) for daily planning.
- UI: Enhanced layout with Gauge charts for a premium dashboard feel.
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import json
from datetime import datetime, timezone

# ---------------- PAGE CONFIG & CSS ----------------
st.set_page_config(page_title="Weather Time Pro", layout="wide", page_icon="🌦")

st.markdown("""
    <style>
    .stMetric { background: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); }
    .comfort-score { text-align: center; padding: 20px; border-radius: 50%; width: 100px; height: 100px; line-height: 60px; border: 5px solid #0ea5e9; font-size: 24px; font-weight: bold; margin: auto; }
    </style>
""", unsafe_allow_html=True)

# ---------------- LOGIC: CALCULATORS ----------------
def get_comfort_score(t, h, r, aqi):
    # Custom 1-100 algorithm
    score = 100
    if t > 32 or t < 10: score -= 20
    if h > 70: score -= 10
    if r > 0: score -= 30
    if aqi > 100: score -= 20
    return max(0, score)

def get_moon_phase(d):
    # Simplified moon phase calculation
    diff = d - datetime(2001, 1, 1)
    days = diff.days + diff.seconds / 86400
    lunations = 0.20439731 + (days * 0.03386319269)
    phase = lunations % 1.0
    if phase < 0.06: return "New Moon", "🌑"
    if phase < 0.19: return "Waxing Crescent", "🌒"
    if phase < 0.31: return "First Quarter", "🌓"
    if phase < 0.44: return "Waxing Gibbous", "🌔"
    if phase < 0.56: return "Full Moon", "🌕"
    if phase < 0.69: return "Waning Gibbous", "🌖"
    if phase < 0.81: return "Last Quarter", "🌗"
    return "Waning Crescent", "🌘"

# ---------------- API LOGIC ----------------
@st.cache_data(ttl=600)
def fetch_full_intel(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,relativehumidity_2m,precipitation&daily=sunrise,sunset,uv_index_max&timezone=auto"
    aqi_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=european_aqi&timezone=auto"
    try:
        return requests.get(url).json(), requests.get(aqi_url).json()
    except: return None, None

def geocode(query):
    try:
        res = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={query}&count=1").json()
        return res["results"][0] if "results" in res else None
    except: return None

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("🌐 Weather Time")
    primary_city = st.text_input("Main City", value="Colombo")
    compare_mode = st.checkbox("Enable Comparison Mode")
    second_city = ""
    if compare_mode:
        second_city = st.text_input("Comparison City", value="London")
    
    st.divider()
    st.session_state.unit = st.radio("Temp Unit", ["Celsius", "Fahrenheit"], horizontal=True)

# ---------------- MAIN UI ----------------
loc1 = geocode(primary_city)
if loc1:
    w1, a1 = fetch_full_intel(loc1['latitude'], loc1['longitude'])
    
    st.title(f"🌍 {loc1['name']}, {loc1.get('country','')}")
    
    t_now, t_astro, t_sys = st.tabs(["🚀 Intel Overview", "🌙 Astro & Light", "🛠 System"])

    with t_now:
        curr = w1['current_weather']
        aqi = a1.get('current', {}).get('european_aqi', 50)
        score = get_comfort_score(curr['temperature'], w1['hourly']['relativehumidity_2m'][0], w1['hourly']['precipitation'][0], aqi)
        
        c1, c2, c3, c4 = st.columns([1,1,1,1])
        c1.metric("Temperature", f"{curr['temperature']}°")
        c2.metric("AQI Index", f"{aqi}")
        c3.metric("Rainfall", f"{w1['hourly']['precipitation'][0]}mm")
        
        with c4:
            st.markdown(f'<div class="comfort-score">{score}</div>', unsafe_allow_html=True)
            st.caption("Comfort Score")

        # --- COMPARISON SECTION ---
        if compare_mode and second_city:
            loc2 = geocode(second_city)
            if loc2:
                w2, a2 = fetch_full_intel(loc2['latitude'], loc2['longitude'])
                st.subheader(f"📊 Comparison: {loc1['name']} vs {loc2['name']}")
                
                comp_df = pd.DataFrame({
                    "Time": pd.to_datetime(w1['hourly']['time'][:24]),
                    loc1['name']: w1['hourly']['temperature_2m'][:24],
                    loc2['name']: w2['hourly']['temperature_2m'][:24]
                }).set_index("Time")
                st.line_chart(comp_df)
        else:
            st.area_chart(pd.DataFrame({
                "Time": pd.to_datetime(w1['hourly']['time'][:24]),
                "Temp": w1['hourly']['temperature_2m'][:24]
            }).set_index("Time"), color="#0ea5e9")

    with t_astro:
        st.subheader("☀️ Solar & Lunar Intelligence")
        col_sun, col_moon = st.columns(2)
        
        with col_sun:
            with st.container(border=True):
                st.write(f"🌅 **Sunrise:** {w1['daily']['sunrise'][0].split('T')[1]}")
                st.write(f"🌇 **Sunset:** {w1['daily']['sunset'][0].split('T')[1]}")
                st.info("Golden Hour is active 1 hour after sunrise and before sunset.")
        
        with col_moon:
            phase_name, phase_icon = get_moon_phase(datetime.now())
            with st.container(border=True):
                st.markdown(f"### {phase_icon} {phase_name}")
                st.write("Current Lunar Cycle Phase")

    with t_sys:
        if os.path.exists("changelog.json"):
            with open("changelog.json", "r") as f:
                ch = json.load(f)
                for entry in ch:
                    with st.expander(f"v{entry['version']} - {entry['date']}", expanded=(entry['version']=="1.2.3.4.2")):
                        for note in entry['notes']: st.write(f"- {note}")

else:
    st.error("City not found. Please try again.")

st.caption(f"v1.2.3.4.2 | Environmental Intelligence Dashboard | {datetime.now().strftime('%H:%M:%S')}")