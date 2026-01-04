# Home.py v1.2.3
import streamlit as st
import requests
import pandas as pd
import json
import os
import time
from datetime import datetime, timezone
import difflib

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Weather Time", layout="wide")

# ---------------- FILES ----------------
FAV_FILE = "favorites.json"
PREF_FILE = "prefs.json"
LAST_DATA_FILE = "last_data.json"

# ---------------- SESSION STATE INIT ----------------
st.session_state.setdefault("ui_mode", "Laptop")
st.session_state.setdefault("continent", "Asia")
st.session_state.setdefault("city", "Colombo, Sri Lanka")
st.session_state.setdefault("unit", "Celsius")
st.session_state.setdefault("wind_unit", "km/h")
st.session_state.setdefault("show_hourly", True)
st.session_state.setdefault("show_daily", True)
st.session_state.setdefault("splash_done", False)
st.session_state.setdefault("last_ui_mode", st.session_state.ui_mode)
st.session_state.setdefault("favorite_cities", [])
st.session_state.setdefault("show_charts_on", True)
st.session_state.setdefault("compact_mode", False)
st.session_state.setdefault("confirm_clear_favs", False)
st.session_state.setdefault("last_fetch_time", None)
st.session_state.setdefault("theme", "light")
st.session_state.setdefault("prefs_loaded", False)

# ---------------- UTILITIES ----------------
def load_json_safe(path):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        return None
    return None

def save_json_safe(path, obj):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

# ---------------- PREFERENCES PERSISTENCE ----------------
def load_prefs():
    prefs = load_json_safe(PREF_FILE) or {}
    # apply prefs to session_state
    st.session_state.theme = prefs.get("theme", st.session_state.theme)
    st.session_state.unit = prefs.get("unit", st.session_state.unit)
    st.session_state.wind_unit = prefs.get("wind_unit", st.session_state.wind_unit)
    st.session_state.compact_mode = prefs.get("compact_mode", st.session_state.compact_mode)
    last_city = prefs.get("last_city")
    if last_city:
        # if last_city exists in favorites or mapping, set it later after mapping load
        st.session_state.setdefault("last_city_pref", last_city)
    st.session_state.prefs_loaded = True

def save_prefs():
    prefs = {
        "theme": st.session_state.theme,
        "unit": st.session_state.unit,
        "wind_unit": st.session_state.wind_unit,
        "compact_mode": st.session_state.compact_mode,
        "last_city": st.session_state.get("last_city_pref", None)
    }
    save_json_safe(PREF_FILE, prefs)

# ---------------- FAVORITES PERSISTENCE ----------------
def load_favorites():
    favs = load_json_safe(FAV_FILE)
    return favs or []

def save_favorites(favs):
    save_json_safe(FAV_FILE, favs)

if not st.session_state.favorite_cities:
    st.session_state.favorite_cities = load_favorites()

# ---------------- THEME CSS ----------------
LIGHT_CSS = """
:root{
  --bg:#FFFFFF;
  --text:#0f1720;
  --muted:#6b7280;
  --card:#f8fafc;
  --accent:#0ea5a4;
}
.stApp, .main, .block-container { background: var(--bg) !important; color: var(--text) !important; }
.stButton>button { background-color: var(--accent) !important; color: white !important; }
"""

DARK_CSS = """
:root{
  --bg:#0b1220;
  --text:#e6eef6;
  --muted:#9aa6b2;
  --card:#0f1724;
  --accent:#06b6d4;
}
.stApp, .main, .block-container { background: var(--bg) !important; color: var(--text) !important; }
.stButton>button { background-color: var(--accent) !important; color: black !important; }
"""

def apply_theme_css():
    css = DARK_CSS if st.session_state.theme == "dark" else LIGHT_CSS
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# ---------------- HELPERS ----------------
def safe_get(lst, i=0, default=0):
    try:
        if lst is None:
            return default
        return lst[i]
    except Exception:
        return default

def convert_temp(celsius):
    if celsius is None:
        return None
    if st.session_state.unit == "Celsius":
        return round(celsius, 1)
    return round((celsius * 9/5) + 32, 1)

def convert_wind(kmh):
    if kmh is None:
        return None
    if st.session_state.wind_unit == "km/h":
        return round(kmh, 1)
    return round(kmh * 0.621371, 1)

