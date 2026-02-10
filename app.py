import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

#Page Config
st.set_page_config(
    page_title="Professional Weather Dashboard",
    page_icon="🌦️",
    layout="wide"
)

#Custom CSS
st.markdown("""
<style>
.stApp {
    background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
    color: white;
}
div[data-testid="metric-container"] {
    background-color: rgba(255,255,255,0.1);
    padding: 15px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

#Load API Key
API_KEY = os.getenv("API_KEY")

if not API_KEY:
    st.error("❌ API Key not found! Please set the API_KEY environment variable.")
    st.stop()

#Sidebar
st.sidebar.title("🌍 Search Location")
city = st.sidebar.selectbox("Select City", ["Karachi", "Lahore", "Islamabad", "Peshawar", "Multan", "Faisalabad", "Rawalpindi"])
search_btn = st.sidebar.button("Search")

st.title("🌦️ Advanced Weather Dashboard")
st.markdown("---")
if not city:
    st.info("👈 Select a city from the dropdown")
    st.stop()
    
#Geo Location
geo_url = f"https://api.openweathermap.org/geo/1.0/direct?q={city},PK&limit=1&appid={API_KEY}"
geo_resp = requests.get(geo_url).json()

if not isinstance(geo_resp, list) or len(geo_resp) == 0:
    st.error("City not found!")
    st.stop()

if "lat" not in geo_resp[0] or "lon" not in geo_resp[0]:
    st.error("Invalid location data!")
    st.stop()

lat = geo_resp[0]["lat"]
lon = geo_resp[0]["lon"]

#Current Weather
weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
weather = requests.get(weather_url).json()

if weather.get("cod") != 200:
    st.error("Weather API error")
    st.stop()

icon_code = weather["weather"][0]["icon"]
icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"

#Header
col1, col2 = st.columns([1,3])

with col1:
    st.image(icon_url)

with col2:
    st.subheader(f"📍 {city.title()}")
    st.write(weather["weather"][0]["description"].title())

st.markdown("---")

#Main Metrics
col1, col2, col3, col4 = st.columns(4) 
with col1:
    st.metric("🌡 Temperature (°C)", weather["main"]["temp"])

with col2:
    st.metric("🤒 Feels Like", weather["main"]["feels_like"])

with col3:
    st.metric("💧 Humidity (%)", weather["main"]["humidity"])

with col4:
    st.metric("🌬 Wind Speed (m/s)", weather["wind"]["speed"])

#Extra Info
col5, col6, col7, col8 = st.columns(4)

with col5:
    st.metric("🔵 Pressure (hPa)", weather["main"]["pressure"])

with col6:
    st.metric("👁 Visibility (m)", weather["visibility"])

with col7:
    st.metric("☁️ Clouds (%)", weather["clouds"]["all"])

with col8:
    sunrise = datetime.fromtimestamp(weather["sys"]["sunrise"])
    sunset = datetime.fromtimestamp(weather["sys"]["sunset"])
    st.write(f"🌅 Sunrise: {sunrise.strftime('%I:%M %p')}")
    st.write(f"🌇 Sunset: {sunset.strftime('%I:%M %p')}")

st.markdown("---")

#Forecast 
forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
forecast = requests.get(forecast_url).json()

if forecast.get("cod") != "200":
    st.error("Forecast API error")
    st.stop()

df = pd.DataFrame(forecast["list"])
df["date"] = pd.to_datetime(df["dt_txt"])
df["temp"] = df["main"].apply(lambda x: x["temp"])

st.subheader("📈 5-Day Temperature Forecast")

fig = px.line(
    df,
    x="date",
    y="temp",
    markers=True,
    template="plotly_dark"
)

fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Temperature (°C)"
)

st.plotly_chart(fig, use_container_width=True)

#Daily Sumary
st.markdown("---")
st.subheader("📅 Daily Summary")

df["day"] = df["date"].dt.date
daily = df.groupby("day")["temp"].mean().reset_index()

cols = st.columns(len(daily))

for i in range(len(daily)):
    with cols[i]:
        st.metric(str(daily["day"][i]), round(daily["temp"][i],1))