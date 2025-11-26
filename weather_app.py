import streamlit as st
import requests
import pandas as pd
from streamlit_lottie import st_lottie
from datetime import datetime

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="WeatherWise Pro", page_icon="⚡", layout="wide")

# --- 2. ASSETS & ANIMATIONS ---
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Load Lottie Animations (Free assets from LottieFiles)
lottie_clear = load_lottieurl("https://assets9.lottiefiles.com/private_files/lf30_jmgebfxz.json")
lottie_rain = load_lottieurl("https://assets9.lottiefiles.com/packages/lf20_b88nh30c.json")
lottie_cloud = load_lottieurl("https://assets9.lottiefiles.com/packages/lf20_kxsd2ytq.json")

# --- 3. ULTRA-MODERN CSS (The "Flashy" Part) ---
st.markdown("""
    <style>
    /* ANIMATED BACKGROUND */
    .stApp {
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }
    
    @keyframes gradient {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }

    /* GLASSMORPHISM CARDS */
    div.css-1r6slb0.e1tzin5v2 {
        background-color: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        color: white;
    }

    /* CUSTOM METRIC BOXES */
    .metric-card {
        background: rgba(0, 0, 0, 0.5);
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #ffffff;
    }
    .metric-label {
        font-size: 1rem;
        color: #d1d1d1;
    }

    /* TEXT GLOW */
    h1 {
        text-shadow: 0 0 10px rgba(255,255,255,0.6);
        color: white !important;
    }
    p, label {
        color: white !important;
    }
    
    /* SIDEBAR STYLE */
    section[data-testid="stSidebar"] {
        background-color: rgba(0,0,0,0.8);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. LOGIC ENGINE (Keep the Smart Logic) ---
def get_weather_data(city):
    # Geocoding
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
    geo_res = requests.get(geo_url).json()
    if not geo_res.get("results"): return None
    
    lat, lon = geo_res["results"][0]["latitude"], geo_res["results"][0]["longitude"]
    name = geo_res["results"][0]["name"]
    
    # Weather
    w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,weather_code,wind_speed_10m&hourly=temperature_2m&daily=sunrise,sunset&timezone=auto"
    w_res = requests.get(w_url).json()
    
    return w_res, name, lat, lon

def generate_advice(temp, rain, wind):
    # Simplified Logic for visual focus
    advice = "✨ Enjoy the day!"
    if rain > 0: advice = "🌧️ Rainy vibes. Grab a trench coat and waterproof boots."
    elif temp < 15: advice = "❄️ It's chilly! Layer up with a hoodie and thermal jacket."
    elif temp > 28: advice = "☀️ Heatwave alert. Linen shirts and hydration check."
    return advice

# --- 5. UI LAYOUT ---

# Sidebar
with st.sidebar:
    st.header("📍 Location")
    city = st.text_input("Search City", "New York")
    st.markdown("---")
    st.write("Designed with ❤️ using Streamlit Lottie")

# Main Page
if city:
    data, name, lat, lon = get_weather_data(city)
    
    if data:
        current = data["current"]
        temp = current["temperature_2m"]
        feels = current["apparent_temperature"]
        rain = current["precipitation"]
        wind = current["wind_speed_10m"]
        code = current["weather_code"]
        
        # Determine Animation
        if code in range(51, 68) or code in range(80, 100):
            anim = lottie_rain
        elif code <= 3:
            anim = lottie_clear
        else:
            anim = lottie_cloud

        # --- HEADER SECTION ---
        c1, c2 = st.columns([1, 2])
        with c1:
            st_lottie(anim, height=200, key="weather_anim")
        with c2:
            st.markdown(f"<h1 style='font-size: 70px; margin-bottom: 0;'>{temp}°</h1>", unsafe_allow_html=True)
            st.markdown(f"<h2>{name}</h2>", unsafe_allow_html=True)
            st.write(f"Feels like {feels}° | Wind {wind} km/h")

        st.markdown("---")

        # --- CUSTOM METRIC CARDS ---
        col1, col2, col3 = st.columns(3)
        
        # Helper to create HTML card
        def card(label, value):
            return f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
            </div>
            """
            
        with col1:
            st.markdown(card("Humidity", f"{current['relative_humidity_2m']}%"), unsafe_allow_html=True)
        with col2:
            st.markdown(card("Wind Speed", f"{wind} km/h"), unsafe_allow_html=True)
        with col3:
            st.markdown(card("Rain Volume", f"{rain} mm"), unsafe_allow_html=True)

        st.markdown("---")

        # --- ADVISORY BANNER ---
        advice = generate_advice(temp, rain, wind)
        st.markdown(f"""
        <div style="background: rgba(0,0,0,0.6); border-left: 5px solid #00f260; padding: 20px; border-radius: 10px;">
            <h3 style="color: #00f260; margin:0;">🤖 AI Style & Lifestyle</h3>
            <p style="font-size: 1.2rem; margin-top: 10px;">{advice}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # --- CHART ---
        st.markdown("### 📈 24h Trend")
        hourly = data["hourly"]
        chart_data = pd.DataFrame({"Temp": hourly["temperature_2m"][:24]})
        st.line_chart(chart_data)
        
    else:
        st.error("City not found!")