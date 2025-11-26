import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="WeatherWise Pro",
    page_icon="⛈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CUSTOM CSS (Dark Mode Optimization) ---
st.markdown("""
    <style>
    /* 1. Main Background and Text Color fixes */
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    
    /* 2. Style the Metric Cards (Temperature, Humidity blocks) */
    [data-testid="stMetric"] {
        background-color: #262730; /* Dark Charcoal background */
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #3b3c40;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.5);
    }
    
    /* 3. Force the big numbers to be White */
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
    }
    
    /* 4. Make the small labels (e.g. "Humidity") Light Gray */
    [data-testid="stMetricLabel"] {
        color: #b0b0b0 !important;
    }

    /* 5. Style the Advisory Expanders */
    div[data-testid="stExpander"] div[role="button"] p {
        font-size: 1.1rem;
        font-weight: 600;
        color: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HELPER FUNCTIONS (API Calls) ---

def get_lat_lon(city_name):
    # Geocoding API
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json"
    try:
        response = requests.get(url).json()
        if not response.get("results"):
            return None, None, None
        result = response["results"][0]
        return result["latitude"], result["longitude"], result["name"]
    except:
        return None, None, None

def get_weather_data(lat, lon):
    # Weather API (Current + Hourly + Daily)
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,weather_code,wind_speed_10m&hourly=temperature_2m,precipitation_probability&daily=sunrise,sunset,uv_index_max&timezone=auto"
    return requests.get(url).json()

def get_aqi_data(lat, lon):
    # Air Quality API
    url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=european_aqi"
    return requests.get(url).json()

# --- 4. SMART LOGIC ENGINE ---

def generate_smart_advisory(temp, feels_like, humidity, rain, wind, aqi, uv_index, is_day):
    # --- A. OUTFIT LOGIC ---
    outfit = []
    
    # Base Layer (Thermal Comfort)
    if feels_like < 5:
        outfit.append("❄️ **Base:** Thermal innerwear + Woolen sweater + Heavy Coat.")
    elif 5 <= feels_like < 12:
        outfit.append("🧥 **Base:** Puffer jacket or Heavy trench coat.")
    elif 12 <= feels_like < 18:
        outfit.append("🧣 **Base:** Hoodie, Cardigan, or Denim jacket.")
    elif 18 <= feels_like < 25:
        outfit.append("👕 **Base:** Long-sleeve t-shirt or Flannels.")
    elif 25 <= feels_like < 30:
        outfit.append("👚 **Base:** Breathable cotton or linen. Short sleeves.")
    else:
        outfit.append("🎽 **Base:** Loose-fit synthetics. Shorts/Skirts permitted.")

    # Wind & Rain
    if rain > 0.0:
        if wind > 20:
            outfit.append("🚫 **Warning:** Wind is too strong for umbrellas! Use a raincoat.")
        else:
            outfit.append("☂️ **Gear:** Carry a sturdy umbrella and waterproof shoes.")
    
    # Accessories
    if uv_index > 5 and is_day:
        outfit.append("🕶️ **Extras:** High UV detected. Polarized sunglasses & Hat required.")
    
    if wind > 25 and feels_like < 15:
        outfit.append("🧤 **Extras:** Wear gloves. Pockets won't be enough.")

    # --- B. SELF CARE (Hygiene/Beauty) ---
    hygiene = []
    
    # Skin & Lips
    if humidity < 35:
        hygiene.append("🧴 **Skin:** Low humidity. Use oil-based moisturizer & lip balm.")
    elif humidity > 75:
        hygiene.append("🧼 **Skin:** High humidity. Carry blotting paper or wet wipes.")
    
    # Hair (Frizz Index)
    dew_point = temp - ((100 - humidity) / 5)
    if dew_point > 20:
        hygiene.append("🦁 **Hair:** Severe Frizz Alert! Use anti-humidity serum/spray.")
    
    # Scent
    if temp > 28:
        hygiene.append("🌬️ **Freshness:** Deodorant is mandatory today. Light perfumes only.")

    # --- C. LIFESTYLE & SAFETY ---
    lifestyle = []
    
    # Air Quality
    if aqi < 40:
        lifestyle.append("🏃 **Exercise:** Air is clean. Great for outdoor runs.")
    elif 40 <= aqi < 80:
        lifestyle.append("😐 **Exercise:** Air is moderate. Sensitive groups should take it easy.")
    elif aqi >= 80:
        lifestyle.append("😷 **Health:** Air is poor. Wear a mask outdoors. Keep windows closed.")

    # Commute
    if rain > 0.5 and wind > 30:
        lifestyle.append("⚠️ **Drive:** Hydroplaning risk! Drive 10km/h below limit.")
    elif is_day == 0 and rain > 0:
        lifestyle.append("🔦 **Walk:** Low visibility. Wear reflective clothing.")
        
    # Hydration
    if feels_like > 32:
        lifestyle.append("💧 **Health:** Heat stress risk. Drink at least 3L of water.")

    return "\n\n".join(outfit), "\n\n".join(hygiene), "\n\n".join(lifestyle)

# --- 5. MAIN UI LAYOUT ---

# Sidebar Input
with st.sidebar:
    st.header("⚙️ Settings")
    city_input = st.text_input("📍 Enter City Name", "Chennai")
    if st.button("Update Report", type="primary"):
        st.session_state.search = True
    
    st.markdown("---")
    st.caption("v2.0 | Built with Streamlit & Open-Meteo")

# Main Content
st.title("🌦️ WeatherWise AI")
st.markdown(f"### Live Lifestyle Advisory for **{city_input.title()}**")

if city_input:
    try:
        # 1. Fetch Lat/Lon
        lat, lon, name = get_lat_lon(city_input)
        
        if not lat:
            st.error(f"🚫 Could not find city: '{city_input}'. Please check spelling.")
        else:
            # 2. Fetch Weather & AQI
            w_data = get_weather_data(lat, lon)
            aqi_data = get_aqi_data(lat, lon)

            # 3. Parse Data
            current = w_data["current"]
            daily = w_data["daily"]
            hourly = w_data["hourly"]
            
            temp = current["temperature_2m"]
            feels_like = current["apparent_temperature"]
            humidity = current["relative_humidity_2m"]
            wind = current["wind_speed_10m"]
            rain = current["precipitation"]
            is_day = current["is_day"]
            w_code = current["weather_code"]
            
            # AQI and UV
            aqi = aqi_data["current"]["european_aqi"]
            uv_max_today = daily["uv_index_max"][0]
            
            # Sunrise/Sunset for UI
            sunrise = datetime.fromisoformat(daily["sunrise"][0]).strftime("%H:%M")
            sunset = datetime.fromisoformat(daily["sunset"][0]).strftime("%H:%M")

            # 4. Top Metrics Row (The Glass Cards)
            col1, col2, col3, col4 = st.columns(4)
            
            col1.metric("Temperature", f"{temp}°C", f"Feels like {feels_like}°C")
            col2.metric("Humidity", f"{humidity}%", "Dew Point Check")
            col3.metric("Wind Speed", f"{wind} km/h", f"Precip: {rain}mm")
            
            # Dynamic AQI Color logic
            aqi_label = "Good" if aqi < 40 else "Moderate" if aqi < 80 else "Poor"
            col4.metric("Air Quality (AQI)", f"{aqi}", aqi_label, delta_color="inverse")

            st.divider()

            # 5. Smart Advisory Section
            outfit_msg, hygiene_msg, lifestyle_msg = generate_smart_advisory(
                temp, feels_like, humidity, rain, wind, aqi, uv_max_today, is_day
            )
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.info(f"**Wardrobe**\n\n{outfit_msg}", icon="🧥")
            with c2:
                st.warning(f"**Self Care**\n\n{hygiene_msg}", icon="✨")
            with c3:
                st.success(f"**Lifestyle**\n\n{lifestyle_msg}", icon="🌿")

            st.divider()

            # 6. Charts & Map Section
            col_chart, col_map = st.columns([2, 1])
            
            with col_chart:
                st.subheader("📅 24-Hour Temperature Trend")
                # Prepare data for chart
                chart_data = pd.DataFrame({
                    "Time": [t.split("T")[1] for t in hourly["time"][:24]],
                    "Temperature (°C)": hourly["temperature_2m"][:24],
                    "Rain Chance (%)": hourly["precipitation_probability"][:24]
                })
                st.line_chart(chart_data.set_index("Time")["Temperature (°C)"], color="#FF4B4B")
            
            with col_map:
                st.subheader("🗺️ Location")
                st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}))
                st.caption(f"☀️ Rise: {sunrise}  |  🌙 Set: {sunset}")

    except Exception as e:
        st.error(f"An error occurred: {e}")