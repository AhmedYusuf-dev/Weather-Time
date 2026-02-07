import streamlit as st
import requests
import os
import pandas as pd
from datetime import datetime

# PAGE CONFIG
st.set_page_config(page_title="Health Advisor | WeatherTime Pro", layout="wide", page_icon="🏥")

# Apply CSS
def apply_ui():
    css_path = os.path.join("..", "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        css_path = os.path.join("assets", "style.css")
        if os.path.exists(css_path):
            with open(css_path, encoding="utf-8") as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

apply_ui()

# Initialize state
if "city_name" not in st.session_state:
    st.session_state.city_name = "Colombo"

# Weather fetch
def get_weather_data(city_name):
    city = city_name.split(",")[0]
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        geo_res = requests.get(geo_url).json()
        if not geo_res.get("results"): return None
        
        loc = geo_res["results"][0]
        w_url = (f"https://api.open-meteo.com/v1/forecast?latitude={loc['latitude']}&longitude={loc['longitude']}"
                 "&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,uv_index"
                 "&hourly=temperature_2m,uv_index,relative_humidity_2m"
                 "&daily=uv_index_max,temperature_2m_max,temperature_2m_min"
                 "&timezone=auto")
        
        weather_data = requests.get(w_url).json()
        return {
            "name": loc["name"],
            "country": loc.get("country", ""),
            "data": weather_data
        }
    except:
        return None

# HEADER
st.markdown('<h1 class="city-title">🏥 Health & Safety Advisor</h1>', unsafe_allow_html=True)
st.markdown("Monitor weather conditions that affect your health and wellbeing")

# SIDEBAR
with st.sidebar:
    st.markdown("### 📍 Location")
    city_input = st.text_input("Enter city name:", value=st.session_state.city_name)
    if st.button("Update Location"):
        st.session_state.city_name = city_input
        st.rerun()

# MAIN CONTENT
weather = get_weather_data(st.session_state.city_name)

if weather:
    curr = weather['data'].get('current', {})
    daily = weather['data'].get('daily', {})
    hourly = weather['data'].get('hourly', {})
    
    temp = curr.get('temperature_2m', 0)
    feels = curr.get('apparent_temperature', 0)
    humidity = curr.get('relative_humidity_2m', 0)
    uv_now = curr.get('uv_index', 0)
    uv_max = daily.get('uv_index_max', [0])[0]
    
    st.markdown(f"### 📍 {weather['name']}, {weather['country']}")
    
    # HEALTH ALERTS
    st.markdown("---")
    st.subheader("⚠️ Health Alerts")
    
    alerts = []
    
    # Temperature alerts
    if temp > 35:
        alerts.append(("🔥 EXTREME HEAT WARNING", 
                      f"Temperature is {temp}°C! Avoid outdoor activities, stay hydrated.",
                      "danger"))
    elif temp > 30:
        alerts.append(("☀️ Heat Advisory", 
                      f"Hot day at {temp}°C. Drink plenty of water and limit sun exposure.",
                      "warning"))
    elif temp < 0:
        alerts.append(("❄️ FREEZING CONDITIONS", 
                      f"Temperature is {temp}°C! Dress warmly and limit exposure.",
                      "danger"))
    elif temp < 5:
        alerts.append(("🧊 Cold Advisory", 
                      f"Cold day at {temp}°C. Dress in layers.",
                      "warning"))
    
    # UV alerts
    if uv_max > 8:
        alerts.append(("☀️ VERY HIGH UV INDEX", 
                      f"UV Index: {uv_max}. Wear SPF 50+ sunscreen, hat, and sunglasses. Avoid midday sun.",
                      "danger"))
    elif uv_max > 5:
        alerts.append(("🧴 High UV Alert", 
                      f"UV Index: {uv_max}. Use SPF 30+ sunscreen and protective clothing.",
                      "warning"))
    
    # Humidity alerts
    if humidity > 80:
        alerts.append(("💧 High Humidity", 
                      f"Humidity: {humidity}%. May feel uncomfortable. Stay cool and hydrated.",
                      "info"))
    elif humidity < 30:
        alerts.append(("🌵 Low Humidity", 
                      f"Humidity: {humidity}%. Use moisturizer and drink water.",
                      "info"))
    
    if not alerts:
        st.success("✅ No active health alerts. Weather conditions are favorable!")
    else:
        for title, message, alert_type in alerts:
            if alert_type == "danger":
                st.error(f"**{title}**\n\n{message}")
            elif alert_type == "warning":
                st.warning(f"**{title}**\n\n{message}")
            else:
                st.info(f"**{title}**\n\n{message}")
    
    # UV EXPOSURE GUIDE
    st.markdown("---")
    st.subheader("☀️ UV Exposure Guide")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # UV Index gauge
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.05); padding:25px; border-radius:15px; text-align:center">
            <h3>Current UV Index</h3>
            <div style="font-size:4rem; font-weight:bold; color:#f59e0b">{uv_now}</div>
            <div style="font-size:1.2rem; margin-top:10px">
                {"Low" if uv_now < 3 else "Moderate" if uv_now < 6 else "High" if uv_now < 8 else "Very High" if uv_now < 11 else "Extreme"}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Safe exposure time
        if uv_now > 0:
            # Rough calculation for skin type II (fair skin)
            safe_minutes = max(5, int(200 / uv_now))
        else:
            safe_minutes = 60
        
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.05); padding:25px; border-radius:15px; text-align:center">
            <h3>Safe Exposure Time</h3>
            <div style="font-size:3rem; font-weight:bold; color:#38bdf8">{safe_minutes}</div>
            <div style="font-size:1.2rem; margin-top:10px">minutes without protection</div>
            <div style="font-size:0.85rem; color:#94a3b8; margin-top:10px">(for fair skin)</div>
        </div>
        """, unsafe_allow_html=True)
    
    # HYDRATION CALCULATOR
    st.markdown("---")
    st.subheader("💧 Hydration Recommendation")
    
    # Base hydration: 2L per day, increases with temperature
    base_water = 2.0  # liters
    if temp > 25:
        extra_water = (temp - 25) * 0.1
        total_water = base_water + extra_water
    else:
        total_water = base_water
    
    glasses = int(total_water * 4)  # 250ml glasses
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("💧 Recommended Daily Intake", f"{total_water:.1f} L")
    with col2:
        st.metric("🥤 Number of Glasses", f"{glasses} × 250ml")
    with col3:
        reminder_hours = 2 if temp > 30 else 3
        st.metric("⏰ Drink Every", f"{reminder_hours} hours")
    
    # COMFORT INDEX
    st.markdown("---")
    st.subheader("🌡️ Comfort & Activity Index")
    
    # Calculate comfort score (0-100)
    comfort_score = 50
    
    # Temperature comfort (optimal 18-24°C)
    if 18 <= temp <= 24:
        comfort_score += 30
    elif 15 <= temp <= 27:
        comfort_score += 15
    else:
        comfort_score -= abs(21 - temp) * 2
    
    # Humidity comfort (optimal 40-60%)
    if 40 <= humidity <= 60:
        comfort_score += 20
    else:
        comfort_score -= abs(50 - humidity) * 0.3
    
    comfort_score = max(0, min(100, comfort_score))
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.05); padding:20px; border-radius:15px">
            <h4>Overall Comfort Score</h4>
            <div style="background:#1e293b; border-radius:10px; height:30px; margin:10px 0; overflow:hidden">
                <div style="background:linear-gradient(90deg, #ef4444, #f59e0b, #10b981); 
                            width:{comfort_score}%; height:100%; transition:width 0.5s"></div>
            </div>
            <div style="text-align:center; font-size:2rem; font-weight:bold; margin:10px 0">
                {comfort_score:.0f}/100
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        activity_level = "Perfect" if comfort_score > 80 else "Good" if comfort_score > 60 else "Moderate" if comfort_score > 40 else "Low"
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.05); padding:20px; border-radius:15px; text-align:center">
            <h4>Activity Level</h4>
            <div style="font-size:2.5rem; margin:15px 0">
                {"🏃‍♂️" if comfort_score > 70 else "🚶‍♂️" if comfort_score > 50 else "🏠"}
            </div>
            <div style="font-size:1.5rem; font-weight:bold">
                {activity_level}
            </div>
        </div>
        """, unsafe_allow_html=True)

else:
    st.error(f"Unable to fetch weather data for {st.session_state.city_name}")
