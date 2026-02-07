import streamlit as st
import requests
import os
from datetime import datetime, timedelta

# PAGE CONFIG
st.set_page_config(page_title="Agriculture Guide | WeatherTime Pro", layout="wide", page_icon="🌾")

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

# Initialize
if "city_name" not in st.session_state:
    st.session_state.city_name = "Colombo"

def get_weather_data(city_name):
    city = city_name.split(",")[0]
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        geo_res = requests.get(geo_url).json()
        if not geo_res.get("results"): return None
        
        loc = geo_res["results"][0]
        w_url = (f"https://api.open-meteo.com/v1/forecast?latitude={loc['latitude']}&longitude={loc['longitude']}"
                 "&current=temperature_2m,relative_humidity_2m,precipitation,soil_temperature_0cm,soil_moisture_0_to_1cm"
                 "&hourly=temperature_2m,precipitation,soil_temperature_0cm,soil_moisture_0_to_1cm"
                 "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_hours"
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
st.markdown('<h1 class="city-title">🌾 Agriculture & Gardening Guide</h1>', unsafe_allow_html=True)
st.markdown("Weather insights for farmers and gardeners")

# SIDEBAR
with st.sidebar:
    st.markdown("### 📍 Location")
    city_input = st.text_input("Enter location:", value=st.session_state.city_name)
    if st.button("Update Location"):
        st.session_state.city_name = city_input
        st.rerun()

# MAIN
weather = get_weather_data(st.session_state.city_name)

if weather:
    curr = weather['data'].get('current', {})
    daily = weather['data'].get('daily', {})
    
    temp = curr.get('temperature_2m', 0)
    humidity = curr.get('relative_humidity_2m', 0)
    soil_temp = curr.get('soil_temperature_0cm', temp)
    soil_moisture = curr.get('soil_moisture_0_to_1cm', 0)
    rain_today = curr.get('precipitation', 0)
    
    st.markdown(f"### 📍 {weather['name']}, {weather['country']}")
    
    # CURRENT CONDITIONS
    st.markdown("---")
    st.subheader("🌡️ Current Field Conditions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🌡️ Air Temperature", f"{temp}°C")
    with col2:
        st.metric("🌱 Soil Temperature", f"{soil_temp}°C")
    with col3:
        st.metric("💧 Soil Moisture", f"{soil_moisture}%")
    with col4:
        st.metric("💦 Humidity", f"{humidity}%")
    
    # FROST WARNING
    st.markdown("---")
    st.subheader("❄️ Frost & Temperature Alerts")
    
    min_temps = daily.get('temperature_2m_min', [])[:7]
    frost_days = [i for i, t in enumerate(min_temps) if t < 2]
    
    if frost_days:
        st.warning(f"""
        **🧊 FROST WARNING**
        
        Frost risk detected in the next {len(frost_days)} day(s)!
        - Protect sensitive crops with covers
        - Harvest vulnerable vegetables
        - Move potted plants indoors
        - Water in the morning (not evening)
        """)
    else:
        st.success("✅ No frost risk in the next 7 days")
    
    # RAINFALL TRACKING
    st.markdown("---")
    st.subheader("🌧️ Irrigation Planning")
    
    rain_forecast = daily.get('precipitation_sum', [])[:7]
    total_rain = sum(rain_forecast)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.05); padding:20px; border-radius:15px">
            <h4>7-Day Rainfall Forecast</h4>
            <div style="font-size:2.5rem; font-weight:bold; color:#38bdf8; margin:15px 0">
                {total_rain:.1f} mm
            </div>
            <div>Total expected rainfall this week</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Daily rain breakdown
        st.markdown("**Daily Breakdown:**")
        for i, rain in enumerate(rain_forecast):
            date = datetime.now() + timedelta(days=i)
            day_name = date.strftime("%A")
            bar_width = min(100, rain * 5)  # Scale for visualization
            st.markdown(f"""
            <div style="margin:5px 0">
                <span style="display:inline-block; width:80px">{day_name[:3]}</span>
                <div style="display:inline-block; width:200px; background:#1e293b; border-radius:5px; height:20px; vertical-align:middle">
                    <div style="background:#38bdf8; width:{bar_width}%; height:100%; border-radius:5px"></div>
                </div>
                <span style="margin-left:10px">{rain:.1f} mm</span>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # Irrigation advice
        if total_rain > 20:
            advice = "🌧️ Heavy rain expected"
            detail = "Reduce or skip irrigation. Ensure good drainage."
            color = "#3b82f6"
        elif total_rain > 10:
            advice = "💧 Moderate rain"
            detail = "Reduce irrigation frequency. Monitor soil moisture."
            color = "#10b981"
        else:
            advice = "☀️ Low rainfall"
            detail = "Regular irrigation needed. Water deeply and less frequently."
            color = "#f59e0b"
        
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.05); padding:20px; border-radius:15px; border-left:4px solid {color}">
            <h4>{advice}</h4>
            <p style="color:#94a3b8">{detail}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # PLANTING CALENDAR
    st.markdown("---")
    st.subheader("📅 Best Days for Farming Activities")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background:rgba(255,255,255,0.05); padding:20px; border-radius:15px; text-align:center">
            <h4>🌱 Best for Planting</h4>
        """, unsafe_allow_html=True)
        
        # Find days with low rain and good temp
        planting_days = []
        for i in range(7):
            if rain_forecast[i] < 5 and 15 < min_temps[i] < 30:
                date = datetime.now() + timedelta(days=i)
                planting_days.append(date.strftime("%a, %b %d"))
        
        if planting_days:
            for day in planting_days[:3]:
                st.markdown(f"✅ {day}")
        else:
            st.markdown("⚠️ Check back later")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background:rgba(255,255,255,0.05); padding:20px; border-radius:15px; text-align:center">
            <h4>🌾 Best for Harvesting</h4>
        """, unsafe_allow_html=True)
        
        # Find dry days
        harvest_days = []
        for i in range(7):
            if rain_forecast[i] < 2:
                date = datetime.now() + timedelta(days=i)
                harvest_days.append(date.strftime("%a, %b %d"))
        
        if harvest_days:
            for day in harvest_days[:3]:
                st.markdown(f"✅ {day}")
        else:
            st.markdown("⚠️ Wet conditions")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background:rgba(255,255,255,0.05); padding:20px; border-radius:15px; text-align:center">
            <h4>🚜 Best for Field Work</h4>
        """, unsafe_allow_html=True)
        
        # Dry days with good conditions
        fieldwork_days = []
        for i in range(7):
            if rain_forecast[i] == 0 and soil_moisture < 80:
                date = datetime.now() + timedelta(days=i)
                fieldwork_days.append(date.strftime("%a, %b %d"))
        
        if fieldwork_days:
            for day in fieldwork_days[:3]:
                st.markdown(f"✅ {day}")
        else:
            st.markdown("⚠️ Wait for drier soil")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # PEST RISK
    st.markdown("---")
    st.subheader("🐛 Pest & Disease Risk Assessment")
    
    # Simple pest risk model based on temp and humidity
    if temp > 20 and humidity > 70:
        risk_level = "High"
        risk_color = "#ef4444"
        risk_icon = "🔴"
        risk_advice = "Favorable conditions for pests. Monitor crops closely and consider preventive measures."
    elif temp > 15 and humidity > 60:
        risk_level = "Moderate"
        risk_color = "#f59e0b"
        risk_icon = "🟡"
        risk_advice = "Some pest activity expected. Regular monitoring recommended."
    else:
        risk_level = "Low"
        risk_color = "#10b981"
        risk_icon = "🟢"
        risk_advice = "Conditions not favorable for most pests. Maintain regular crop checks."
    
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.05); padding:25px; border-radius:15px; border-left:5px solid {risk_color}">
        <h3>{risk_icon} Pest Risk: {risk_level}</h3>
        <p style="font-size:1.1rem; color:#94a3b8">{risk_advice}</p>
        <div style="margin-top:15px; font-size:0.9rem">
            <div>🌡️ Temperature: {temp}°C</div>
            <div>💧 Humidity: {humidity}%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

else:
    st.error(f"Unable to fetch weather data for {st.session_state.city_name}")
