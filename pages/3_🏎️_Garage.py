import streamlit as st

st.set_page_config(page_title="Garage Hub", layout="wide")

# Gatekeeper
if st.session_state.get("weather_data") is None:
    st.error("Garage Node Offline. Search on Home Page.")
    st.stop()

# Safe Precipitation Extraction
w = st.session_state.weather_data
hourly = w.get('hourly', {})
total_rain = sum(hourly.get('precipitation', [0])[:24])

st.title("🏎️ Garage & Scouts")
if total_rain > 0.5:
    st.error(f"❌ Don't Wash Car: {total_rain}mm rain expected.")
else:
    st.success("✅ Clear to Wash: Dry window detected.")