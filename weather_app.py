import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="WeatherWise Pro",
    page_icon="⛈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CUSTOM CSS (Dark Mode & Cards) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #fafafa; }
    
    /* Metric Cards */
    [data-testid="stMetric"] {
        background-color: #1f2937;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #374151;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    [data-testid="stMetricValue"] { color: #ffffff !important; }
    [data-testid="stMetricLabel"] { color: #9ca3af !important; }
    
    /* Advisory Cards (Styled as Containers) */
    .advisory-card {
        background-color: #1f2937;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.1);
        height: 100%;
    }
    .info { border-left: 4px solid #3b82f6; }
    .warning { border-left: 4px solid #f59e0b; }
    .success { border-left: 4px solid #10b981; }
    .purple { border-left: 4px solid #8b5cf6; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION STATE (Auth Simulation) ---
if 'user' not in st.session_state:
    st.session_state.user = None

# --- 4. API HELPERS ---
def get_lat_lon(city_name):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json"
    try:
        r = requests.get(url).json()
        if not r.get("results"): return None, None
        return r["results"][0]["latitude"], r["results"][0]["longitude"]
    except: return None, None

def get_weather_data(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,weather_code,wind_speed_10m&hourly=temperature_2m,precipitation_probability&daily=sunrise,sunset,uv_index_max&timezone=auto"
    return requests.get(url).json()

def get_aqi_data(lat, lon):
    url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=european_aqi"
    return requests.get(url).json()

# --- 5. LOGIC ENGINE ---
def generate_advisory(current, daily, aqi):
    temp = current['temperature_2m']
    feels_like = current['apparent_temperature']
    rain = current['precipitation']
    wind = current['wind_speed_10m']
    humidity = current['relative_humidity_2m']
    is_day = current['is_day']
    uv = daily['uv_index_max'][0]
    
    # A. Wardrobe
    outfit = []
    if feels_like < 5: outfit.append("❄️ **Base:** Thermal innerwear + Woolen sweater + Heavy Coat.")
    elif 5 <= feels_like < 12: outfit.append("🧥 **Base:** Puffer jacket or Heavy trench coat.")
    elif 12 <= feels_like < 18: outfit.append("🧣 **Base:** Hoodie, Cardigan, or Denim jacket.")
    elif 18 <= feels_like < 25: outfit.append("👕 **Base:** Long-sleeve t-shirt or Flannels.")
    elif 25 <= feels_like < 30: outfit.append("👚 **Base:** Breathable cotton or linen. Short sleeves.")
    else: outfit.append("🎽 **Base:** Loose-fit synthetics. Shorts/Skirts permitted.")
    
    if rain > 0.5: outfit.append("👢 **Shoes:** Waterproof boots. Avoid suede.")
    elif rain > 0: outfit.append("👟 **Shoes:** Water-resistant sneakers.")
    elif temp > 30: outfit.append("👡 **Shoes:** Open-toe sandals or mesh trainers.")
    else: outfit.append("👞 **Shoes:** Comfortable loafers or sneakers.")

    if rain > 0: outfit.append("☂️ **Gear:** Carry an umbrella/raincoat.")
    if uv > 5 and is_day: outfit.append("🕶️ **Extras:** Polarized sunglasses & Hat.")

    # B. Self Care
    hygiene = []
    if humidity < 35: hygiene.append("🧴 **Skin:** Dry air. Use oil-based moisturizer.")
    elif humidity > 75: hygiene.append("🧼 **Skin:** High humidity. Use gel-based moisturizer.")
    else: hygiene.append("✨ **Skin:** Balanced. Standard lotion is fine.")

    if uv >= 5 and is_day: hygiene.append(f"🛡️ **SPF:** High UV ({uv}). Apply SPF 30+.")
    
    dew_point = temp - ((100 - humidity) / 5)
    if dew_point > 20: hygiene.append("🦁 **Hair:** Frizz Alert! Use anti-humidity serum.")
    
    if temp > 30: hygiene.append("🥤 **Hydration:** Add electrolytes to water.")
    else: hygiene.append("💧 **Hydration:** Drink 2.5L water today.")

    # C. Lifestyle
    lifestyle = []
    if aqi < 50 and rain == 0: lifestyle.append("🏃 **Exercise:** Perfect for outdoor run.")
    elif rain > 0: lifestyle.append("🧘 **Exercise:** Rainy. Try indoor Yoga.")
    elif aqi >= 100: lifestyle.append("😷 **Health:** Poor Air Quality. Wear mask outdoors.")
    else: lifestyle.append("💪 **Exercise:** Gym session or light jog.")

    if temp > 32: lifestyle.append("🥗 **Diet:** Eat cooling foods (cucumber, melons).")
    elif temp < 15: lifestyle.append("🍲 **Diet:** Hearty soups recommended.")

    # D. Routine
    routine = []
    # Morning
    if rain > 0: routine.append("07:00 AM - 🧘 Indoor Yoga (Rainy Start)")
    elif aqi < 50: routine.append("07:00 AM - 🏃 Morning Run (Clean Air)")
    else: routine.append("07:00 AM - 🏋️ Gym Workout")
    
    # Commute
    if rain > 0.5: routine.append("08:30 AM - 🚗 Leave 20m early (Traffic Risk)")
    else: routine.append("08:45 AM - 🚇 Regular Commute")
    
    # Lunch
    if temp > 30: routine.append("01:00 PM - 🥗 Light Salad Lunch")
    elif temp < 15: routine.append("01:00 PM - 🍜 Hot Soup & Sandwich")
    else: routine.append("01:00 PM - 🍱 Balanced Meal")
    
    # Evening
    if rain == 0 and 15 < temp < 27: routine.append("06:30 PM - 🚶 Evening Walk / Park")
    else: routine.append("06:30 PM - 📖 Indoor Reading / Relaxation")

    return outfit, hygiene, lifestyle, routine

# --- 6. AUTH SCREEN ---
def login_screen():
    st.markdown("<h1 style='text-align: center; color: #60a5fa;'>WeatherWise Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #9ca3af;'>Sign in to access daily routine AI</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.form("login_form"):
            name = st.text_input("Full Name", placeholder="John Doe")
            email = st.text_input("Email", placeholder="name@example.com")
            submitted = st.form_submit_button("Sign In", type="primary", use_container_width=True)
            
            if submitted and name:
                st.session_state.user = {'name': name, 'email': email}
                st.rerun()

# --- 7. MAIN DASHBOARD ---
def dashboard():
    # Header
    c1, c2 = st.columns([3, 1])
    with c1:
        st.title("WeatherWise Pro")
        st.caption(f"Welcome back, {st.session_state.user['name']}")
    with c2:
        if st.button("Sign Out"):
            st.session_state.user = None
            st.rerun()

    # Search
    city = st.text_input("📍 Search City", "Bengaluru")
    
    if city:
        try:
            lat, lon = get_lat_lon(city)
            if not lat:
                st.error("City not found.")
                return

            w_data = get_weather_data(lat, lon)
            a_data = get_aqi_data(lat, lon)
            
            curr = w_data['current']
            daily = w_data['daily']
            hourly = w_data['hourly']
            aqi = a_data['current']['european_aqi']
            
            # Metric Cards
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Temperature", f"{curr['temperature_2m']}°C", f"Feels {curr['apparent_temperature']}°C")
            m1.caption("🌡️ Thermal Comfort")
            
            m2.metric("Humidity", f"{curr['relative_humidity_2m']}%", "Dew Point Check")
            m2.caption("💧 Moisture Levels")
            
            m3.metric("Wind", f"{curr['wind_speed_10m']} km/h", f"Rain: {curr['precipitation']}mm")
            m3.caption("🌬️ Breeze & Precip")
            
            aqi_label = "Good" if aqi < 40 else "Moderate" if aqi < 80 else "Poor"
            m4.metric("Air Quality", aqi, aqi_label)
            m4.caption("🌿 European AQI")

            st.markdown("---")

            # Smart Advisory Grid
            outfit, hygiene, lifestyle, routine = generate_advisory(curr, daily, aqi)
            
            c1, c2, c3, c4 = st.columns(4)
            
            with c1:
                st.markdown('<div class="advisory-card info"><h4>🧥 Wardrobe</h4>', unsafe_allow_html=True)
                for item in outfit: st.markdown(f"- {item}")
                st.markdown('</div>', unsafe_allow_html=True)
                
            with c2:
                st.markdown('<div class="advisory-card warning"><h4>✨ Self Care</h4>', unsafe_allow_html=True)
                for item in hygiene: st.markdown(f"- {item}")
                st.markdown('</div>', unsafe_allow_html=True)

            with c3:
                st.markdown('<div class="advisory-card success"><h4>🥗 Lifestyle</h4>', unsafe_allow_html=True)
                for item in lifestyle: st.markdown(f"- {item}")
                st.markdown('</div>', unsafe_allow_html=True)

            with c4:
                st.markdown('<div class="advisory-card purple"><h4>⏰ Routine</h4>', unsafe_allow_html=True)
                for item in routine: st.markdown(f"- {item}")
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("---")

            # Charts and Map
            g1, g2 = st.columns([2, 1])
            with g1:
                st.subheader("24-Hour Forecast")
                chart_data = pd.DataFrame({
                    "Time": [t.split("T")[1] for t in hourly["time"][:24]],
                    "Temp (°C)": hourly["temperature_2m"][:24]
                })
                st.line_chart(chart_data.set_index("Time"))
            
            with g2:
                st.subheader("Location")
                st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}))
                st.caption(f"Sunrise: {daily['sunrise'][0].split('T')[1]} | Sunset: {daily['sunset'][0].split('T')[1]}")

        except Exception as e:
            st.error(f"Error: {e}")

# --- 8. APP ROUTING ---
if st.session_state.user:
    dashboard()
else:
    login_screen()