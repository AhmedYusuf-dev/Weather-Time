import streamlit as st
import requests
import os
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

# PAGE CONFIG
st.set_page_config(page_title="Travel Planner | WeatherTime Pro", layout="wide", page_icon="🌍")

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

# POPULAR CITIES
POPULAR_CITIES = [
    "Amsterdam, Netherlands", "Athens, Greece", "Austin, USA", "Abu Dhabi, UAE",
    "Bangkok, Thailand", "Beijing, China", "Berlin, Germany", "Boston, USA",
    "Cairo, Egypt", "Cape Town, South Africa", "Chicago, USA", "Colombo, Sri Lanka",
    "Delhi, India", "Dubai, UAE", "Dublin, Ireland",
    "London, UK", "Los Angeles, USA", "Madrid, Spain", "Mumbai, India",
    "New York, USA", "Paris, France", "Rome, Italy", "Singapore",
    "Sydney, Australia", "Tokyo, Japan", "Toronto, Canada"
]

# Weather fetch function
def get_weather_data(city_name):
    city = city_name.split(",")[0]
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        geo_res = requests.get(geo_url).json()
        if not geo_res.get("results"): return None
        
        loc = geo_res["results"][0]
        w_url = (f"https://api.open-meteo.com/v1/forecast?latitude={loc['latitude']}&longitude={loc['longitude']}"
                 "&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m,precipitation"
                 "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,uv_index_max,weather_code"
                 "&timezone=auto")
        
        weather_data = requests.get(w_url).json()
        return {
            "name": loc["name"],
            "country": loc.get("country", ""),
            "data": weather_data
        }
    except:
        return None

# WMO Code mapping
def get_weather_icon(code):
    mapping = {
        0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️",
        45: "🌫️", 48: "🌫️", 51: "🌦️", 53: "🌧️",
        61: "🌦️", 63: "🌧️", 65: "⛈️", 71: "❄️",
        80: "🌦️", 95: "⛈️"
    }
    return mapping.get(code, "🌡️")

# HEADER
st.markdown('<h1 class="city-title">🌍 Travel Planner</h1>', unsafe_allow_html=True)
st.markdown("Compare weather across multiple destinations to plan your perfect trip!")

# CITY SELECTION
st.markdown("---")
st.subheader("🎯 Select Your Destinations")

col1, col2, col3, col4 = st.columns(4)

with col1:
    city1 = st.selectbox("Destination 1", POPULAR_CITIES, index=POPULAR_CITIES.index("London, UK"))
with col2:
    city2 = st.selectbox("Destination 2", POPULAR_CITIES, index=POPULAR_CITIES.index("Paris, France"))
with col3:
    city3 = st.selectbox("Destination 3", POPULAR_CITIES, index=POPULAR_CITIES.index("Rome, Italy"))
with col4:
    city4 = st.selectbox("Destination 4", POPULAR_CITIES, index=POPULAR_CITIES.index("Tokyo, Japan"))

cities = [city1, city2, city3, city4]

if st.button("🔍 Compare Weather", width="stretch"):
    st.session_state['compare_cities'] = cities

# COMPARISON
if 'compare_cities' in st.session_state:
    st.markdown("---")
    st.subheader("📊 Weather Comparison")
    
    comparison_data = []
    cols = st.columns(4)
    
    for idx, city in enumerate(st.session_state['compare_cities']):
        weather = get_weather_data(city)
        if weather:
            comparison_data.append(weather)
            
            with cols[idx]:
                curr = weather['data'].get('current', {})
                daily = weather['data'].get('daily', {})
                
                temp = curr.get('temperature_2m', 0)
                feels = curr.get('apparent_temperature', 0)
                w_code = curr.get('weather_code', 0)
                rain = daily.get('precipitation_sum', [0])[0]
                uv = daily.get('uv_index_max', [0])[0]
                
                icon = get_weather_icon(w_code)
                
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.05); padding:20px; border-radius:15px; text-align:center; height:350px">
                    <h3 style="color:#38bdf8; margin-bottom:10px">{weather['name']}</h3>
                    <div style="font-size:0.9rem; color:#94a3b8; margin-bottom:15px">{weather['country']}</div>
                    <div style="font-size:4rem; margin:15px 0">{icon}</div>
                    <div style="font-size:2.5rem; font-weight:bold; margin:10px 0">{temp}°C</div>
                    <div style="color:#94a3b8; margin-bottom:15px">Feels like {feels}°C</div>
                    <div style="display:grid; gap:8px; text-align:left; font-size:0.85rem">
                        <div>💧 Rain: {rain} mm</div>
                        <div>☀️ UV: {uv}</div>
                        <div>💨 Wind: {curr.get('wind_speed_10m', 0)} km/h</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # 7-DAY COMPARISON CHART
    if comparison_data:
        st.markdown("---")
        st.subheader("📈 7-Day Temperature Forecast")
        
        fig = go.Figure()
        
        for weather in comparison_data:
            daily = weather['data'].get('daily', {})
            times = daily.get('time', [])[:7]
            temps_max = daily.get('temperature_2m_max', [])[:7]
            
            fig.add_trace(go.Scatter(
                x=times,
                y=temps_max,
                mode='lines+markers',
                name=weather['name'],
                line=dict(width=3),
                marker=dict(size=8)
            ))
        
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="white",
            height=400,
            xaxis_title="Date",
            yaxis_title="Temperature (°C)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, width="stretch")
        
        # RECOMMENDATIONS
        st.markdown("---")
        st.subheader("💡 Travel Recommendations")
        
        # Find best city based on temperature and rain
        best_city = None
        best_score = -999
        
        for weather in comparison_data:
            curr = weather['data'].get('current', {})
            daily = weather['data'].get('daily', {})
            
            temp = curr.get('temperature_2m', 0)
            rain = daily.get('precipitation_sum', [0])[0]
            uv = daily.get('uv_index_max', [0])[0]
            
            # Simple scoring: prefer 18-25°C, low rain, moderate UV
            score = 0
            if 18 <= temp <= 25: score += 50
            elif 15 <= temp <= 28: score += 30
            score -= rain * 5  # Penalize rain
            if 3 <= uv <= 6: score += 20  # Moderate UV is good
            
            if score > best_score:
                best_score = score
                best_city = weather
        
        if best_city:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"""
                <div style="background:linear-gradient(135deg, #38bdf8 0%, #818cf8 100%); 
                            padding:25px; border-radius:15px; color:white">
                    <h3>🏆 Best Destination This Week</h3>
                    <h2>{best_city['name']}, {best_city['country']}</h2>
                    <p style="font-size:1.1rem; opacity:0.9">
                        Perfect weather conditions with comfortable temperatures and minimal rainfall!
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div style="background:rgba(255,255,255,0.05); padding:20px; border-radius:15px">
                    <h4>📋 Packing Checklist</h4>
                    <div style="font-size:0.9rem; line-height:1.8">
                        ☀️ Sunglasses<br>
                        🧴 Sunscreen<br>
                        👕 Light clothing<br>
                        🧥 Light jacket<br>
                        📸 Camera
                    </div>
                </div>
                """, unsafe_allow_html=True)
