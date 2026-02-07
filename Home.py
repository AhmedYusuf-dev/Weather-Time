import streamlit as st
import requests
import os
import pandas as pd
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# 1. PAGE CONFIG & UI
st.set_page_config(page_title="WeatherTime Pro", layout="wide", page_icon="🌍")

def apply_ui():
    # Inject Custom CSS
    css_path = os.path.join("assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning("Style asset missing!")

apply_ui()

# 2. MASTER STATE INIT
if "city_name" not in st.session_state: st.session_state.city_name = "Colombo"
if "weather_data" not in st.session_state: st.session_state.weather_data = None

# --- LOCAL INTELLIGENCE DATABASE (For Autocomplete) ---
POPULAR_CITIES = [
    "Amsterdam, Netherlands", "Athens, Greece", "Austin, USA", "Abu Dhabi, UAE",
    "Bangkok, Thailand", "Beijing, China", "Berlin, Germany", "Boston, USA",
    "Cairo, Egypt", "Cape Town, South Africa", "Chicago, USA", "Colombo, Sri Lanka",
    "Delhi, India", "Dubai, UAE", "Dublin, Ireland",
    "Frankfurt, Germany", 
    "Galle, Sri Lanka", "Geneva, Switzerland",
    "Hong Kong", "Houston, USA",
    "Istanbul, Turkey",
    "Jakarta, Indonesia", 
    "Kandy, Sri Lanka", "Kyoto, Japan",
    "London, UK", "Los Angeles, USA", "Lisbon, Portugal",
    "Madrid, Spain", "Maranello, Italy", "Melbourne, Australia", "Mumbai, India", "Moscow, Russia",
    "New York, USA", "Nairobi, Kenya",
    "Osaka, Japan", "Oslo, Norway",
    "Paris, France", "Porscheplatz (Stuttgart), Germany",
    "Rome, Italy", "Rio de Janeiro, Brazil",
    "San Francisco, USA", "Seoul, South Korea", "Shanghai, China", "Singapore", "Stuttgart, Germany", "Sydney, Australia",
    "Tokyo, Japan", "Toronto, Canada",
    "Vancouver, Canada",
    "Zurich, Switzerland"
]

# 3. ADVANCED DATA ENGINE
def get_weather_intel(search_term):
    city = search_term.split(",")[0]
    
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        geo_res = requests.get(geo_url).json()
        if not geo_res.get("results"): return None
        
        loc = geo_res["results"][0]
        
        # EXPANDED API CALL: Added daily forecast, sunrise/sunset, UV index
        w_url = (f"https://api.open-meteo.com/v1/forecast?latitude={loc['latitude']}&longitude={loc['longitude']}"
                 "&current=temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,rain,weather_code,wind_speed_10m"
                 "&hourly=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,visibility"
                 "&daily=temperature_2m_max,temperature_2m_min,sunrise,sunset,uv_index_max,precipitation_sum,weather_code"
                 "&timezone=auto")
        
        return {
            "name": loc["name"], 
            "lat": loc["latitude"], 
            "lon": loc["longitude"], 
            "country": loc.get("country", ""),
            "data": requests.get(w_url).json()
        }
    except Exception as e:
        print(e)
        return None

# MAPPING WMO CODES TO ICONS/LABELS
def get_condition_intel(code, is_day=1):
    # Simplified WMO code map
    mapping = {
        0: ("Clear Sky", "☀️" if is_day else "🌙", "clear"),
        1: ("Mainly Clear", "🌤️" if is_day else "🌙", "cloudy"),
        2: ("Partly Cloudy", "⛅", "cloudy"),
        3: ("Overcast", "☁️", "cloudy"),
        45: ("Foggy", "🌫️", "mist"),
        48: ("Rime Fog", "🌫️", "mist"),
        51: ("Light Drizzle", "🌦️", "rain"),
        53: ("Drizzle", "🌧️", "rain"),
        61: ("Slight Rain", "🌦️", "rain"),
        63: ("Rain", "🌧️", "rain"),
        65: ("Heavy Rain", "⛈️", "rain"),
        71: ("Snow", "❄️", "snow"),
        80: ("Showers", "🌦️", "rain"),
        95: ("Thunderstorm", "⛈️", "storm"),
    }
    return mapping.get(code, ("Unknown", "🌡️", "neutral"))

# LIFESTYLE ALGORITHM
def get_lifestyle_tips(temp, rain, uv):
    tips = []
    if rain > 0: tips.append("☂️ Take an umbrella")
    if uv > 5: tips.append("🧴 High UV! Wear sunscreen")
    if temp < 10: tips.append("🧣 Wear a scarf")
    if temp > 25: tips.append("👕 T-shirt weather")
    if 15 <= temp <= 25 and rain == 0: tips.append("🏃 Good for a run")
    return tips if tips else ["✨ Have a great day!"]

# 4. SIDEBAR NAVIGATION
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4052/4052984.png", width=80)
    st.markdown("## 🛰️ WeatherTime Pro")
    
    selected_city = st.selectbox(
        "Global Search", 
        options=POPULAR_CITIES,
        index=POPULAR_CITIES.index("Colombo, Sri Lanka") if "Colombo, Sri Lanka" in POPULAR_CITIES else 0,
    )
    
    st.markdown("---")
    custom_search = st.text_input("Manual Coordinates", placeholder="City Name...")

    if st.button("Sync Node", width="stretch"):
        target = custom_search if custom_search else selected_city
        st.session_state.city_name = target
        st.rerun()
    
    st.markdown("### ⚙️ Premium Settings")
    st.checkbox("High Contrast Mode")
    st.checkbox("Live Satellite Feed (Demo)")

# 5. MAIN HUB LOGIC
payload = get_weather_intel(st.session_state.city_name)

if payload:
    w = payload['data']
    
    # Safely handle 'current' vs 'current_weather' fallback if needed, but we used &current=
    curr = w.get('current', {})
    daily = w.get('daily', {})
    
    # Extract Key Metrics
    temp_now = curr.get('temperature_2m', 0)
    feels_like = curr.get('apparent_temperature', 0)
    w_code = curr.get('weather_code', 0)
    is_day = curr.get('is_day', 1)
    
    cond_text, cond_icon, bg_class = get_condition_intel(w_code, is_day)
    
    # DYNAMIC HERO SECTION
    cols = st.columns([2, 1])
    with cols[0]:
        st.markdown(f'<div class="city-title">{payload["name"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:1.5rem; color:#94a3b8; margin-top:-15px">{payload["country"]} | {datetime.now().strftime("%A, %d %B")}</div>', unsafe_allow_html=True)
        
        st.markdown(f'''
        <div style="display:flex; align-items:center; gap:20px; margin-top:20px">
            <span style="font-size:5rem">{cond_icon}</span>
            <div>
                <div class="current-temp-hero">{temp_now}°</div>
                <div style="font-size:1.5rem; opacity:0.8">{cond_text}</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    with cols[1]:
        # Lifestyle Card
        tips = get_lifestyle_tips(temp_now, curr.get('rain', 0), daily['uv_index_max'][0])
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 💡 AI Insights")
        for t in tips:
            st.markdown(f"**{t}**")
        st.markdown('</div>', unsafe_allow_html=True)

    # DETAILS GRID
    st.markdown("### 📡 Telemetry Grid")
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1: st.metric("Feels Like", f"{feels_like}°")
    with m2: st.metric("Humidity", f"{curr.get('relative_humidity_2m')}%")
    with m3: st.metric("Wind", f"{curr.get('wind_speed_10m')} km/h")
    with m4: st.metric("UV Index", f"{daily['uv_index_max'][0]}")
    with m5: st.metric("Precipitation", f"{curr.get('precipitation', 0)} mm")

    # 7-DAY FORECAST ROW
    st.markdown("---")
    st.subheader("📅 7-Day Forecast")
    
    d_cols = st.columns(7)
    for i in range(7):
        with d_cols[i]:
            day_date = datetime.strptime(daily['time'][i], "%Y-%m-%d")
            day_name = day_date.strftime("%a")
            d_code = daily['weather_code'][i]
            d_min = daily['temperature_2m_min'][i]
            d_max = daily['temperature_2m_max'][i]
            _, d_icon, _ = get_condition_intel(d_code)
            
            st.markdown(f"""
            <div style="text-align:center; padding:10px; background:rgba(255,255,255,0.05); border-radius:10px;">
                <div style="font-weight:bold; color:#38bdf8">{day_name}</div>
                <div style="font-size:2rem; margin:5px 0">{d_icon}</div>
                <div>{d_max}° <span style="font-size:0.8em; opacity:0.6">{d_min}°</span></div>
            </div>
            """, unsafe_allow_html=True)

    # INTERACTIVE CHART REPLACEMENT
    st.markdown("---")
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("📈 Temperature Trend (Next 24 Hours)")
        # Clean data for chart
        hourly = w.get('hourly', {})
        chart_df = pd.DataFrame({
            "Time": pd.to_datetime(hourly['time'][:24]),
            "Temp": hourly['temperature_2m'][:24],
            "Feels": hourly['apparent_temperature'][:24]
        })
        
        fig = px.area(chart_df, x='Time', y=['Temp', 'Feels'], 
                      color_discrete_sequence=["#38bdf8", "#f472b6"])
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="white",
            showlegend=True,
            margin=dict(l=0, r=0, t=0, b=0),
            height=300
        )
        st.plotly_chart(fig, width="stretch")
        
    with c2:
        st.subheader("📍 Geospatial Node")
        map_view = pd.DataFrame({'lat': [payload['lat']], 'lon': [payload['lon']]})
        st.map(map_view, zoom=9)

else:
    st.error(f"Node connection to '{st.session_state.city_name}' failed.")

# CHANGELOG
st.markdown("---")
if os.path.exists("changelog.json"):
    with open("changelog.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        for entry in data:
            with st.expander(f"🚀 v{entry['version']} — {entry['date']}"):
                for n in entry['notes']: st.markdown(f"• {n}")
else:
    st.caption("v1.3.1 | Minor Update | Stability Improvements")