def format_age(ts):
    if ts is None:
        return "unknown"
    age_seconds = int((datetime.now(timezone.utc) - ts).total_seconds())
    if age_seconds < 60:
        return f"{age_seconds}s"
    if age_seconds < 3600:
        return f"{age_seconds//60}m"
    return f"{age_seconds//3600}h"

# ---------------- SPLASH ----------------
def show_splash():
    splash_html = """
    <style>
    .splash { position: fixed; inset: 0; background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
      display:flex;flex-direction:column;align-items:center;justify-content:center;color:white;z-index:9999; }
    .icon{font-size:90px} .title{font-size:38px;font-weight:700} .subtitle{opacity:0.85}
    </style>
    <div class="splash"><div class="icon">🌦</div><div class="title">Weather Time</div>
    <div class="subtitle">Preparing your view...</div></div>
    """
    placeholder = st.empty()
    placeholder.markdown(splash_html, unsafe_allow_html=True)
    time.sleep(1.2)
    placeholder.empty()

if not st.session_state.splash_done or st.session_state.ui_mode != st.session_state.last_ui_mode:
    show_splash()
    st.session_state.splash_done = True
    st.session_state.last_ui_mode = st.session_state.ui_mode

# ---------------- HEADER ----------------
# load prefs once at startup
if not st.session_state.prefs_loaded:
    load_prefs()

apply_theme_css()
st.title("🌦 Weather Time")
st.caption("Your personal real-time weather assistant")
st.markdown("---")
st.caption("Version 1.2.3")

# ---------------- SIDEBAR CONTROLS ----------------
st.sidebar.markdown("### 📱 UI Mode")
new_ui = st.sidebar.radio("Select UI Mode", ["Laptop", "Mobile"],
                          index=["Laptop", "Mobile"].index(st.session_state.ui_mode))
if new_ui != st.session_state.ui_mode:
    st.session_state.ui_mode = new_ui
    st.session_state.splash_done = False
    st.rerun()

show_sidebar = st.session_state.ui_mode == "Laptop"

st.sidebar.markdown("### 🌡 Temperature Unit")
unit_choice = st.sidebar.radio("Select Unit", ["Celsius", "Fahrenheit"],
                               index=["Celsius", "Fahrenheit"].index(st.session_state.unit))
if unit_choice != st.session_state.unit:
    st.session_state.unit = unit_choice
    save_prefs()

st.sidebar.markdown("### 💨 Wind Speed Unit")
wind_unit_choice = st.sidebar.radio("Select Wind Speed Unit", ["km/h", "mph"],
                                    index=["km/h", "mph"].index(st.session_state.wind_unit))
if wind_unit_choice != st.session_state.wind_unit:
    st.session_state.wind_unit = wind_unit_choice
    save_prefs()

# Theme toggle
st.sidebar.markdown("### 🎨 Theme")
theme_choice = st.sidebar.radio("Color Mode", ["Light", "Dark"], index=0 if st.session_state.theme=="light" else 1)
new_theme = "dark" if theme_choice == "Dark" else "light"
if new_theme != st.session_state.theme:
    st.session_state.theme = new_theme
    save_prefs()
    apply_theme_css()

# Compact layout toggle
st.sidebar.markdown("### 🧭 Display")
compact_choice = st.sidebar.checkbox("Compact mobile layout", value=st.session_state.compact_mode)
if compact_choice != st.session_state.compact_mode:
    st.session_state.compact_mode = compact_choice
    save_prefs()

# manual refresh
if st.sidebar.button("🔄 Refresh Weather Data"):
    st.cache_data.clear()
    st.rerun()

# clear favorites (sidebar quick)
if st.sidebar.button("🗑 Clear Favorites (quick)"):
    st.session_state.confirm_clear_favs = True

