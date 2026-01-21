# Home.py v1.2.3.4.2.2
"""
Weather Time v1.2.3.4.2.2 - Intelligence & Context Hub
- Stability: Resolved 'KeyError' and 'NameError' with safe .get() methods and explicit imports.
- UI: Premium Glassmorphism Hero Card with dynamic health alerts.
- Intel: Integrated Plotly Radar, AQI, Pollen, and Moon Phase tracking.
- Navigation: Search + Curated Global Recommendations.
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import json
from datetime import datetime

# ---------------- PAGE CONFIG & STYLING ----------------
st.set_page_config(page_title="Weather Time Pro", layout="wide", page_icon="🌍")

def apply_ui_design():
    st.markdown("""
        <style>
        .stApp { background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%); }
        div[data-testid="stMetric"] { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 15px; }
        .hero-card { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(15px); border-radius: 20px; border: 1px solid rgba(255,255,255,0.1); padding: 30px; margin-bottom: 25px; }
        .alert-banner { padding: 10px; border-radius: 8px; border-left: 5px solid #ff4b4b; background: rgba(255, 75, 75, 0.1); color: #ff4b4b; font-weight: bold; margin-bottom: 10px; }
        </style>
    """, unsafe_allow_html=True)

# ---------------- LOGIC: CALCULATORS ----------------
def get_comfort_score(t, h, r, aqi):
    score = 100
    if t > 32 or t < 10: score -= 20
    if h > 70: score -= 10
    if r > 0.5: score -= 25
    if aqi > 80: score -= 15
    return max(0, score)

def get_moon_phase(d):
    diff = d - datetime(2001, 1, 1)
    days = diff.days + diff.seconds / 86400
    phase = (0.20439731 + (days * 0.03386319269)) % 1.0
    if phase < 0.06: return "New Moon", "🌑"
    if phase < 0.50: return "Waxing", "🌓"
    if phase < 0.56: return "Full Moon", "🌕"
    return "Waning", "🌗"

# ---------------- API LOGIC ----------------
@st.cache_data(ttl=600)
def fetch_weather_intel(lat, lon):
    # FIXED: Explicitly asking for every hourly and daily variable to prevent KeyErrors
    w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,relativehumidity_2m,precipitation,visibility&daily=uv_index_max,sunrise,sunset&timezone=auto"
    a_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=european_aqi,pollen_birch,pollen_grass&hourly=pm10,pm2_5&timezone=auto"
    try:
        w_res = requests.get(w_url).json()
        a_res = requests.get(a_url).json()
        return w_res, a_res
    except: return None, None

def get_radar_chart(temp, hum, wind, uv, rain):
    categories = ['Temp', 'Humidity', 'Wind', 'UV', 'Rain']
    values = [min(temp*2, 100), hum, min(wind*2, 100), min(uv*10, 100), min(rain*10, 100)]
    fig = go.Figure(data=go.Scatterpolar(r=values, theta=categories, fill='toself', marker=dict(color='#0ea5e9')))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, height=320,
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
    return fig

# ---------------- SIDEBAR & NAVIGATION ----------------
apply_ui_design()
with st.sidebar:
    st.title("🌐 Weather Time")
    query = st.text_input("Search Location", value="Colombo")
    st.divider()
    st.subheader("📍 Quick Discover")
    for city in ["London", "Tokyo", "Nuwara Eliya", "Dubai"]:
        if st.button(city, key=f"btn_{city}"): query = city
    st.divider()
    unit = st.radio("System", ["Celsius", "Fahrenheit"], horizontal=True)

# Geocoding
res = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={query}&count=1").json()
loc = res["results"][0] if "results" in res else {"latitude": 6.9271, "longitude": 79.8612, "name": "Colombo", "country": "Sri Lanka"}

# ---------------- DASHBOARD RENDER ----------------
w_data, a_data = fetch_weather_intel(loc['latitude'], loc['longitude'])

if w_data and a_data:
    # DEFENSIVE CODING: Using .get() prevents KeyError crashes
    curr_w = w_data.get('current_weather', {})
    curr_a = a_data.get('current', {})
    hourly_w = w_data.get('hourly', {})
    hourly_a = a_data.get('hourly', {})

    # Calculate Intelligence
    comfort = get_comfort_score(curr_w.get('temperature', 25), hourly_w.get('relativehumidity_2m', [70])[0], hourly_w.get('precipitation', [0])[0], curr_a.get('european_aqi', 40))
    moon_name, moon_icon = get_moon_phase(datetime.now())

    # HTML HERO CARD
    st.markdown(f"""
    <div class="hero-card">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <h1 style="margin:0; font-size: 38px; color: white;">{loc['name']}, {loc.get('country', '')}</h1>
                <p style="color: #94a3b8; font-size: 16px;">{moon_icon} {moon_name} • {comfort}/100 Comfort Score</p>
            </div>
            <div style="text-align: right;">
                <h1 style="margin:0; font-size: 58px; color: #0ea5e9;">{curr_w.get('temperature')}°</h1>
                <p style="margin:0; color: #94a3b8;">AQI: {curr_a.get('european_aqi', 'N/A')}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ANALYTICS TABS
    tab_now, tab_charts, tab_air, tab_sys = st.tabs(["🚀 Intel Overview", "📈 Analytics", "🧪 Health & Air", "🛠 System"])

    with tab_now:
        # Alerts
        if w_data['daily']['uv_index_max'][0] > 8:
            st.markdown('<div class="alert-banner">☀️ SEVERE UV: Burn risk in 15 mins. Use SPF 50+.</div>', unsafe_allow_html=True)
            
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Visibility", f"{hourly_w.get('visibility', [10000])[0]/1000} km")
        c2.metric("UV Index", f"{w_data['daily']['uv_index_max'][0]}")
        c3.metric("Rainfall", f"{hourly_w.get('precipitation', [0])[0]}mm")
        c4.metric("Humidity", f"{hourly_w.get('relativehumidity_2m', [70])[0]}%")

        col_radar, col_map = st.columns([1, 1])
        with col_radar:
            st.subheader("5-Factor Radar Summary")
            st.plotly_chart(get_radar_chart(curr_w.get('temperature', 25), hourly_w.get('relativehumidity_2m', [70])[0], curr_w.get('windspeed', 10), w_data['daily']['uv_index_max'][0], hourly_w.get('precipitation', [0])[0]), use_container_width=True)
        with col_map:
            st.subheader("📍 World Location")
            st.map(pd.DataFrame({'lat': [loc['latitude']], 'lon': [loc['longitude']]}), zoom=8)

    with tab_charts:
        st.subheader("24-Hour Interactive Trend")
        df_trends = pd.DataFrame({"Time": pd.to_datetime(hourly_w.get('time', [])[:24]), "Temp": hourly_w.get('temperature_2m', [])[:24]})
        fig = px.area(df_trends, x="Time", y="Temp", color_discrete_sequence=['#0ea5e9'])
        st.plotly_chart(fig, use_container_width=True)
        st.info(f"🌅 Sunrise: {w_data['daily']['sunrise'][0].split('T')[1]} | 🌇 Sunset: {w_data['daily']['sunset'][0].split('T')[1]}")

    with tab_air:
        st.subheader("🌫 Pollutant Intel (PM2.5 & PM10)")
        df_aqi = pd.DataFrame({"Time": pd.to_datetime(hourly_a.get('time', [])[:48]), "PM2.5": hourly_a.get('pm2_5', [])[:48], "PM10": hourly_a.get('pm10', [])[:48]}).set_index("Time")
        st.line_chart(df_aqi)
        st.write(f"🍃 **Birch Pollen:** {curr_a.get('pollen_birch', 0)} | **Grass Pollen:** {curr_a.get('pollen_grass', 0)}")

    with tab_sys:
        st.subheader("📜 Version History")
        if os.path.exists("changelog.json"):
            with open("changelog.json", "r") as f:
                ch = json.load(f)
                for v in ch:
                    with st.expander(f"v{v['version']} - {v['date']}", expanded=(v['version']=="1.2.3.4.2.2")):
                        for n in v['notes']: st.write(f"- {n}")

else:
    st.error("Intelligence synchronization failed. Check local node status.")

st.caption(f"v1.2.3.4.2.2 | Context Intelligence Dashboard | {datetime.now().strftime('%H:%M:%S')}")