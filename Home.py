import streamlit as st
import requests
import os
import pandas as pd
import json  # <--- ADD THIS LINE
from datetime import datetime

# 1. PAGE CONFIG
st.set_page_config(page_title="WeatherTime Pro", layout="wide", page_icon="🌍")

# 2. APPLY EXTERNAL CSS
def apply_ui():
    css_path = os.path.join("assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

apply_ui()

# 3. MASTER STATE INIT
if "city_name" not in st.session_state: st.session_state.city_name = "Colombo"
if "weather_data" not in st.session_state: st.session_state.weather_data = None

# 4. DATA ENGINE
def get_weather_intel(city):
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        geo_res = requests.get(geo_url).json()
        if not geo_res.get("results"): return None
        
        loc = geo_res["results"][0]
        # Include precipitation for the Garage page sync
        w_url = f"https://api.open-meteo.com/v1/forecast?latitude={loc['latitude']}&longitude={loc['longitude']}&current_weather=true&hourly=temperature_2m,relativehumidity_2m,precipitation&daily=uv_index_max,sunrise,sunset&timezone=auto"
        return {"name": loc["name"], "data": requests.get(w_url).json()}
    except: return None

# 5. SIDEBAR
with st.sidebar:
    st.markdown("## 🛰️ Navigation")
    search_input = st.text_input("Find Location", value=st.session_state.city_name)
    if st.button("Sync Data Node"):
        st.session_state.city_name = search_input
        st.rerun()

# 6. MAIN HUB
payload = get_weather_intel(st.session_state.city_name)

if payload:
    st.session_state.weather_data = payload['data']
    w = payload['data']
    curr = w['current_weather']
    
    st.markdown(f'<h1 class="city-title">{payload["name"]}</h1>', unsafe_allow_html=True)
    
    # Hero Card
    st.markdown(f"""
        <div class="glass-hero">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h2 style="margin:0; opacity:0.7;">CURRENT STATUS</h2>
                    <p style="font-size: 1.2rem;">Node Synced & Operational</p>
                </div>
                <div style="text-align: right;">
                    <h1 style="font-size: 6rem; color: #38bdf8; margin:0;">{curr['temperature']}°</h1>
                    <p style="margin:0; opacity:0.8;">Wind: {curr['windspeed']} km/h</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 24h Visualizer
    st.subheader("📊 24-Hour Forecast")
    df = pd.DataFrame({
        "Time": pd.to_datetime(w['hourly']['time'][:24]),
        "Temp": w['hourly']['temperature_2m'][:24]
    }).set_index("Time")
    st.area_chart(df, color="#38bdf8")

else:
    st.error("Connection failed. Please check city name.")

# --- CHANGELOG NODE (Add this to the bottom of Home.py) ---
st.markdown("---")
st.subheader("🛠 System Version History")

changelog_path = "changelog.json"

if os.path.exists(changelog_path):
    try:
        with open(changelog_path, "r") as f:
            changelog_data = json.load(f)
            
            # Display each version in a clean expander
            for entry in changelog_data:
                with st.expander(f"🚀 Version {entry['version']} — {entry['date']}"):
                    for note in entry['notes']:
                        st.markdown(f"• {note}")
    except Exception as e:
        st.error(f"Failed to parse changelog: {e}")
else:
    # If the file is missing, we show this helpful alert
    st.info("Changelog file not found. Ensure 'changelog.json' is in your main Dash_Board folder.")
    # Create a dummy one for the user to see what it should look like
    if st.button("Generate Template changelog.json"):
        template = [
            {"version": "1.2.3.5", "date": "2026-01-24", "notes": ["Final Release Candidate", "Glassmorphism UI"]}
        ]
        with open("changelog.json", "w") as f:
            json.dump(template, f, indent=4)
        st.rerun()

st.caption(f"v1.2.3.5 | Data Node Only | {datetime.now().strftime('%H:%M:%S')}")