# ---------------- CONTINENTS & CITIES (sample mapping) ----------------
continents = {
    "Custom Coordinates": {"Custom Coordinates": (0.0, 0.0)},
    "North America": {
        "New York, USA": (40.7128, -74.0060),
        "Los Angeles, USA": (34.0522, -118.2437),
        "Toronto, Canada": (43.6532, -79.3832),
        "Mexico City, Mexico": (19.4326, -99.1332),
        "Chicago, USA": (41.8781, -87.6298),
        "Houston, USA": (29.7604, -95.3698),
        "Vancouver, Canada": (49.2827, -123.1207),
        "Montreal, Canada": (45.5017, -73.5673),
        "San Francisco, USA": (37.7749, -122.4194),
        "Miami, USA": (25.7617, -80.1918)
    },
    "South America": {
        "São Paulo, Brazil": (-23.5505, -46.6333),
        "Buenos Aires, Argentina": (-34.6037, -58.3816),
        "Rio de Janeiro, Brazil": (-22.9068, -43.1729),
        "Bogotá, Colombia": (4.7110, -74.0721),
        "Lima, Peru": (-12.0464, -77.0428),
        "Santiago, Chile": (-33.4489, -70.6693),
        "Quito, Ecuador": (-0.1807, -78.4678),
        "Caracas, Venezuela": (10.4806, -66.9036),
        "Montevideo, Uruguay": (-34.9011, -56.1645),
        "La Paz, Bolivia": (-16.4897, -68.1193),
        "Asunción, Paraguay": (-25.2637, -57.6740),
        "Georgetown, Guyana": (6.8013, -58.1551),
        "Paramaribo, Suriname": (5.8232, -55.1679),
        "Cayenne, French Guiana": (4.9224, -52.3135)
    },
    "Europe": {
        "London, UK": (51.5074, -0.1278),
        "Paris, France": (48.8566, 2.3522),
        "Berlin, Germany": (52.5200, 13.4050),
        "Madrid, Spain": (40.4168, -3.7038),
        "Rome, Italy": (41.9028, 12.4964),
        "Amsterdam, Netherlands": (52.3676, 4.9041),
        "Vienna, Austria": (48.2082, 16.3738),
        "Stockholm, Sweden": (59.3293, 18.0686),
        "Prague, Czech Republic": (50.0755, 14.4378),
        "Lisbon, Portugal": (38.7223, -9.1393),
        "Dublin, Ireland": (53.3498, -6.2603),
        "Brussels, Belgium": (50.8503, 4.3517),
        "Copenhagen, Denmark": (55.6761, 12.5683),
        "Helsinki, Finland": (60.1695, 24.9354),
        "Warsaw, Poland": (52.2297, 21.0122),
        "Athens, Greece": (37.9838, 23.7275),
        "Budapest, Hungary": (47.4979, 19.0402),
        "Oslo, Norway": (59.9139, 10.7522),
        "Zagreb, Croatia": (45.8150, 15.9819),
        "Belgrade, Serbia": (44.7866, 20.4489)
    },
    "Asia": {
        "Tokyo, Japan": (35.6895, 139.6917),
        "Delhi, India": (28.6139, 77.2090),
        "Shanghai, China": (31.2304, 121.4737),
        "Beijing, China": (39.9042, 116.4074),
        "Mumbai, India": (19.0760, 72.8777),
        "Seoul, South Korea": (37.5665, 126.9780),
        "Bangkok, Thailand": (13.7563, 100.5018),
        "Jakarta, Indonesia": (-6.2088, 106.8456),
        "Singapore, Singapore": (1.3521, 103.8198),
        "Kuala Lumpur, Malaysia": (3.1390, 101.6869),
        "Colombo, Sri Lanka": (6.9271, 79.8612),
        "Dhaka, Bangladesh": (23.8103, 90.4125),
        "Manila, Philippines": (14.5995, 120.9842),
        "Hanoi, Vietnam": (21.0278, 105.8342),
        "Taipei, Taiwan": (25.0330, 121.5654)
    },
    "Africa": {
        "Cairo, Egypt": (30.0444, 31.2357),
        "Lagos, Nigeria": (6.5244, 3.3792),
        "Johannesburg, South Africa": (-26.2041, 28.0473),
        "Nairobi, Kenya": (-1.2921, 36.8219),
        "Casablanca, Morocco": (33.5731, -7.5898),
        "Accra, Ghana": (5.6037, -0.1870),
        "Addis Ababa, Ethiopia": (8.9806, 38.7578),
        "Dakar, Senegal": (14.6928, -17.4467),
        "Kigali, Rwanda": (-1.9706, 30.1044),
        "Tunis, Tunisia": (36.8065, 10.1815)
    },
    "Oceania": {
        "Sydney, Australia": (-33.8688, 151.2093),
        "Melbourne, Australia": (-37.8136, 144.9631),
        "Brisbane, Australia": (-27.4698, 153.0251),
        "Auckland, New Zealand": (-36.8485, 174.7633),
        "Wellington, New Zealand": (-41.2865, 174.7762),
        "Perth, Australia": (-31.9505, 115.8605),
        "Suva, Fiji": (-18.1248, 178.4501),
        "Port Moresby, Papua New Guinea": (-9.4438, 147.1803),
        "Honolulu, USA (Hawaii)": (21.3069, -157.8583),
        "Apia, Samoa": (-13.8507, -171.7514),
        "Nouméa, New Caledonia": (-22.2670, 166.4583),
        "Port Vila, Vanuatu": (-17.7401, 168.3095)
    },
    "Antarctica": {
        "McMurdo Station": (-77.8419, 166.6863),
        "Palmer Station": (-64.7741, -64.0531),
        "Rothera Research Station": (-67.5681, -68.1230),
        "Davis Station": (-68.5766, 77.9674),
        "Mawson Station": (-67.6027, 62.8738),
        "Casey Station": (-66.2818, 110.5276),
        "Vostok Station": (-78.4644, 106.8320),
        "Dumont d'Urville Station": (-66.6581, 140.0010),
        "Syowa Station": (-69.0000, 39.5833),
        "Concordia Station": (-75.1000, 123.3500)
    }
}


