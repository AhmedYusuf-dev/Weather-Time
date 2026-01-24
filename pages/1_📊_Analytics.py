import streamlit as st
import plotly.express as px
import pandas as pd
import os

st.set_page_config(page_title="Analytics", layout="wide")

# Safe Loading
if st.session_state.get("weather_data") is None:
    st.warning("📡 Please search for a city on the Home page first.")
    st.stop()

# Apply CSS
with open("assets/style.css") as f: st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title(f"📊 Deep Analytics: {st.session_state.city_name}")
w = st.session_state.weather_data
df = pd.DataFrame({"Time": pd.to_datetime(w['hourly']['time'][:48]), "Temp": w['hourly']['temperature_2m'][:48]})
fig = px.line(df, x="Time", y="Temp", template="plotly_dark", title="48h Temperature Flow")
st.plotly_chart(fig, use_container_width=True)