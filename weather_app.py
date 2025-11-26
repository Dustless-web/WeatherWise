import streamlit as st
import requests
import pandas as pd
from streamlit_lottie import st_lottie
from datetime import datetime

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="WeatherWise Pro", page_icon="🌤️", layout="wide")

# --- 2. ASSETS & ANIMATIONS ---
def load_lottieurl(url):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200: return None
        return r.json()
    except: return None

# Reliable Animations
lottie_clear = load_lottieurl("https://lottie.host/5a91595d-d965-442b-a5ce-4af2438883cc/1z7K7qJ1sF.json") 
lottie_rain = load_lottieurl("https://lottie.host/0a112702-6029-451e-84b2-243179267a57/H0852e697H.json") 
lottie_cloud = load_lottieurl("https://lottie.host/0e611d27-2483-4700-b6f1-a1b635483259/3a2y0o2a3d.json")

# --- 3. PROFESSIONAL CSS STYLING ---
st.markdown("""
    <style>
    /* MAIN BACKGROUND */
    .stApp {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
    }
    
    /* REMOVE STREAMLIT PADDING & ANCHORS */
    .block-container { padding-top: 2rem; }
    a.anchor-link { display: none; }
    [data-testid="stHeader"] { display: none; }

    /* GLASSMORPHISM HERO CARD (Top Section) */
    .hero-card {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
        text-align: center;
    }

    /* METRIC CARDS (Small) */
    .metric-card {
        background: rgba(0, 0, 0, 0.3);
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.05);
    }
    .metric-value { font-size: 1.8rem; font-weight: bold; color: white; }
    .metric-label { font-size: 0.9rem; color: #a0a0a0; margin-bottom: 5px; }

    /* ADVICE CARDS (Colored Borders) */
    .advice-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 20px;
        height: 100%;
        border-left: 5px solid;
    }
    .advice-title { font-size: 1.1rem; font-weight: bold; margin-bottom: 10px; color: white; }
    .advice-text { font-size: 0.95rem; color: #e0e0e0; line-height: 1.5; }

    </style>
    """, unsafe_allow_html=True)

# --- 4. DATA LOGIC ---
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
    # OUTFIT
    outfit = ""
    if rain > 0: outfit += "☔ Waterproof shell essential. "
    if feels_like < 15: outfit += "🧥 Wear a heavy coat and thermal layers."
    elif feels_like < 22: outfit += "🧣 A light hoodie or windbreaker is perfect."
    else: outfit += "👕 Breathable cottons; stay cool."
    if wind > 20: outfit += " 💨 Avoid hats or loose scarves."

    # HYGIENE
    hygiene = ""
    dew_point = temp - ((100 - humidity) / 5)
    if humidity < 35: hygiene += "🧴 Skin is dry: Use moisturizer."
    elif humidity > 70: hygiene += "🚿 High humidity: Carry wet wipes."
    elif dew_point > 20: hygiene += "🦁 Frizz Alert: Use hair serum."
    else: hygiene += "✨ Conditions are balanced."

    # LIFESTYLE
    lifestyle = ""
    if rain > 0.5: lifestyle += "🚗 Drive slow (Hydroplaning risk)."
    elif temp > 30: lifestyle += "💧 Heat stress risk: Drink water."
    else: lifestyle += "🏃 Perfect weather for outdoor cardio."
    
    return outfit, hygiene, lifestyle

# --- 5. UI STRUCTURE ---

# Sidebar
with st.sidebar:
    st.markdown("### 📍 Location")
    city_input = st.text_input("City Name", "Bengaluru", label_visibility="collapsed")
    st.markdown("---")
    st.caption("WeatherWise Pro v3.0")

# Main Logic
if city_input:
    data, name, lat, lon = get_weather_data(city_input)
    
    if data:
        current = data["current"]
        temp = current["temperature_2m"]
        feels = current["apparent_temperature"]
        rain = current["precipitation"]
        wind = current["wind_speed_10m"]
        code = current["weather_code"]
        humidity = current["relative_humidity_2m"]

        # --- A. HERO SECTION (The Big Card) ---
        # We use a container to group the top info
        with st.container():
            c1, c2 = st.columns([1, 2])
            
            # Animation Logic
            anim = lottie_cloud
            if code in range(51, 100): anim = lottie_rain
            elif code <= 3: anim = lottie_clear
            
            with c1:
                if anim: st_lottie(anim, height=180, key="hero_anim")
                else: st.markdown("# 🌤️")
            
            with c2:
                # Using custom HTML for perfect alignment
                st.markdown(f"""
                <div style="text-align: left; padding-top: 20px;">
                    <h1 style="font-size: 60px; margin: 0; color: white;">{temp}°</h1>
                    <h2 style="font-size: 30px; margin: 0; color: #e0e0e0;">{name}</h2>
                    <p style="font-size: 16px; color: #a0a0a0;">Feels like {feels}° | Wind {wind} km/h</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")

        # --- B. METRICS ROW ---
        m1, m2, m3 = st.columns(3)
        def metric_html(label, value, icon):
            return f"""
            <div class="metric-card">
                <div class="metric-label">{icon} {label}</div>
                <div class="metric-value">{value}</div>
            </div>
            """
        
        with m1: st.markdown(metric_html("Humidity", f"{humidity}%", "💧"), unsafe_allow_html=True)
        with m2: st.markdown(metric_html("Wind", f"{wind} km/h", "💨"), unsafe_allow_html=True)
        with m3: st.markdown(metric_html("Precipitation", f"{rain} mm", "🌧️"), unsafe_allow_html=True)

        st.markdown("### ") # Spacer

        # --- C. AI ADVISORY SECTION ---
        st.markdown("### 🧠 AI Lifestyle Analysis")
        outfit_txt, hygiene_txt, life_txt = generate_smart_advisory(temp, feels, humidity, rain, wind)
        
        a1, a2, a3 = st.columns(3)
        
        def advice_html(title, text, color, icon):
            return f"""
            <div class="advice-card" style="border-color: {color};">
                <div class="advice-title">{icon} {title}</div>
                <div class="advice-text">{text}</div>
            </div>
            """

        with a1: st.markdown(advice_html("Wardrobe", outfit_txt, "#00f260", "🧥"), unsafe_allow_html=True)
        with a2: st.markdown(advice_html("Hygiene", hygiene_txt, "#00d2ff", "🧴"), unsafe_allow_html=True)
        with a3: st.markdown(advice_html("Lifestyle", life_txt, "#ff007f", "🚀"), unsafe_allow_html=True)

        st.markdown("---")

        # --- D. VISUALS (Chart & Map) ---
        v1, v2 = st.columns([2, 1])
        
        with v1:
            st.markdown("#### 📅 24h Trend")
            hourly = data["hourly"]
            chart_df = pd.DataFrame({"Temperature": hourly["temperature_2m"][:24]})
            st.line_chart(chart_df, color="#ff4b4b", height=250)
            
        with v2:
            st.markdown("#### 📍 Radar")
            st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}), zoom=10, use_container_width=True)

    else:
        st.error("City not found!")