def safe_city_index(city, cities_list):
    return cities_list.index(city) if city in cities_list else 0

# build flattened city list for search
_flat_city_list = []
for cont, cities in continents.items():
    for city_name in cities.keys():
        _flat_city_list.append(city_name)

# If prefs had last city, try to set it
if st.session_state.get("last_city_pref"):
    pref = st.session_state.get("last_city_pref")
    if pref in _flat_city_list:
        st.session_state.city = pref
        # find continent
        for cont, cities in continents.items():
            if pref in cities:
                st.session_state.continent = cont
                break

# ---------------- LOCATION UI ----------------
if show_sidebar:
    st.sidebar.markdown("### 🌍 Location")
    st.session_state.continent = st.sidebar.selectbox("Select Continent", list(continents.keys()),
                                                      index=safe_city_index(st.session_state.continent, list(continents.keys())))
    cities = list(continents[st.session_state.continent].keys())
    if st.session_state.city not in cities:
        st.session_state.city = cities[0]
    st.session_state.city = st.sidebar.selectbox("Select City", cities,
                                                index=safe_city_index(st.session_state.city, cities))
    st.sidebar.subheader("⭐ Favorite Cities")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        fav_input = st.sidebar.text_input("Add a city", "")
    with col2:
        if st.sidebar.button("Add to Favorites") and fav_input.strip():
            new_city = fav_input.strip()
            if new_city not in st.session_state.favorite_cities:
                st.session_state.favorite_cities.append(new_city)
                save_favorites(st.session_state.favorite_cities)
                st.sidebar.success("Added")
            else:
                st.sidebar.info("Already in favorites")
    if st.session_state.favorite_cities:
        remove_city = st.sidebar.selectbox("Remove favorite", [""] + st.session_state.favorite_cities)
        if st.sidebar.button("Remove") and remove_city:
            st.session_state.favorite_cities = [c for c in st.session_state.favorite_cities if c != remove_city]
            save_favorites(st.session_state.favorite_cities)
        st.sidebar.write(", ".join(st.session_state.favorite_cities))
else:
    st.subheader("🌍 Location")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.continent = st.selectbox("Continent", list(continents.keys()),
                                                  index=safe_city_index(st.session_state.continent, list(continents.keys())),
                                                  label_visibility="collapsed")
    cities = list(continents[st.session_state.continent].keys())
    if st.session_state.city not in cities:
        st.session_state.city = cities[0]
    with col2:
        st.session_state.city = st.selectbox("City", cities,
                                            index=safe_city_index(st.session_state.city, cities),
                                            label_visibility="collapsed")
    st.subheader("⭐ Favorite Cities")
    col1, col2 = st.columns(2)
    with col1:
        fav_input = st.text_input("Add a city", "")
    with col2:
        if st.button("Add to Favorites") and fav_input.strip():
            new_city = fav_input.strip()
            if new_city not in st.session_state.favorite_cities:
                st.session_state.favorite_cities.append(new_city)
                save_favorites(st.session_state.favorite_cities)
                st.success("Added")
            else:
                st.info("Already in favorites")
    if st.session_state.favorite_cities:
        remove_city = st.selectbox("Remove favorite", [""] + st.session_state.favorite_cities)
        if st.button("Remove") and remove_city:
            st.session_state.favorite_cities = [c for c in st.session_state.favorite_cities if c != remove_city]
            save_favorites(st.session_state.favorite_cities)
        st.write(", ".join(st.session_state.favorite_cities))

