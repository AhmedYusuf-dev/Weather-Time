import streamlit as st
import requests
import os
from datetime import datetime

st.set_page_config(page_title="Weather Time Pro", layout="wide", page_icon="🌍")

# --- UI INJECTION ---
def apply_ui():
    css_path = os.path.join("assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

apply_ui()

# --- INITIALIZE MASTER STATE ---
if "city_name" not in st.session_state: st.session_state.city_name = "Colombo"
if "loc_data" not in st.session_state: st.session_state.loc_data = None
if "weather_data" not in st.session_state: st.session_state.weather_data = None

# --- SEARCH LOGIC ---
st.markdown('<h1 class="city-title">Weather Intelligence</h1>', unsafe_allow_html=True)
search_q = st.text_input("Search Location", value=st.session_state.city_name)

if st.button("Sync Data Node"):
    res = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={search_q}&count=1").json()
    if "results" in res:
        # Save Location
        loc = res["results"][0]
        st.session_state.loc_data = loc
        st.session_state.city_name = loc['name']
        
        # Fetch Weather (Added 'precipitation' to fix Garage KeyError)
        w_url = f"https://api.open-meteo.com/v1/forecast?latitude={loc['latitude']}&longitude={loc['longitude']}&current_weather=true&hourly=temperature_2m,relativehumidity_2m,precipitation&daily=uv_index_max,sunrise,sunset&timezone=auto"
        st.session_state.weather_data = requests.get(w_url).json()
        st.success(f"Intelligence Synced: {loc['name']}")
    else:
        st.error("City not found.")

# --- HERO DISPLAY ---
if st.session_state.weather_data:
    w = st.session_state.weather_data
    curr = w['current_weather']
    st.markdown(f"""
        <div class="glass-hero">
            <div style="display: flex; justify-content: space-between;">
                <div><h1>{st.session_state.city_name}</h1><p>Active Intelligence Node</p></div>
                <div style="text-align: right;"><h1 style="color:#38bdf8;">{curr['temperature']}°</h1></div>
            </div>
        </div>
    """, unsafe_allow_html=True)