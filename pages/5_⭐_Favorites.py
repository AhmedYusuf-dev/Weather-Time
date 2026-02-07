import streamlit as st
import json
import os
import requests
from datetime import datetime

# PAGE CONFIG
st.set_page_config(page_title="Favorites | WeatherTime Pro", layout="wide", page_icon="⭐")

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

# Favorites file path
FAVORITES_FILE = "favorites.json"

# Load favorites
def load_favorites():
    if os.path.exists(FAVORITES_FILE):
        try:
            with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
        except:
            pass
    return []

# Save favorites
def save_favorites(favorites):
    with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
        json.dump(favorites, f, indent=2)

# Get weather
def get_weather_quick(city_name):
    city = city_name.split(",")[0]
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        geo_res = requests.get(geo_url).json()
        if not geo_res.get("results"): return None
        
        loc = geo_res["results"][0]
        w_url = (f"https://api.open-meteo.com/v1/forecast?latitude={loc['latitude']}&longitude={loc['longitude']}"
                 "&current=temperature_2m,weather_code,precipitation"
                 "&daily=temperature_2m_max,temperature_2m_min"
                 "&timezone=auto")
        
        weather_data = requests.get(w_url).json()
        return {
            "name": loc["name"],
            "country": loc.get("country", ""),
            "data": weather_data
        }
    except:
        return None

def get_weather_icon(code):
    mapping = {
        0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️",
        45: "🌫️", 48: "🌫️", 51: "🌦️", 53: "🌧️",
        61: "🌦️", 63: "🌧️", 65: "⛈️", 71: "❄️",
        80: "🌦️", 95: "⛈️"
    }
    return mapping.get(code, "🌡️")

# HEADER
st.markdown('<h1 class="city-title">⭐ Favorite Locations</h1>', unsafe_allow_html=True)
st.markdown("Save and track weather for your favorite places")

# Load current favorites
favorites = load_favorites()

# ADD NEW FAVORITE
st.markdown("---")
st.subheader("➕ Add New Favorite")

col1, col2 = st.columns([3, 1])
with col1:
    new_city = st.text_input("Enter city name:", placeholder="e.g. Tokyo, Japan")
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Add to Favorites", width="stretch"):
        if new_city and new_city not in favorites:
            favorites.append(new_city)
            save_favorites(favorites)
            st.success(f"✅ Added {new_city} to favorites!")
            st.rerun()
        elif new_city in favorites:
            st.warning("City already in favorites!")

# DISPLAY FAVORITES
if favorites:
    st.markdown("---")
    st.subheader(f"📍 Your Favorites ({len(favorites)})")
    
    # Quick overview grid
    cols_per_row = 3
    for i in range(0, len(favorites), cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            idx = i + j
            if idx < len(favorites):
                city = favorites[idx]
                weather = get_weather_quick(city)
                
                with cols[j]:
                    if weather:
                        curr = weather['data'].get('current', {})
                        daily = weather['data'].get('daily', {})
                        
                        temp = curr.get('temperature_2m', 0)
                        w_code = curr.get('weather_code', 0)
                        temp_max = daily.get('temperature_2m_max', [0])[0]
                        temp_min = daily.get('temperature_2m_min', [0])[0]
                        
                        icon = get_weather_icon(w_code)
                        
                        st.markdown(f"""
                        <div style="background:rgba(255,255,255,0.05); padding:20px; border-radius:15px; text-align:center; min-height:220px">
                            <h4 style="color:#38bdf8">{weather['name']}</h4>
                            <div style="color:#94a3b8; font-size:0.85rem; margin-bottom:10px">{weather['country']}</div>
                            <div style="font-size:3rem; margin:10px 0">{icon}</div>
                            <div style="font-size:2rem; font-weight:bold; margin:10px 0">{temp}°C</div>
                            <div style="color:#94a3b8; font-size:0.9rem">
                                H: {temp_max}° L: {temp_min}°
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button(f"🗑️ Remove", key=f"remove_{idx}", width="stretch"):
                            favorites.remove(city)
                            save_favorites(favorites)
                            st.rerun()
                    else:
                        st.markdown(f"""
                        <div style="background:rgba(255,255,255,0.05); padding:20px; border-radius:15px; text-align:center">
                            <h4>{city}</h4>
                            <div style="color:#ef4444; margin:20px 0">❌ Unable to load</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button(f"🗑️ Remove", key=f"remove_{idx}", width="stretch"):
                            favorites.remove(city)
                            save_favorites(favorites)
                            st.rerun()
    
    # COMPARISON TABLE
    st.markdown("---")
    st.subheader("📊 Quick Comparison")
    
    comparison_data = []
    for city in favorites:
        weather = get_weather_quick(city)
        if weather:
            curr = weather['data'].get('current', {})
            daily = weather['data'].get('daily', {})
            
            comparison_data.append({
                "City": f"{weather['name']}, {weather['country']}",
                "Temp": f"{curr.get('temperature_2m', 0)}°C",
                "High": f"{daily.get('temperature_2m_max', [0])[0]}°C",
                "Low": f"{daily.get('temperature_2m_min', [0])[0]}°C",
                "Condition": get_weather_icon(curr.get('weather_code', 0))
            })
    
    if comparison_data:
        import pandas as pd
        df = pd.DataFrame(comparison_data)
        st.dataframe(df, width="stretch", hide_index=True)
    
    # EXPORT/IMPORT
    st.markdown("---")
    st.subheader("💾 Backup & Restore")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Export Favorites**")
        favorites_json = json.dumps(favorites, indent=2)
        st.download_button(
            label="📥 Download Favorites",
            data=favorites_json,
            file_name=f"weathertime_favorites_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            width="stretch"
        )
    
    with col2:
        st.markdown("**Import Favorites**")
        uploaded_file = st.file_uploader("Choose a JSON file", type=['json'])
        if uploaded_file:
            try:
                imported = json.load(uploaded_file)
                if isinstance(imported, list):
                    # Merge with existing
                    for city in imported:
                        if city not in favorites:
                            favorites.append(city)
                    save_favorites(favorites)
                    st.success(f"✅ Imported {len(imported)} locations!")
                    st.rerun()
            except:
                st.error("Invalid file format")
    
    # CLEAR ALL
    st.markdown("---")
    if st.button("🗑️ Clear All Favorites", type="secondary"):
        if st.session_state.get('confirm_clear'):
            favorites.clear()
            save_favorites(favorites)
            st.session_state.confirm_clear = False
            st.rerun()
        else:
            st.session_state.confirm_clear = True
            st.warning("Click again to confirm deletion of all favorites")

else:
    st.info("📍 No favorites yet! Add your first location above.")