# ---------------- COORDINATES ----------------
try:
    lat, lon = continents[st.session_state.continent][st.session_state.city]
except Exception:
    lat, lon = (0.0, 0.0)

if st.session_state.city == "Custom Coordinates":
    lat = st.number_input("Latitude", value=lat if lat is not None else 0.0, format="%.6f")
    lon = st.number_input("Longitude", value=lon if lon is not None else 0.0, format="%.6f")
    if lat < -90 or lat > 90 or lon < -180 or lon > 180:
        st.warning("⚠ Please enter valid coordinates.")
        st.stop()

# ---------------- SEARCHABLE CITY LOOKUP ----------------
st.markdown("### 🔎 Quick city search")
search_input = st.text_input("Type a city name (fuzzy search)", "")
if search_input:
    # use difflib to find close matches
    matches = difflib.get_close_matches(search_input, _flat_city_list, n=10, cutoff=0.4)
    if matches:
        sel = st.selectbox("Matches", [""] + matches)
        if sel:
            # set continent and city
            for cont, cities in continents.items():
                if sel in cities:
                    st.session_state.continent = cont
                    st.session_state.city = sel
                    st.session_state.last_city_pref = sel
                    save_prefs()
                    st.experimental_rerun()
    else:
        st.info("No close matches found. Try a different spelling or add custom coordinates.")

# ---------------- MAP DISPLAY ----------------
# Build map DataFrame without using deprecated .append()
records = []

# selected city (only add if lat/lon are valid numbers)
try:
    sel_lat = float(lat)
    sel_lon = float(lon)
    records.append({"lat": sel_lat, "lon": sel_lon, "name": st.session_state.city})
except Exception:
    pass

# favorites that exist in mapping
for fav in st.session_state.favorite_cities:
    for cont, cities in continents.items():
        if fav in cities:
            f_lat, f_lon = cities[fav]
            try:
                records.append({"lat": float(f_lat), "lon": float(f_lon), "name": fav})
            except Exception:
                continue

# create DataFrame once
if records:
    map_df = pd.DataFrame.from_records(records, columns=["lat", "lon", "name"])
    # ensure numeric and drop invalid rows
    map_df["lat"] = pd.to_numeric(map_df["lat"], errors="coerce")
    map_df["lon"] = pd.to_numeric(map_df["lon"], errors="coerce")
    map_df = map_df.dropna(subset=["lat", "lon"])
else:
    map_df = pd.DataFrame(columns=["lat", "lon", "name"])

# render map if we have valid points
if not map_df.empty:
    st.map(map_df[["lat", "lon"]])
else:
    st.info("No valid coordinates to display on the map.")

# ---------------- WEATHER API with OFFLINE FALLBACK ----------------
@st.cache_data(ttl=600)
def fetch_weather(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&"
        "current_weather=true&hourly=temperature_2m,precipitation,wind_speed_10m,relativehumidity_2m&"
        "daily=temperature_2m_max,temperature_2m_min,uv_index_max,precipitation_sum&timezone=auto"
    )
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return {}

with st.spinner("🌦 Fetching weather data..."):
    data = fetch_weather(lat, lon)
    if data:
        # save last known good data
        save_json_safe(LAST_DATA_FILE, {"fetched_at": datetime.now(timezone.utc).isoformat(), "lat": lat, "lon": lon, "data": data})
        st.session_state.last_fetch_time = datetime.now(timezone.utc)
    else:
        # try offline fallback
        last = load_json_safe(LAST_DATA_FILE)
        if last and "data" in last:
            data = last["data"]
            # set last_fetch_time from saved timestamp if available
            try:
                st.session_state.last_fetch_time = datetime.fromisoformat(last.get("fetched_at")).astimezone(timezone.utc)
            except Exception:
                st.session_state.last_fetch_time = None
            st.warning("Using last known data (offline fallback). Some values may be stale.")
        else:
            st.error("Failed to fetch weather data and no cached data available.")
            st.stop()

