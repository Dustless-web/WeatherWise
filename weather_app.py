import streamlit as st
import requests
import pandas as pd
from datetime import datetime
try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# Page config
st.set_page_config(
    page_title="WeatherWise Pro",
    page_icon="🌧️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main, .stApp {
        background-color: #0e1117;
        color: #ffffff !important;
    }

    html, body, [class*="css"] {
        color: #ffffff !important;
    }

    h1, h2, h3, h4, h5, h6, p, span, div {
        color: #ffffff !important;
    }

    /* Metric Values */
    div[data-testid="stMetricValue"] {
        font-size: 30px;
        font-weight: bold;
        color: #ffffff !important;
    }

    div[data-testid="stMetricLabel"] {
        font-size: 14px;
        text-transform: uppercase;
        font-weight: bold;
        color: #d1d5db !important;
    }

    /* Input boxes */
    .stTextInput input {
        background-color: #1f2937;
        color: #ffffff !important;
        border: 1px solid #4b5563;
        border-radius: 8px;
    }

    /* Buttons */
    .stButton button {
        background-color: #374151;
        color: #ffffff !important;
        border: 1px solid #4b5563;
        border-radius: 8px;
        font-size: 15px;
    }
    .stButton button:hover {
        background-color: #4b5563;
        border-color: #6b7280;
    }

    /* Advisory Cards */
    .advisory-card {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# API Helper Functions
@st.cache_data(ttl=3600)
def get_lat_lon(city_name):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get('results'):
            return data['results'][0]
        return None
    except Exception as e:
        st.error(f"Geocoding error: {e}")
        return None

@st.cache_data(ttl=1800)
def get_weather_data(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,weather_code,wind_speed_10m&hourly=temperature_2m,precipitation_probability&daily=sunrise,sunset,uv_index_max&timezone=auto"
    response = requests.get(url, timeout=10)
    return response.json()

@st.cache_data(ttl=1800)
def get_aqi_data(lat, lon):
    url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=european_aqi"
    response = requests.get(url, timeout=10)
    return response.json()

# Advisory Generation Logic
def generate_smart_advisory(current, daily, aqi):
    temp = current['temperature_2m']
    feels_like = current['apparent_temperature']
    humidity = current['relative_humidity_2m']
    wind = current['wind_speed_10m']
    rain = current['precipitation']
    is_day = current['is_day']
    uv_index = daily['uv_index_max'][0]
    weather_code = current['weather_code']
    
    outfit = []
    hygiene = []
    lifestyle = []
    routine = []
    
    # WARDROBE LOGIC
    if feels_like < 5:
        outfit.append("❄️ Base: Thermal innerwear + Woolen sweater + Heavy Coat.")
    elif feels_like < 12:
        outfit.append("🧥 Base: Puffer jacket or Heavy trench coat.")
    elif feels_like < 18:
        outfit.append("🧣 Base: Hoodie, Cardigan, or Denim jacket.")
    elif feels_like < 25:
        outfit.append("👕 Base: Long-sleeve t-shirt or Flannels.")
    elif feels_like < 30:
        outfit.append("👚 Base: Breathable cotton or linen. Short sleeves.")
    else:
        outfit.append("🎽 Base: Loose-fit synthetics. Shorts/Skirts permitted.")
    
    # Footwear
    if rain > 0.5:
        outfit.append("👢 Shoes: Waterproof boots or gumboots. Avoid suede.")
    elif rain > 0:
        outfit.append("👟 Shoes: Water-resistant leather sneakers. No canvas.")
    elif temp > 30:
        outfit.append("👡 Shoes: Open-toe sandals or breathable mesh trainers.")
    elif feels_like < 10:
        outfit.append("🧦 Shoes: Insulated boots with thick wool socks.")
    else:
        outfit.append("👞 Shoes: Comfortable loafers or casual sneakers.")
    
    # Fabrics & Colors
    if temp > 28 and is_day:
        outfit.append("🎨 Style: Wear light colors (white/beige) to reflect heat.")
        outfit.append("🧵 Fabric: Opt for 100% Linen or Cotton.")
    elif feels_like < 15:
        outfit.append("🎨 Style: Dark colors absorb heat better today.")
        outfit.append("🧵 Fabric: Fleece, Wool, or Cashmere blends.")
    else:
        outfit.append("🎨 Style: Any color works today.")
        outfit.append("🧵 Fabric: Comfortable cotton blends or light layers.")
    
    # Accessories
    accessories_added = False
    if rain > 0.0:
        if wind > 20:
            outfit.append("🚫 Warning: Wind is too strong for umbrellas! Use a raincoat.")
        else:
            outfit.append("☂️ Gear: Carry a sturdy umbrella.")
        accessories_added = True
    if uv_index > 5 and is_day:
        outfit.append("🕶️ Extras: Polarized sunglasses & wide-brim hat required.")
        accessories_added = True
    if not accessories_added:
        outfit.append("🎒 Extras: A standard backpack or handbag is sufficient.")
    
    # SELF CARE
    if humidity < 35:
        hygiene.append("🧴 Skin: Dry air alert. Use oil-based moisturizer & lip balm.")
    elif humidity > 75:
        hygiene.append("🧼 Skin: High humidity. Use gel-based moisturizer. Carry blotting paper.")
    else:
        hygiene.append("✨ Skin: Balanced humidity. Standard lotion is fine.")
    
    # Sun Protection
    if uv_index >= 8 and is_day:
        hygiene.append("🛡️ SPF: Extreme UV. Apply SPF 50+ every 2 hours.")
    elif uv_index >= 5 and is_day:
        hygiene.append("🛡️ SPF: High UV. Apply SPF 30+ before stepping out.")
    elif is_day:
        hygiene.append("🛡️ SPF: Low UV. Daily SPF 15 moisturizer is sufficient.")
    else:
        hygiene.append("🌙 Care: No UV concern. Focus on night-time skincare routine.")
    
    # Hair & Eyes
    dew_point = temp - ((100 - humidity) / 5)
    hair_eye_added = False
    if dew_point > 20:
        hygiene.append("🦁 Hair: Severe Frizz Alert! Use anti-humidity serum.")
        hair_eye_added = True
    if wind > 20 and is_day:
        hygiene.append("👁️ Eyes: Windy & bright. Wear sunglasses to prevent dry eyes.")
        hair_eye_added = True
    if not hair_eye_added:
        hygiene.append("👀 Eyes & Hair: Conditions are mild. Standard care applies.")
    
    # Hydration
    if temp > 30:
        hygiene.append("🥤 Hydration: Add electrolytes to your water today.")
    elif temp < 15:
        hygiene.append("🍵 Hydration: Warm herbal teas will keep you hydrated.")
    else:
        hygiene.append("💧 Hydration: Maintain distinct daily water intake (approx 2.5L).")
    
    # LIFESTYLE
    if aqi < 50 and rain == 0:
        lifestyle.append("🏃 Exercise: Perfect conditions for an outdoor run.")
    elif rain > 0:
        lifestyle.append("🧘 Exercise: Rainy day. Try Yoga or Calisthenics indoors.")
    elif aqi >= 100:
        lifestyle.append("😷 Health: Air is poor. Gym workout only. Wear mask outdoors.")
    else:
        lifestyle.append("💪 Exercise: Weather is neutral. Good for a gym session or light jog.")
    
    # Food & Diet
    if temp > 32:
        lifestyle.append("🥗 Diet: Eat cooling foods like cucumber, melons, and salads.")
    elif temp < 15:
        lifestyle.append("🍲 Diet: Hearty soups and root vegetables recommended.")
    else:
        lifestyle.append("🍎 Diet: Balanced weather. Great time for fresh fruits and veggies.")
    
    # Productivity & Mood
    if rain > 0 or weather_code > 50:
        lifestyle.append("🎧 Focus: Gloomy weather is perfect for deep work. Use lo-fi beats.")
    elif is_day and 20 < temp < 30:
        lifestyle.append("💡 Focus: Great weather! Take walking meetings if possible.")
    else:
        lifestyle.append("✨ Mood: Steady weather. Good for clearing your backlog.")
    
    # Home Environment
    if humidity > 70:
        lifestyle.append("🏠 Home: Run a dehumidifier or AC dry mode to prevent mold.")
    elif humidity < 30:
        lifestyle.append("🏠 Home: Air is dry. Use a humidifier for better sleep.")
    else:
        lifestyle.append("🏠 Home: Indoor climate is comfortable. Open windows for fresh air.")
    
    # DAILY ROUTINE
    if rain > 0:
        routine.append("07:00 AM - 🧘 Indoor Yoga (Rainy Start)")
    elif aqi < 50:
        routine.append("07:00 AM - 🏃 Morning Run (Clean Air)")
    else:
        routine.append("07:00 AM - 🏋️ Gym Workout / Stretching")
    
    if rain > 0.5:
        routine.append("08:30 AM - 🚗 Leave 20m early (Traffic)")
    else:
        routine.append("08:45 AM - 🚇 Regular Commute")
    
    if temp > 30:
        routine.append("01:00 PM - 🥗 Light Salad Lunch (Heat)")
    elif temp < 15:
        routine.append("01:00 PM - 🍜 Hot Soup & Sandwich")
    else:
        routine.append("01:00 PM - 🍱 Balanced Healthy Lunch")
    
    if temp > 28:
        routine.append("03:00 PM - 🥤 Hydration Break (Iced Tea)")
    else:
        routine.append("03:00 PM - ☕ Coffee/Tea Break")
    
    if rain == 0 and 15 < temp < 27:
        routine.append("06:30 PM - 🚶 Evening Walk / Park")
    elif aqi > 100:
        routine.append("06:30 PM - 🏠 Indoor Hobby (Bad Air)")
    else:
        routine.append("06:30 PM - 📖 Reading / Relaxation")
    
    return {
        'outfit': outfit,
        'hygiene': hygiene,
        'lifestyle': lifestyle,
        'routine': routine
    }

def get_aqi_status(aqi_value):
    if aqi_value < 40:
        return "Good", "🟢"
    elif aqi_value < 80:
        return "Moderate", "🟡"
    else:
        return "Poor", "🔴"

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'city' not in st.session_state:
    st.session_state.city = "Bengaluru"

# Authentication Screen
if not st.session_state.authenticated:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style='text-align: center; padding: 40px; background-color: rgba(31, 41, 55, 0.8); border-radius: 20px; border: 1px solid rgba(75, 85, 99, 0.5);'>
            <h1>🌧️ WeatherWise Pro</h1>
            <p style='color: #93c5fd; margin-bottom: 30px;'>Get personalized weather insights daily</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            name = st.text_input("Full Name", placeholder="John Doe")
            email = st.text_input("Email Address", placeholder="name@example.com")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            
            submitted = st.form_submit_button("🚀 Sign In", use_container_width=True)
            
            if submitted:
                if name and email and password:
                    st.session_state.authenticated = True
                    st.session_state.user_name = name
                    st.rerun()
                else:
                    st.error("Please fill in all fields")

else:
    # Main App
    # Header
    col1, col2, col3 = st.columns([2, 3, 2])
    
    with col1:
        st.markdown(f"""
        <div style='display: flex; align-items: center; gap: 15px;'>
            <div style='background: linear-gradient(135deg, #2563eb, #4f46e5); padding: 12px; border-radius: 12px;'>
                <span style='font-size: 32px;'>🌧️</span>
            </div>
            <div>
                <h2 style='margin: 0; font-size: 24px;'>WeatherWise Pro</h2>
                <p style='margin: 0; color: #93c5fd; font-size: 12px;'>Daily Routine & Lifestyle AI</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        search_col1, search_col2 = st.columns([3, 1])
        with search_col1:
            city_input = st.text_input("", value=st.session_state.city, placeholder="Search city...", label_visibility="collapsed")
        with search_col2:
            if st.button("Search", use_container_width=True):
                st.session_state.city = city_input
                st.rerun()
    
    with col3:
        logout_col1, logout_col2 = st.columns([3, 1])
        with logout_col1:
            st.markdown(f"""
            <div style='text-align: right; padding-top: 10px;'>
                <p style='margin: 0; font-size: 12px; color: #9ca3af;'>Hello,</p>
                <p style='margin: 0; font-size: 14px; font-weight: bold;'>{st.session_state.user_name}</p>
            </div>
            """, unsafe_allow_html=True)
        with logout_col2:
            if st.button("🚪", help="Sign Out"):
                st.session_state.authenticated = False
                st.session_state.user_name = ""
                st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Fetch Weather Data
    with st.spinner(f"Fetching weather data for {st.session_state.city}..."):
        location_data = get_lat_lon(st.session_state.city)
        
        if location_data:
            weather_data = get_weather_data(location_data['latitude'], location_data['longitude'])
            aqi_data = get_aqi_data(location_data['latitude'], location_data['longitude'])
            
            current = weather_data['current']
            daily = weather_data['daily']
            hourly = weather_data['hourly']
            current_aqi = aqi_data['current']['european_aqi']
            
            advisory = generate_smart_advisory(current, daily, current_aqi)
            aqi_status, aqi_emoji = get_aqi_status(current_aqi)
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "🌡️ Temperature",
                    f"{current['temperature_2m']}°C",
                    delta=f"Feels like {current['apparent_temperature']}°C"
                )
            
            with col2:
                dew_point = current['temperature_2m'] - ((100 - current['relative_humidity_2m']) / 5)
                st.metric(
                    "💧 Humidity",
                    f"{current['relative_humidity_2m']}%",
                    delta=f"Dew Point: {dew_point:.1f}°"
                )
            
            with col3:
                st.metric(
                    "💨 Wind Speed",
                    f"{current['wind_speed_10m']} km/h",
                    delta=f"Precipitation: {current['precipitation']}mm"
                )
            
            with col4:
                st.metric(
                    f"{aqi_emoji} Air Quality",
                    current_aqi,
                    delta=aqi_status
                )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Advisory Sections
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("""
                <div style='background-color: rgba(37, 99, 235, 0.1); border: 1px solid rgba(37, 99, 235, 0.3); border-radius: 12px; padding: 20px; height: 100%;'>
                    <h3 style='color: #93c5fd; margin-top: 0; display: flex; align-items: center; gap: 8px;'>
                        <span>👔</span> Daily Wardrobe
                    </h3>
                """, unsafe_allow_html=True)
                for item in advisory['outfit']:
                    st.markdown(f"<p style='font-size: 14px; line-height: 1.6; margin: 8px 0;'>• {item}</p>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div style='background-color: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 12px; padding: 20px; height: 100%;'>
                    <h3 style='color: #fcd34d; margin-top: 0; display: flex; align-items: center; gap: 8px;'>
                        <span>✨</span> Self Care Rituals
                    </h3>
                """, unsafe_allow_html=True)
                for item in advisory['hygiene']:
                    st.markdown(f"<p style='font-size: 14px; line-height: 1.6; margin: 8px 0;'>• {item}</p>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div style='background-color: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 12px; padding: 20px; height: 100%;'>
                    <h3 style='color: #6ee7b7; margin-top: 0; display: flex; align-items: center; gap: 8px;'>
                        <span>☕</span> Lifestyle & Diet
                    </h3>
                """, unsafe_allow_html=True)
                for item in advisory['lifestyle']:
                    st.markdown(f"<p style='font-size: 14px; line-height: 1.6; margin: 8px 0;'>• {item}</p>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            
            with col4:
                st.markdown("""
                <div style='background-color: rgba(139, 92, 246, 0.1); border: 1px solid rgba(139, 92, 246, 0.3); border-radius: 12px; padding: 20px; height: 100%;'>
                    <h3 style='color: #c4b5fd; margin-top: 0; display: flex; align-items: center; gap: 8px;'>
                        <span>🕐</span> Today's Routine
                    </h3>
                """, unsafe_allow_html=True)
                for item in advisory['routine']:
                    st.markdown(f"<p style='font-size: 14px; line-height: 1.6; margin: 8px 0;'>• {item}</p>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Charts
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Hourly Temperature Chart
                hours = hourly['time'][:24]
                temps = hourly['temperature_2m'][:24]
                
                if PLOTLY_AVAILABLE:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=[datetime.fromisoformat(h) for h in hours],
                        y=temps,
                        mode='lines',
                        fill='tozeroy',
                        line=dict(color='#60a5fa', width=3),
                        fillcolor='rgba(96, 165, 250, 0.2)'
                    ))
                    
                    fig.update_layout(
                        title="24-Hour Temperature Forecast",
                        xaxis_title="Time",
                        yaxis_title="Temperature (°C)",
                        height=300,
                        plot_bgcolor='rgba(31, 41, 55, 0.3)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white'),
                        xaxis=dict(showgrid=True, gridcolor='rgba(75, 85, 99, 0.3)'),
                        yaxis=dict(showgrid=True, gridcolor='rgba(75, 85, 99, 0.3)')
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    # Fallback to simple line chart
                    st.markdown("### 📈 24-Hour Temperature Forecast")
                    chart_data = pd.DataFrame({
                        'Time': [datetime.fromisoformat(h) for h in hours],
                        'Temperature (°C)': temps
                    })
                    st.line_chart(chart_data.set_index('Time'))
            
            with col2:
                st.markdown(f"""
                ### 📍 Location
                **{location_data['name']}, {location_data.get('country', '')}**
                
                🌅 Sunrise: {datetime.fromisoformat(daily['sunrise'][0]).strftime('%H:%M')}  
                🌇 Sunset: {datetime.fromisoformat(daily['sunset'][0]).strftime('%H:%M')}
                
                📌 Lat: {location_data['latitude']:.2f}  
                📌 Lon: {location_data['longitude']:.2f}
                """)
                
                # Map
                map_url = f"https://www.openstreetmap.org/export/embed.html?bbox={location_data['longitude']-0.05}%2C{location_data['latitude']-0.05}%2C{location_data['longitude']+0.05}%2C{location_data['latitude']+0.05}&layer=mapnik&marker={location_data['latitude']}%2C{location_data['longitude']}"
                st.markdown(f'<iframe width="100%" height="200" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="{map_url}"></iframe>', unsafe_allow_html=True)
            
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("<div style='text-align: center; color: #6b7280; font-size: 12px;'>WeatherWise Pro v2.2 | Enhanced Advice Engine</div>", unsafe_allow_html=True)
            
        else:
            st.error(f"City '{st.session_state.city}' not found. Please try another city.")
