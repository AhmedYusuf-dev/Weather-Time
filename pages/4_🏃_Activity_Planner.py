import streamlit as st
import requests
import os
from datetime import datetime

# PAGE CONFIG
st.set_page_config(page_title="Activity Planner | WeatherTime Pro", layout="wide", page_icon="🏃")

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
                 "&current=temperature_2m,precipitation,wind_speed_10m,cloud_cover"
                 "&hourly=temperature_2m,precipitation_probability,wind_speed_10m,cloud_cover,visibility"
                 "&daily=sunrise,sunset,temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max"
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
st.markdown('<h1 class="city-title">🏃 Outdoor Activity Planner</h1>', unsafe_allow_html=True)
st.markdown("Find the perfect time for your outdoor activities")

# SIDEBAR
with st.sidebar:
    st.markdown("### 📍 Location")
    city_input = st.text_input("Enter location:", value=st.session_state.city_name)
    if st.button("Update Location"):
        st.session_state.city_name = city_input
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 🎯 Select Activity")
    activity = st.selectbox("Choose your activity:", [
        "🏃 Running",
        "🚴 Cycling",
        "🥾 Hiking",
        "🏖️ Beach Day",
        "📸 Photography",
        "⛵ Sailing",
        "⛳ Golf",
        "🎣 Fishing"
    ])

weather = get_weather_data(st.session_state.city_name)