# ---------------- LAST UPDATED & CACHE INFO ----------------
CACHE_TTL_SECONDS = 600
age_display = format_age(st.session_state.get("last_fetch_time"))
remaining = max(0, CACHE_TTL_SECONDS - int((datetime.now(timezone.utc) - st.session_state.get("last_fetch_time")).total_seconds())) if st.session_state.get("last_fetch_time") else 0
cache_hint = f"🔁 Cached (expires in {remaining//60}m {remaining%60}s)" if remaining > 0 else "🔁 Cache expired / fresh fetch"
st.caption(f"⏱ Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} — Age: {age_display} — {cache_hint}")

curr = data.get("current_weather", {})
hourly = data.get("hourly", {})
daily = data.get("daily", {})

# ---------------- BUILD DATAFRAMES ----------------
hourly_times = hourly.get("time", []) or []
hourly_temps = hourly.get("temperature_2m", []) or []
hourly_rain = hourly.get("precipitation", []) or []
hourly_wind = hourly.get("wind_speed_10m", []) or []
hourly_humidity = hourly.get("relativehumidity_2m", []) or []

try:
    hourly_df = pd.DataFrame({
        "Time": pd.to_datetime(hourly_times),
        "Temp_C": hourly_temps,
        "Temp": [convert_temp(t) if t is not None else None for t in hourly_temps],
        "Rain": hourly_rain,
        "Wind_kmh": hourly_wind,
        "Wind": [convert_wind(w) if w is not None else None for w in hourly_wind],
        "Humidity": hourly_humidity
    })
except Exception:
    hourly_df = pd.DataFrame(columns=["Time", "Temp", "Rain", "Wind", "Humidity"])

daily_times = daily.get("time", []) or []
daily_min = daily.get("temperature_2m_min", []) or []
daily_max = daily.get("temperature_2m_max", []) or []
daily_uv = daily.get("uv_index_max", []) or []
daily_precip = daily.get("precipitation_sum", []) or []

try:
    daily_df = pd.DataFrame({
        "Date": pd.to_datetime(daily_times),
        "Min Temp": [convert_temp(t) if t is not None else None for t in daily_min],
        "Max Temp": [convert_temp(t) if t is not None else None for t in daily_max],
        "UV": daily_uv,
        "Precip": daily_precip
    })
except Exception:
    daily_df = pd.DataFrame(columns=["Date", "Min Temp", "Max Temp", "UV", "Precip"])

# ---------------- METRICS ----------------
temperature_c = curr.get("temperature") if curr else None
temperature = convert_temp(temperature_c)
wind_kmh_now = curr.get("windspeed") if curr else None
wind_display = convert_wind(wind_kmh_now)
rain_now = safe_get(hourly_rain, 0, 0)
uv_today = safe_get(daily_uv, 0, 0)
hourly_humidity_val = safe_get(hourly_humidity, 0, 'N/A')

unit_symbol = "°C" if st.session_state.unit == "Celsius" else "°F"
wind_symbol = st.session_state.wind_unit

# ---------------- METRICS DISPLAY ----------------
if st.session_state.compact_mode:
    cols = st.columns([1,1,1,1])
    cols[0].metric("🌡", f"{temperature if temperature is not None else 'N/A'}{unit_symbol}")
    cols[1].metric("💨", f"{wind_display if wind_display is not None else 'N/A'}{wind_symbol}")
    cols[2].metric("💧", f"{hourly_humidity_val}%")
    cols[3].metric("🌧", f"{rain_now}mm")
    with st.expander("Show charts"):
        if st.session_state.show_charts_on and not hourly_df.empty:
            st.line_chart(hourly_df.set_index("Time")[["Temp"]].rename(columns={"Temp": f"Temp ({unit_symbol})"}))
            st.bar_chart(hourly_df.set_index("Time")[["Rain"]])
            st.line_chart(hourly_df.set_index("Time")[["Wind"]])
