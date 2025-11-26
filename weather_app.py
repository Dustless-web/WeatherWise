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
        r = requests.get(url, timeout=5)
        if r.status_code != 200: return None
        return r.json()
    except: return None

# Animations (Fail-safe)
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
        margin-bottom: 20px;
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

    /* ADVISORY CARDS */
    .advice-card {
        background: rgba(0, 0, 0, 0.3);
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 5px solid;
    }

    /* CUSTOM HEADERS */
    h1, h2, h3, h4 {
        color: white !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.5);
    }
    
    /* REMOVE WHITE SPACE AT TOP */
    .block-container {
        padding-top: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. LOGIC ENGINE (DETAILED) ---
def get_weather_data(city):
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
    try:
        geo_res = requests.get(geo_url).json()
        if not geo_res.get("results"): return None, None, None, None
        
        lat, lon = geo_res["results"][0]["latitude"], geo_res["results"][0]["longitude"]
        name = geo_res["results"][0]["name"]
        
        w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,weather_code,wind_speed_10m&hourly=temperature_2m&timezone=auto"
        w_res = requests.get(w_url).json()
        return w_res, name, lat, lon
    except: return None, None, None, None

def generate_smart_advisory(temp, feels_like, humidity, rain, wind):
    # --- OUTFIT ---
    outfit = "👕 **Outfit:** "
    if rain > 0: outfit += "Waterproof shell required. Rain likely. "
    elif wind > 20: outfit += "Windbreaker recommended. "
    
    if feels_like < 10: outfit += "Heavy coat & thermal layers."
    elif 10 <= feels_like < 18: outfit += "Sweater or Hoodie."
    elif 18 <= feels_like < 25: outfit += "Long sleeve t-shirt."
    else: outfit += "Breathable cottons, shorts/skirts."

    # --- HYGIENE ---
    hygiene = "🧴 **Hygiene:** "
    dew_point = temp - ((100 - humidity) / 5)
    if humidity < 35: hygiene += "Skin is drying out. Use moisturizer."
    elif humidity > 75: hygiene += "High sweat risk. Carry wet wipes."
    elif dew_point > 20: hygiene += "Frizz alert! Use hair serum."
    else: hygiene += "Conditions are balanced."

    # --- LIFESTYLE ---
    lifestyle = "🚀 **Activity:** "
    if rain > 0.5 and wind > 30: lifestyle += "Drive slow (Hydroplaning risk)."
    elif temp > 30: lifestyle += "Stay hydrated. Heat stress risk."
    elif wind > 25: lifestyle += "Avoid outdoor cycling."
    else: lifestyle += "Great conditions for outdoor activities."
    
    return outfit, hygiene, lifestyle

# --- 5. UI LAYOUT ---

# Sidebar
with st.sidebar:
    st.header("📍 Location")
    city = st.text_input("Search City", "Toronto")
    st.markdown("---")
    st.caption("WeatherWise Pro v3.0")

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
        humidity = current["relative_humidity_2m"]
        
        # --- TITLE SECTION ---
        st.markdown("<h1 style='text-align: center; margin-bottom: 5px;'>WeatherWise Pro</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 1.2rem; margin-bottom: 30px;'>Your AI-Powered Personal Meteorologist</p>", unsafe_allow_html=True)

        # --- ANIMATION & TEMP ---
        anim = None
        if code in range(51, 68) or code in range(80, 100): anim = lottie_rain
        elif code <= 3: anim = lottie_clear
        else: anim = lottie_cloud

        c1, c2 = st.columns([1, 2])
        with c1:
            if anim: st_lottie(anim, height=200, key="weather_anim")
            else: st.markdown("<h1 style='text-align: center; font-size: 100px;'>🌤️</h1>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<h1 style='font-size: 90px; margin-bottom: 0;'>{temp}°</h1>", unsafe_allow_html=True)
            st.markdown(f"<h2>{name}</h2>", unsafe_allow_html=True)
            st.write(f"Feels like {feels}° | Wind {wind} km/h")

        st.markdown("---")

        # --- METRIC CARDS ---
        col1, col2, col3 = st.columns(3)
        def card(label, value):
            return f"""<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>"""
        
        with col1: st.markdown(card("Humidity", f"{humidity}%"), unsafe_allow_html=True)
        with col2: st.markdown(card("Wind Speed", f"{wind} km/h"), unsafe_allow_html=True)
        with col3: st.markdown(card("Precipitation", f"{rain} mm"), unsafe_allow_html=True)

        # --- DETAILED ADVICE SECTION ---
        st.subheader("🧠 AI Lifestyle Analysis")
        
        # Get detailed advice
        outfit_txt, hygiene_txt, life_txt = generate_smart_advisory(temp, feels, humidity, rain, wind)

        # Helper for Advice Cards
        def advice_html(content, color):
            return f"""
            <div class="advice-card" style="border-color: {color};">
                <p style="font-size: 1.1rem; margin: 0; color: white;">{content}</p>
            </div>
            """

        a1, a2, a3 = st.columns(3)
        with a1: st.markdown(advice_html(outfit_txt, "#00f260"), unsafe_allow_html=True) # Green
        with a2: st.markdown(advice_html(hygiene_txt, "#00d2ff"), unsafe_allow_html=True) # Blue
        with a3: st.markdown(advice_html(life_txt, "#ff007f"), unsafe_allow_html=True)   # Pink

        st.markdown("---")

        # --- MAP & CHART SECTION ---
        c_chart, c_map = st.columns([2, 1])
        
        with c_chart:
            st.subheader("📈 24h Trend")
            hourly = data["hourly"]
            chart_data = pd.DataFrame({"Temperature": hourly["temperature_2m"][:24]})
            st.line_chart(chart_data)
        
        with c_map:
            st.subheader("🗺️ Radar")
            st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}))
        
    else:
        st.error("City not found or API error.")