if weather:
    curr = weather['data'].get('current', {})
    daily = weather['data'].get('daily', {})
    hourly = weather['data'].get('hourly', {})
    
    temp = curr.get('temperature_2m', 0)
    wind = curr.get('wind_speed_10m', 0)
    clouds = curr.get('cloud_cover', 0)
    rain = curr.get('precipitation', 0)
    
    st.markdown(f"### 📍 {weather['name']}, {weather['country']}")
    
    # ACTIVITY RATING
    st.markdown("---")
    st.subheader(f"⭐ Conditions for {activity}")
    
    # Calculate activity score based on conditions
    score = 50  # Base score
    
    activity_name = activity.split()[1]  # Get activity name without emoji
    
    # Activity-specific scoring
    if activity_name in ["Running", "Cycling", "Hiking"]:
        # Prefer 15-25°C, low rain, moderate wind
        if 15 <= temp <= 25: score += 30
        elif 10 <= temp <= 30: score += 15
        score -= rain * 20
        score -= max(0, wind - 15) * 2
        
    elif activity_name == "Beach":
        # Prefer hot, sunny
        if temp > 25: score += 30
        if clouds < 30: score += 20
        score -= rain * 30
        
    elif activity_name == "Photography":
        # Golden hour, interesting clouds
        if 20 < clouds < 70: score += 20  # Interesting sky
        score -= rain * 25
        
    elif activity_name == "Sailing":
        # Need wind but not too much
        if 10 <= wind <= 25: score += 40
        elif wind < 10: score -= 20
        score -= rain * 20
    
    elif activity_name in ["Golf", "Fishing"]:
        # Dry conditions preferred
        if 15 <= temp <= 28: score += 25
        score -= rain * 25
        if wind < 20: score += 15
    
    score = max(0, min(100, score))
    
    # Display score
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Score bar
        if score >= 80:
            rating = "Excellent"
            color = "#10b981"
            emoji = "🌟"
        elif score >= 60:
            rating = "Good"
            color = "#38bdf8"
            emoji = "👍"
        elif score >= 40:
            rating = "Fair"
            color = "#f59e0b"
            emoji = "⚠️"
        else:
            rating = "Poor"
            color = "#ef4444"
            emoji = "❌"
        
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.05); padding:25px; border-radius:15px">
            <h3>{emoji} {rating} Conditions</h3>
            <div style="background:#1e293b; border-radius:10px; height:40px; margin:15px 0; overflow:hidden">
                <div style="background:{color};
                            width:{score}%; height:100%; transition:width 0.5s;
                            display:flex; align-items:center; justify-content:center;
                            font-weight:bold; font-size:1.2rem">
                    {score:.0f}%
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.05); padding:25px; border-radius:15px; text-align:center">
            <h4>Current Conditions</h4>
            <div style="margin:10px 0">🌡️ {temp}°C</div>
            <div style="margin:10px 0">💨 {wind} km/h</div>
            <div style="margin:10px 0">☁️ {clouds}%</div>
            <div style="margin:10px 0">💧 {rain} mm</div>
        </div>
        """, unsafe_allow_html=True)
    
    # BEST TIME TODAY
    st.markdown("---")
    st.subheader("⏰ Best Hours Today")
    
    # Analyze next 12 hours
    temps = hourly.get('temperature_2m', [])[:12]
    rain_prob = hourly.get('precipitation_probability', [0]*12)[:12]
    winds = hourly.get('wind_speed_10m', [])[:12]
    times = hourly.get('time', [])[:12]
    
    best_hours = []
    for i in range(len(temps)):
        hour_score = 50
        
        if activity_name in ["Running", "Cycling", "Hiking"]:
            if 15 <= temps[i] <= 25: hour_score += 30
            hour_score -= rain_prob[i] * 0.5
            hour_score -= max(0, winds[i] - 15) * 2
        elif activity_name == "Beach":
            if temps[i] > 25: hour_score += 30
            hour_score -= rain_prob[i] * 0.8
        elif activity_name == "Sailing":
            if 10 <= winds[i] <= 25: hour_score += 40
            hour_score -= rain_prob[i] * 0.3
        
        hour_score = max(0, min(100, hour_score))
        best_hours.append((times[i], temps[i], rain_prob[i], hour_score))
    
    # Sort by score
    best_hours.sort(key=lambda x: x[3], reverse=True)
    
    # Display top 3 hours
    cols = st.columns(3)
    for idx, (time, temp, rain_p, h_score) in enumerate(best_hours[:3]):
        with cols[idx]:
            hour = datetime.fromisoformat(time).strftime("%I %p")
            medal = ["🥇", "🥈", "🥉"][idx]
            
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.05); padding:20px; border-radius:15px; text-align:center">
                <div style="font-size:2rem">{medal}</div>
                <h3>{hour}</h3>
                <div style="margin:10px 0; font-size:1.5rem; font-weight:bold">{h_score:.0f}%</div>
                <div style="color:#94a3b8; font-size:0.9rem">
                    <div>{temp}°C</div>
                    <div>{rain_p}% rain chance</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # GOLDEN HOUR (for photography)
    if activity_name == "Photography":
        st.markdown("---")
        st.subheader("📸 Golden Hour Times")
        
        sunrise = daily.get('sunrise', [''])[0]
        sunset = daily.get('sunset', [''])[0]
        
        if sunrise and sunset:
            sunrise_time = datetime.fromisoformat(sunrise).strftime("%I:%M %p")
            sunset_time = datetime.fromisoformat(sunset).strftime("%I:%M %p")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div style="background:linear-gradient(135deg, #fbbf24, #f59e0b); padding:25px; border-radius:15px; text-align:center; color:white">
                    <h3>🌅 Sunrise Golden Hour</h3>
                    <div style="font-size:2.5rem; font-weight:bold; margin:15px 0">{sunrise_time}</div>
                    <div>Best light: 30 mins before sunrise</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style="background:linear-gradient(135deg, #f97316, #dc2626); padding:25px; border-radius:15px; text-align:center; color:white">
                    <h3>🌇 Sunset Golden Hour</h3>
                    <div style="font-size:2.5rem; font-weight:bold; margin:15px 0">{sunset_time}</div>
                    <div>Best light: 1 hour before sunset</div>
                </div>
                """, unsafe_allow_html=True)
    
    # 7-DAY OUTLOOK
    st.markdown("---")
    st.subheader("📅 7-Day Activity Outlook")
    
    max_temps = daily.get('temperature_2m_max', [])[:7]
    rain_sums = daily.get('precipitation_sum', [])[:7]
    daily_times = daily.get('time', [])[:7]
    
    for i in range(7):
        date = datetime.fromisoformat(daily_times[i])
        day_name = date.strftime("%A, %b %d")
        
        # Calculate daily score
        day_score = 50
        if activity_name in ["Running", "Cycling", "Hiking"]:
            if 15 <= max_temps[i] <= 28: day_score += 30
            day_score -= rain_sums[i] * 5
        elif activity_name == "Beach":
            if max_temps[i] > 25: day_score += 30
            day_score -= rain_sums[i] * 8
        
        day_score = max(0, min(100, day_score))
        
        if day_score >= 70:
            day_emoji = "😊"
            day_color = "#10b981"
        elif day_score >= 40:
            day_emoji = "😐"
            day_color = "#f59e0b"
        else:
            day_emoji = "😞"
            day_color = "#ef4444"
        
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.05); padding:15px; border-radius:10px; margin:10px 0; border-left:4px solid {day_color}">
            <div style="display:flex; justify-content:space-between; align-items:center">
                <div>
                    <span style="font-size:1.5rem">{day_emoji}</span>
                    <span style="font-weight:bold; margin-left:10px">{day_name}</span>
                </div>
                <div style="text-align:right">
                    <span style="font-size:1.2rem; font-weight:bold; color:{day_color}">{day_score:.0f}%</span>
                    <span style="color:#94a3b8; margin-left:15px">{max_temps[i]}°C | {rain_sums[i]:.1f}mm</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

else:
    st.error(f"Unable to fetch weather data for {st.session_state.city_name}")