else:
    st.subheader("🌟 Current Weather")
    c1, c2, c3, c4 = st.columns(4)

    # Temperature trend
    temp_trend = None
    if not hourly_df.empty and "Temp" in hourly_df.columns and len(hourly_df) > 1:
        prev_temp = hourly_df["Temp"].iloc[-2]
        curr_temp = hourly_df["Temp"].iloc[-1]
        if prev_temp is not None and curr_temp is not None:
            temp_trend = "↑" if curr_temp > prev_temp else "↓" if curr_temp < prev_temp else "→"

    # Wind trend
    wind_trend = None
    if not hourly_df.empty and "Wind" in hourly_df.columns and len(hourly_df) > 1:
        prev_wind = hourly_df["Wind"].iloc[-2]
        curr_wind = hourly_df["Wind"].iloc[-1]
        if prev_wind is not None and curr_wind is not None:
            wind_trend = "↑" if curr_wind > prev_wind else "↓" if curr_wind < prev_wind else "→"

    # Rain trend
    rain_trend = None
    if not hourly_df.empty and "Rain" in hourly_df.columns and len(hourly_df) > 1:
        prev_rain = hourly_df["Rain"].iloc[-2]
        curr_rain = hourly_df["Rain"].iloc[-1]
        if prev_rain is not None and curr_rain is not None:
            rain_trend = "↑" if curr_rain > prev_rain else "↓" if curr_rain < prev_rain else "→"

    c1.metric("🌡 Temp", f"{temperature if temperature is not None else 'N/A'} {unit_symbol}", temp_trend)
    c2.metric("💨 Wind", f"{wind_display if wind_display is not None else 'N/A'} {wind_symbol}", wind_trend)
    c3.metric("💧 Humidity", f"{hourly_humidity_val}%")
    c4.metric("🌧 Rain", f"{rain_now} mm", rain_trend)

# ---------------- CLOTHING ----------------
st.subheader("👕 Clothing Recommendation")
clothing = []
if temperature_c is None:
    clothing.append("No temperature data available")
else:
    if temperature_c >= 32:
        clothing.append("🩳 Light clothing")
    elif temperature_c >= 22:
        clothing.append("👕 Comfortable wear")
    else:
        clothing.append("🧥 Jacket recommended")
if rain_now > 1:
    clothing.append("☔ Umbrella")
if wind_kmh_now and wind_kmh_now > 25:
    clothing.append("🧢 Windbreaker")
if uv_today and uv_today > 7:
    clothing.append("🕶 Sunscreen")
st.success(" • ".join(clothing))

# ---------------- PRECIPITATION ----------------
st.subheader("🌧 Precipitation Details")
rain_today = safe_get(daily_precip, 0, 0)
p1, p2, p3 = st.columns(3)
p1.metric("Now", f"{rain_now} mm")
p2.metric("Today", f"{rain_today} mm")
if rain_now == 0:
    intensity = "☀️ No Rain"
elif rain_now < 1:
    intensity = "🌦 Light"
elif rain_now < 5:
    intensity = "🌧 Moderate"
else:
    intensity = "⛈ Heavy"
p3.metric("Intensity", intensity)

# ---------------- CHART CONTROLS ----------------
if show_sidebar:
    st.sidebar.markdown("### 📊 Chart Controls")
    st.session_state.show_charts_on = st.sidebar.checkbox("Show Charts", value=st.session_state.show_charts_on)
else:
    with st.expander("📊 Chart Controls"):
        st.session_state.show_charts_on = st.checkbox("Show Charts", value=st.session_state.show_charts_on)

# ---------------- TABS ----------------
tab1, tab2, tab3 = st.tabs(["📊 Hourly Charts", "📅 Daily Charts", "⚠ Alerts & Tips"])

with tab1:
    st.subheader("📊 Hourly")
    if st.session_state.show_charts_on and not hourly_df.empty:
        st.line_chart(hourly_df.set_index("Time")[["Temp"]].rename(columns={"Temp": f"Temp ({unit_symbol})"}))
        st.subheader("🌧 Hourly Rainfall")
        st.bar_chart(hourly_df.set_index("Time")[["Rain"]])
        st.subheader(f"💨 Hourly Wind Speed ({wind_symbol})")
        st.line_chart(hourly_df.set_index("Time")[["Wind"]])
        st.subheader("📋 Hourly Data")
        st.dataframe(hourly_df[["Time", "Temp", "Rain", "Wind", "Humidity"]], use_container_width=True)
        st.download_button("⬇ Download Hourly Data (CSV)",
                           hourly_df[["Time", "Temp", "Rain", "Wind", "Humidity"]].to_csv(index=False).encode("utf-8"),
                           "hourly_weather.csv", "text/csv")
    else:
        st.info("Hourly charts are hidden or no hourly data available")

