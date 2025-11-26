import streamlit as st
import requests
import pandas as pd
from streamlit_lottie import st_lottie
from datetime import datetime

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="WeatherWise Pro", page_icon="⚡", layout="wide")

# --- 2. ASSETS & ANIMATIONS ---
def load_lottieurl(url):
    try:
        r = requests.get(url, timeout=5) # Added timeout to prevent hanging
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Load Lottie Animations (More reliable links)
# If these fail, the app will now safe-fail to an emoji instead of crashing
lottie_clear = load_lottieurl("https://lottie.host/5a91595d-d965-442b-a5ce-4af2438883cc/1z7K7qJ1sF.json") 
lottie_rain = load_lottieurl("https://lottie.host/0a112702-6029-451e-84b2-243179267a57/H0852e697H.json") 
lottie_cloud = load_lottieurl("https://lottie.host/0e611d27-2483-4700-b6f1-a1b635483259/3a2y0o2a3d.json")

# --- 3. ULTRA-MODERN CSS ---
st.markdown("""
    <style>
    /* ANIMATED BACKGROUND */
    .stApp {
        background: linear-gradient(-45deg, #1e3c72, #2a5298, #23d5ab, #23a6d5);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        color: white;
    }
    
    @keyframes gradient {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }

    /* GLASSMORPHISM CARDS */
    .metric-card {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(5px);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #ffffff;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #e0e0e0;
    }

    /* CUSTOM HEADERS */
    h1, h2, h3 {
        color: white !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.5);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. LOGIC ENGINE ---
def get_weather_data(city):
    # Geocoding
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
    try:
        geo_res = requests.get(geo_url).json()
        if not geo_res.get("results"): return None, None, None, None
        
        lat, lon = geo_res["results"][0]["latitude"], geo_res["results"][0]["longitude"]
        name = geo_res["results"][0]["name"]
        
        # Weather
        w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,weather_code,wind_speed_10m&hourly=temperature_2m&timezone=auto"
        w_res = requests.get(w_url).json()
        return w_res, name, lat, lon
    except:
        return None, None, None, None

def generate_advice(temp, rain):
    if rain > 0: return "🌧️ Rainy vibes. Grab a trench coat and waterproof boots."
    elif temp < 15: return "❄️ It's chilly! Layer up with a hoodie and thermal jacket."
    elif temp > 28: return "☀️ Heatwave alert. Linen shirts and hydration check."
    return "✨ Enjoy the day! Conditions are stable."

# --- 5. UI LAYOUT ---

# Sidebar
with st.sidebar:
    st.header("📍 Location")
    city = st.text_input("Search City", "New York")
    st.markdown("---")
    st.caption("WeatherWise Pro v2.1")

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
        anim = None
        if code in range(51, 68) or code in range(80, 100):
            anim = lottie_rain
        elif code <= 3:
            anim = lottie_clear
        else:
            anim = lottie_cloud

        # --- HEADER SECTION ---
        c1, c2 = st.columns([1, 2])
        
        with c1:
            # --- CRASH FIX: SAFETY CHECK ---
            if anim:
                st_lottie(anim, height=200, key="weather_anim")
            else:
                # If animation fails, show a big emoji instead
                st.markdown("<h1 style='text-align: center; font-size: 100px;'>🌤️</h1>", unsafe_allow_html=True)
                
        with c2:
            st.markdown(f"<h1 style='font-size: 80px; margin-bottom: 0;'>{temp}°</h1>", unsafe_allow_html=True)
            st.markdown(f"<h2>{name}</h2>", unsafe_allow_html=True)
            st.write(f"Feels like {feels}° | Wind {wind} km/h")

        st.markdown("---")

        # --- CUSTOM METRIC CARDS ---
        col1, col2, col3 = st.columns(3)
        
        def card(label, value):
            return f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
            </div>
            """
            
        with col1: st.markdown(card("Humidity", f"{current['relative_humidity_2m']}%"), unsafe_allow_html=True)
        with col2: st.markdown(card("Wind Speed", f"{wind} km/h"), unsafe_allow_html=True)
        with col3: st.markdown(card("Precipitation", f"{rain} mm"), unsafe_allow_html=True)

        st.markdown("---")

        # --- ADVISORY BANNER ---
        st.markdown(f"""
        <div style="background: rgba(0,0,0,0.5); border-left: 6px solid #00f260; padding: 20px; border-radius: 10px;">
            <h3 style="color: #00f260; margin:0;">🤖 AI Lifestyle Advice</h3>
            <p style="font-size: 1.2rem; margin-top: 10px; color: white;">{generate_advice(temp, rain)}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # --- CHART ---
        st.markdown("### 📈 24h Temperature Trend")
        hourly = data["hourly"]
        chart_data = pd.DataFrame({"Temperature": hourly["temperature_2m"][:24]})
        st.line_chart(chart_data)
        
    else:
        st.error("City not found or API error.")