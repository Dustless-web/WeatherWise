import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="WeatherWise Pro",
    page_icon="⛈️",
    layout="wide",  # Uses the full width of the screen
    initial_sidebar_state="expanded"
)

# --- 2. CUSTOM CSS FOR "GLASS" LOOK ---
# --- 2. CUSTOM CSS FOR VISIBLE CARDS ---
st.markdown("""
    <style>
    /* Styles for the metric cards (Temperature, Humidity, etc.) */
    [data-testid="stMetric"] {
        background-color: #262730; /* Darker background for contrast */
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3); /* Slightly stronger shadow */
        color: white; /* Ensures text is white */
    }
    
    /* Styles for the labels within the cards to ensure they are readable */
    [data-testid="stMetricLabel"] {
        color: #b4b4b4; /* Slightly lighter gray for the label text */
    }

    /* Styles for the expanding advisory cards */
    div[data-testid="stExpander"] div[role="button"] p {
        font-size: 1.1rem;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HELPER FUNCTIONS ---

def get_lat_lon(city_name):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json"
    response = requests.get(url).json()
    if not response.get("results"):
        return None, None, None
    return response["results"][0]["latitude"], response["results"][0]["longitude"], response["results"][0]["name"]

def get_weather_data(lat, lon):
    # Fetching Current Weather + Hourly Forecast + Daily Sunrise/Sunset
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,weather_code,wind_speed_10m&hourly=temperature_2m,precipitation_probability&daily=sunrise,sunset&timezone=auto"
    return requests.get(url).json()

def get_aqi_data(lat, lon):
    # Fetching Air Quality Index (European AQI)
    url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=european_aqi"
    return requests.get(url).json()

# --- 4. ADVISORY LOGIC ---

def generate_advisory(temp, apparent_temp, rain, wind, aqi, uv_index=5):
    # Outfit
    outfit = "👕 **Outfit:** "
    if rain > 0:
        outfit += "Waterproof shell required. Rain likely. "
    elif wind > 20:
        outfit += "Windbreaker recommended. "
    
    if apparent_temp < 10:
        outfit += "Heavy coat, scarf, and thermal layers."
    elif 10 <= apparent_temp < 18:
        outfit += "Sweater or hoodie with a light jacket."
    elif 18 <= apparent_temp < 25:
        outfit += "Long sleeve t-shirt or light cardigan."
    else:
        outfit += "Breathable cottons, shorts/skirts. Sunglasses."

    # Health
    health = "❤️ **Health:** "
    if aqi > 60:
        health += "Air quality is moderate/poor. Sensitive groups should wear masks. "
    elif aqi > 80:
        health += "⚠️ Poor Air Quality! Avoid outdoor cardio. "
    else:
        health += "Air is clean. Great for outdoor activities. "
    
    if apparent_temp > 32:
        health += "Stay hydrated! Heat stress risk."

    # Travel/Drive
    travel = "🚗 **Commute:** "
    if rain > 0.5:
        travel += "Roads are slippery. Increase following distance."
    elif wind > 30:
        travel += "High crosswinds. Hold the steering wheel firmly."
    else:
        travel += "Conditions are good for driving/biking."

    return outfit, health, travel

# --- 5. MAIN UI LAYOUT ---

# SIDEBAR
with st.sidebar:
    st.header("⚙️ Settings")
    city = st.text_input("📍 Enter City", "Bengaluru")
    if st.button("Update Report", type="primary"):
        st.session_state.search = True

# MAIN CONTENT
st.title("🌦️ WeatherWise AI")
st.markdown(f"### Live Lifestyle Advisory for **{city}**")

# Run logic only if city is present
if city:
    try:
        # A. Fetch Data
        lat, lon, name = get_lat_lon(city)
        
        if not lat:
            st.error("🚫 City not found. Please verify spelling.")
        else:
            w_data = get_weather_data(lat, lon)
            aqi_data = get_aqi_data(lat, lon)

            # B. Parse Data
            current = w_data["current"]
            daily = w_data["daily"]
            hourly = w_data["hourly"]
            
            temp = current["temperature_2m"]
            feels_like = current["apparent_temperature"]
            humidity = current["relative_humidity_2m"]
            wind = current["wind_speed_10m"]
            rain = current["precipitation"]
            is_day = current["is_day"]
            aqi = aqi_data["current"]["european_aqi"]
            
            # Formatting Time
            sunrise = datetime.fromisoformat(daily["sunrise"][0]).strftime("%H:%M")
            sunset = datetime.fromisoformat(daily["sunset"][0]).strftime("%H:%M")

            # C. Top Metrics Row (The "Glass" Cards)
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Temperature", f"{temp}°C", f"Feels like {feels_like}°C")
            col2.metric("Humidity", f"{humidity}%", "Dew Point 18°")
            col3.metric("Wind Speed", f"{wind} km/h", "Direction NW")
            col4.metric("Air Quality (AQI)", f"{aqi}", "Good" if aqi < 40 else "Moderate" if aqi < 80 else "Poor", delta_color="inverse")

            st.divider()

            # D. The "Smart" Advisory Section
            outfit_msg, health_msg, travel_msg = generate_advisory(temp, feels_like, rain, wind, aqi)
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.info(outfit_msg, icon="🧥")
            with c2:
                st.warning(health_msg, icon="❤️")
            with c3:
                st.success(travel_msg, icon="🚦")

            st.divider()

            # E. The "Cool" Features: Chart & Map
            col_chart, col_map = st.columns([2, 1])
            
            with col_chart:
                st.subheader("📅 24-Hour Temperature Trend")
                # Create a simple dataframe for the chart
                chart_data = pd.DataFrame({
                    "Time": [t.split("T")[1] for t in hourly["time"][:24]],
                    "Temperature (°C)": hourly["temperature_2m"][:24]
                })
                st.line_chart(chart_data.set_index("Time"))
            
            with col_map:
                st.subheader("🗺️ Location")
                st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}))
                st.caption(f"Sun Rise: {sunrise}  |  Sun Set: {sunset}")

    except Exception as e:

        st.error(f"Error fetching data: {e}")
