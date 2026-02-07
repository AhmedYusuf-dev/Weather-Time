import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
import os
from datetime import datetime, timedelta

# PAGE CONFIG
st.set_page_config(page_title="Analytics | WeatherTime Pro", layout="wide", page_icon="📊")

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

# Session State for City
if "city_name" not in st.session_state: st.session_state.city_name = "Colombo"

# HELPER: Get Coordinates
def get_coordinates(city_name):
    try:
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1"
        res = requests.get(url).json()
        if res.get("results"):
            return res["results"][0]
    except:
        return None
    return None

# HELPER: Get Historical Data
def get_historical_data(lat, lon, days=30):
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    url = (f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}"
           f"&start_date={start_date}&end_date={end_date}"
           "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,max_wind_speed_10m"
           "&timezone=auto")
    
    try:
        res = requests.get(url).json()
        return res.get("daily", {})
    except:
        return None

# HEADER
st.markdown(f'<h1 class="city-title">📊 Historical Analytics</h1>', unsafe_allow_html=True)
st.markdown(f"Weather trends for **{st.session_state.city_name}** over the last 30 days")

# MAIN LOGIC
loc = get_coordinates(st.session_state.city_name)

if loc:
    with st.spinner("Fetching historical archive..."):
        data = get_historical_data(loc['latitude'], loc['longitude'])
    
    if data:
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # KEY METRICS
        st.markdown("---")
        st.subheader("📉 Monthly Overview")
        
        avg_max = df['temperature_2m_max'].mean()
        avg_min = df['temperature_2m_min'].mean()
        total_rain = df['precipitation_sum'].sum()
        max_wind = df['max_wind_speed_10m'].max()
        
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("Avg High Temp", f"{avg_max:.1f}°C")
        with c2: st.metric("Avg Low Temp", f"{avg_min:.1f}°C")
        with c3: st.metric("Total Rainfall", f"{total_rain:.1f} mm")
        with c4: st.metric("Max Wind Gust", f"{max_wind:.1f} km/h")
        
        # CHARTS
        st.markdown("---")
        
        # Temperature Trend
        st.subheader("🌡️ Temperature History")
        fig_temp = go.Figure()
        fig_temp.add_trace(go.Scatter(x=df['time'], y=df['temperature_2m_max'], name='Max Temp', line=dict(color='#f472b6')))
        fig_temp.add_trace(go.Scatter(x=df['time'], y=df['temperature_2m_min'], name='Min Temp', line=dict(color='#38bdf8')))
        fig_temp.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="white",
            height=350,
            xaxis_title="Date",
            yaxis_title="Temperature (°C)"
        )
        st.plotly_chart(fig_temp, width="stretch")
        
        # Rainfall Analysis
        st.subheader("🌧️ Rainfall Distribution")
        fig_rain = px.bar(df, x='time', y='precipitation_sum', 
                          color='precipitation_sum',
                          color_continuous_scale='Teal')
        fig_rain.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="white",
            height=350,
            xaxis_title="Date",
            yaxis_title="Rainfall (mm)"
        )
        st.plotly_chart(fig_rain, width="stretch")
        
        # Wind Analysis
        st.subheader("💨 Wind Speed Trends")
        fig_wind = px.area(df, x='time', y='max_wind_speed_10m',
                           line_shape='spline')
        fig_wind.update_traces(line_color='#a78bfa', fill_color='rgba(167, 139, 250, 0.3)')
        fig_wind.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="white",
            height=350,
            xaxis_title="Date",
            yaxis_title="Wind Speed (km/h)"
        )
        st.plotly_chart(fig_wind, width="stretch")

    else:
        st.error("Failed to load historical data.")
else:
    st.error("Location not found.")