with tab2:
    st.subheader("📅 Daily")
    if st.session_state.show_charts_on and not daily_df.empty:
        st.area_chart(daily_df.set_index("Date")[["Min Temp", "Max Temp"]])
        st.subheader("☀️ Daily UV Index")
        st.bar_chart(daily_df.set_index("Date")[["UV"]])
        st.subheader("📋 Daily Data")
        st.dataframe(daily_df, use_container_width=True)
        st.download_button("⬇ Download Daily Data (CSV)",
                           daily_df.to_csv(index=False).encode("utf-8"),
                           "daily_weather.csv", "text/csv")
    else:
        st.info("Daily charts are hidden or no daily data available")

with tab3:
    if uv_today and uv_today > 7:
        st.warning("☀️ High UV today")
    if temperature_c and temperature_c > 35:
        st.warning("🔥 Extreme heat")
    if wind_kmh_now and wind_kmh_now > 30:
        st.warning("💨 Strong winds")
    st.markdown("### 💡 Tips")
    st.write("- Stay hydrated")
    st.write("- Dress smart")
    st.write("- Check updates hourly")

# ---------------- FAVORITES (MAIN) ----------------
st.subheader("⭐ Favorite Cities")
col1, col2 = st.columns(2)
with col1:
    main_fav_input = st.text_input("Add a city", "")
with col2:
    if st.button("Add to Favorites") and main_fav_input.strip():
        new_city = main_fav_input.strip()
        if new_city not in st.session_state.favorite_cities:
            st.session_state.favorite_cities.append(new_city)
            save_favorites(st.session_state.favorite_cities)
            st.success("Added")
        else:
            st.info("Already in favorites")

if st.session_state.favorite_cities:
    st.write("Your favorites:")
    for i, fav in enumerate(st.session_state.favorite_cities):
        cols = st.columns([4,1,1,1,1])
        cols[0].write(fav)
        if cols[1].button("↑", key=f"fav_up_{i}"):
            if i > 0:
                st.session_state.favorite_cities[i-1], st.session_state.favorite_cities[i] = st.session_state.favorite_cities[i], st.session_state.favorite_cities[i-1]
                save_favorites(st.session_state.favorite_cities)
                st.experimental_rerun()
        if cols[2].button("↓", key=f"fav_down_{i}"):
            if i < len(st.session_state.favorite_cities)-1:
                st.session_state.favorite_cities[i+1], st.session_state.favorite_cities[i] = st.session_state.favorite_cities[i], st.session_state.favorite_cities[i+1]
                save_favorites(st.session_state.favorite_cities)
                st.experimental_rerun()
        if cols[3].button("Go", key=f"fav_go_{i}"):
            # try to set continent and city
            found = False
            for cont, cities in continents.items():
                if fav in cities:
                    st.session_state.continent = cont
                    st.session_state.city = fav
                    st.session_state.last_city_pref = fav
                    save_prefs()
                    st.experimental_rerun()
                    found = True
                    break
            if not found:
                st.info("Favorite not in built-in list. Select manually or add coordinates.")
        if cols[4].button("Remove", key=f"fav_remove_{i}"):
            st.session_state.favorite_cities = [c for c in st.session_state.favorite_cities if c != fav]
            save_favorites(st.session_state.favorite_cities)
            st.experimental_rerun()

    # Clear all with confirmation
    if st.session_state.confirm_clear_favs:
        st.warning("Are you sure you want to clear all favorites?")
        c1, c2 = st.columns(2)
        if c1.button("Yes, clear all"):
            st.session_state.favorite_cities = []
            save_favorites(st.session_state.favorite_cities)
            st.session_state.confirm_clear_favs = False
            st.experimental_rerun()
        if c2.button("Cancel"):
            st.session_state.confirm_clear_favs = False
    else:
        if st.button("🗑 Clear Favorites"):
            st.session_state.confirm_clear_favs = True

# ---------------- SHAREABLE SNAPSHOT ----------------
st.markdown("### 📤 Share / Export")
summary = f"{st.session_state.city} — Temp: {temperature if temperature is not None else 'N/A'}{unit_symbol}, Wind: {wind_display if wind_display is not None else 'N/A'}{wind_symbol}, Rain: {rain_now} mm"
st.write(summary)
# download text snapshot
st.download_button("⬇ Download snapshot (text)", summary.encode("utf-8"), file_name="weather_snapshot.txt", mime="text/plain")

# ---------------- SAVE LAST CITY PREF ----------------
# Save last selected city to prefs for persistence
st.session_state.last_city_pref = st.session_state.city
save_prefs()

# ---------------- END ----------------
