import streamlit as st
import os
from datetime import datetime

# 1. PAGE SETUP & STYLE
st.set_page_config(page_title="Astro Intelligence", layout="wide")

def apply_style():
    css_path = os.path.join("assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

apply_style()

# --- THE GATEKEEPER (Prevents AttributeError) ---
if st.session_state.get("weather_data") is None:
    st.warning("📡 **Astro Node Offline**")
    st.info("Please return to the **Home** page and sync a city to unlock lunar and solar data.")
    if st.button("Back to Home"):
        st.switch_page("Home.py")
    st.stop()

# --- DATA ACCESS ---
data = st.session_state.weather_data
city = st.session_state.city_name

# --- MOON PHASE LOGIC ---
def get_moon_phase(d):
    diff = d - datetime(2001, 1, 1)
    days = diff.days + diff.seconds / 86400
    lunations = 0.20439731 + (days * 0.03386319269)
    phase = lunations % 1.0
    if phase < 0.06: return "New Moon", "🌑"
    if phase < 0.50: return "Waxing", "🌓"
    if phase < 0.56: return "Full Moon", "🌕"
    return "Waning", "🌗"

# --- UI RENDER ---
st.markdown(f'<h1 class="city-title">{city} Astro</h1>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("☀️ Solar Tracking")
    sunrise = data['daily']['sunrise'][0].split("T")[1]
    sunset = data['daily']['sunset'][0].split("T")[1]
    
    st.success(f"🌅 Sunrise: {sunrise}")
    st.error(f"🌇 Sunset: {sunset}")
    st.info("📸 **Photography Tip:** Golden Hour begins 45 minutes before sunset.")

with col2:
    st.subheader("🌑 Lunar Intelligence")
    name, icon = get_moon_phase(datetime.now())
    st.markdown(f"""
        <div style="background: rgba(255,255,255,0.05); padding: 40px; border-radius: 25px; text-align: center; border: 1px solid rgba(255,255,255,0.1);">
            <h1 style="font-size: 80px; margin: 0;">{icon}</h1>
            <h2 style="margin: 0;">{name}</h2>
            <p style="opacity: 0.6;">Node Phase Tracking Active</p>
        </div>
    """, unsafe_allow_html=True)