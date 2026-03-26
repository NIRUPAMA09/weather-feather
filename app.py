import streamlit as st
import requests
from datetime import datetime
import time
import pandas as pd

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SkySense – Weather Dashboard",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Load CSS ────────────────────────────────────────────────────────────────────
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── API Key ────────────────────────────────────────────────────────────────────
OWM_KEY    = st.secrets.get("OPENWEATHER_API_KEY", "")
IPINFO_KEY = st.secrets.get("IPINFO_KEY", "")

# ══════════════════════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=300)
def get_location_from_ip() -> dict:
    try:
        token = f"?token={IPINFO_KEY}" if IPINFO_KEY else ""
        r = requests.get(f"https://ipinfo.io/json{token}", timeout=5)
        data = r.json()
        return {"city": data.get("city", "London"), "success": True}
    except Exception:
        return {"city": "London", "success": False}


@st.cache_data(ttl=300)
def fetch_current_weather(city: str) -> dict | None:
    if not OWM_KEY:
        return None
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={OWM_KEY}&units=metric"
    )
    r = requests.get(url, timeout=8)
    return r.json() if r.status_code == 200 else None


@st.cache_data(ttl=300)
def fetch_forecast(city: str) -> dict | None:
    if not OWM_KEY:
        return None
    url = (
        f"https://api.openweathermap.org/data/2.5/forecast"
        f"?q={city}&appid={OWM_KEY}&units=metric"
    )
    r = requests.get(url, timeout=8)
    return r.json() if r.status_code == 200 else None


def unix_to_time(ts: int, tz_offset: int = 0) -> str:
    return datetime.utcfromtimestamp(ts + tz_offset).strftime("%H:%M")


def unix_to_date(ts: int) -> str:
    return datetime.utcfromtimestamp(ts).strftime("%a %d %b")


def weather_emoji(condition: str) -> str:
    cond = condition.lower()
    if "thunder" in cond: return "⛈️"
    if "drizzle" in cond: return "🌦️"
    if "rain"    in cond: return "🌧️"
    if "snow"    in cond: return "❄️"
    if "mist"    in cond or "fog" in cond: return "🌫️"
    if "cloud"   in cond: return "☁️"
    if "clear"   in cond: return "☀️"
    return "🌤️"


def alert_level(w: dict) -> list[str]:
    alerts = []
    wind  = w.get("wind", {}).get("speed", 0)
    temp  = w.get("main", {}).get("temp", 20)
    cond  = w.get("weather", [{}])[0].get("main", "")
    humid = w.get("main", {}).get("humidity", 50)
    if wind  > 15:          alerts.append(f"🌬️ Strong winds: {wind:.1f} m/s – secure loose objects.")
    if temp  > 38:          alerts.append(f"🔥 Extreme heat: {temp:.1f}°C – stay hydrated.")
    if temp  < 0:           alerts.append(f"🥶 Freezing temperatures: {temp:.1f}°C – dress warmly.")
    if "Thunder" in cond:   alerts.append("⛈️ Thunderstorm detected – avoid open areas.")
    if "Rain"    in cond:   alerts.append("☔ Rain expected – carry an umbrella.")
    if humid > 85:          alerts.append(f"💧 Very high humidity: {humid}% – heat index elevated.")
    return alerts


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown('<div class="sidebar-logo">🌤️ SkySense</div>', unsafe_allow_html=True)
    st.markdown("---")

    if "detected_city" not in st.session_state:
        loc = get_location_from_ip()
        st.session_state.detected_city = loc["city"]

    city_input = st.text_input(
        "📍 City",
        value=st.session_state.detected_city,
        placeholder="e.g. Mumbai, Tokyo, Paris",
    )

    col_a, col_b = st.columns(2)
    with col_a:
        unit = st.radio("🌡️ Unit", ["°C", "°F"])
    with col_b:
        auto_refresh = st.checkbox("🔄 Auto-refresh\n(5 min)", value=False)

    st.markdown("---")
    st.markdown("**ℹ️ About**")
    st.markdown("SkySense uses **OpenWeatherMap** for live weather data.")

    if st.button("🔍 Fetch Weather", use_container_width=True, type="primary"):
        st.cache_data.clear()

if auto_refresh:
    time.sleep(300)
    st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
#  MAIN CONTENT
# ══════════════════════════════════════════════════════════════════════════════

city = city_input.strip() or "London"

st.markdown(f'<h1 class="dashboard-title">🌍 {city} Weather Dashboard</h1>', unsafe_allow_html=True)
st.markdown(f'<p class="last-updated">Last updated: {datetime.now().strftime("%d %b %Y, %H:%M:%S")}</p>', unsafe_allow_html=True)

if not OWM_KEY:
    st.warning(
        "⚠️ **OpenWeatherMap API key not found.**\n\n"
        "Add `OPENWEATHER_API_KEY = 'your_key'` to `.streamlit/secrets.toml`\n\n"
        "Get a free key at [openweathermap.org](https://openweathermap.org/api)."
    )
    st.stop()

with st.spinner("Fetching live weather data…"):
    weather  = fetch_current_weather(city)
    forecast = fetch_forecast(city)

if not weather:
    st.error(f"❌ Could not find weather data for **{city}**. Check spelling or try another city.")
    st.stop()

def c_to_display(c: float) -> str:
    if unit == "°F":
        return f"{c * 9/5 + 32:.1f}°F"
    return f"{c:.1f}°C"

# ══════════════════════════════════════════════════════════════════════════════
#  ROW 1 – HERO CARD
# ══════════════════════════════════════════════════════════════════════════════

main  = weather["main"]
winfo = weather["weather"][0]
wind  = weather["wind"]
sys   = weather.get("sys", {})
tz    = weather.get("timezone", 0)

temp       = main["temp"]
feels_like = main["feels_like"]
humidity   = main["humidity"]
pressure   = main["pressure"]
wind_speed = wind["speed"]
wind_deg   = wind.get("deg", 0)
visibility = weather.get("visibility", 10000) / 1000
emoji      = weather_emoji(winfo["main"])
sunrise_str = unix_to_time(sys.get("sunrise", 0), tz)
sunset_str  = unix_to_time(sys.get("sunset",  0), tz)

col1, col2, col3 = st.columns([2, 1.2, 1.2])

with col1:
    st.markdown(f"""
    <div class="hero-card">
        <div class="hero-emoji">{emoji}</div>
        <div class="hero-temp">{c_to_display(temp)}</div>
        <div class="hero-desc">{winfo["description"].title()}</div>
        <div class="hero-city">📍 {weather.get("name")}, {sys.get("country","")}</div>
        <div class="hero-feels">Feels like {c_to_display(feels_like)}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown('<div class="section-title">🌡️ Conditions</div>', unsafe_allow_html=True)
    metrics = [
        ("💧 Humidity",   f"{humidity}%"),
        ("🔵 Pressure",   f"{pressure} hPa"),
        ("👁️ Visibility", f"{visibility:.1f} km"),
        ("💨 Wind Speed", f"{wind_speed} m/s"),
        ("🧭 Wind Dir",   f"{wind_deg}°"),
    ]
    for label, val in metrics:
        st.markdown(
            f'<div class="metric-row"><span>{label}</span>'
            f'<span class="metric-val">{val}</span></div>',
            unsafe_allow_html=True,
        )

with col3:
    st.markdown('<div class="section-title">🌅 Sun Times</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="sun-card">
        <div class="sun-item">
            <div class="sun-icon">🌄</div>
            <div class="sun-label">Sunrise</div>
            <div class="sun-time">{sunrise_str}</div>
        </div>
        <div class="sun-divider"></div>
        <div class="sun-item">
            <div class="sun-icon">🌇</div>
            <div class="sun-label">Sunset</div>
            <div class="sun-time">{sunset_str}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    clouds = weather.get("clouds", {}).get("all", 0)
    st.markdown(f"""
    <div class="cloud-bar-wrap">
        <span class="cloud-label">☁️ Cloud Cover: {clouds}%</span>
        <div class="cloud-bar"><div class="cloud-fill" style="width:{clouds}%"></div></div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  ROW 2 – ALERTS
# ══════════════════════════════════════════════════════════════════════════════

alerts = alert_level(weather)
if alerts:
    st.markdown('<div class="section-title">⚠️ Weather Alerts</div>', unsafe_allow_html=True)
    for a in alerts:
        st.markdown(f'<div class="alert-banner">{a}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  ROW 3 – 5-DAY FORECAST
# ══════════════════════════════════════════════════════════════════════════════

st.markdown('<div class="section-title">📅 5-Day Forecast</div>', unsafe_allow_html=True)

if forecast:
    daily: dict[str, dict] = {}
    for item in forecast["list"]:
        day = unix_to_date(item["dt"])
        if day not in daily:
            daily[day] = {
                "temps": [], "humidity": [],
                "wind": [], "desc": item["weather"][0]["description"],
                "main": item["weather"][0]["main"],
            }
        daily[day]["temps"].append(item["main"]["temp"])
        daily[day]["humidity"].append(item["main"]["humidity"])
        daily[day]["wind"].append(item["wind"]["speed"])

    cols = st.columns(min(5, len(daily)))
    for i, (day, data) in enumerate(list(daily.items())[:5]):
        t_min = min(data["temps"])
        t_max = max(data["temps"])
        h_avg = sum(data["humidity"]) / len(data["humidity"])
        w_avg = sum(data["wind"])     / len(data["wind"])
        em    = weather_emoji(data["main"])
        with cols[i]:
            st.markdown(f"""
            <div class="forecast-card">
                <div class="fc-day">{day}</div>
                <div class="fc-emoji">{em}</div>
                <div class="fc-desc">{data['desc'].title()}</div>
                <div class="fc-temp">{c_to_display(t_max)} / {c_to_display(t_min)}</div>
                <div class="fc-meta">💧 {h_avg:.0f}%  💨 {w_avg:.1f} m/s</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Trend charts ───────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">📈 Trend (next 40 hrs)</div>', unsafe_allow_html=True)
    rows = []
    for item in forecast["list"][:14]:
        dt  = datetime.utcfromtimestamp(item["dt"])
        tmp = item["main"]["temp"]
        hum = item["main"]["humidity"]
        wnd = item["wind"]["speed"]
        if unit == "°F":
            tmp = tmp * 9/5 + 32
        rows.append({"Time": dt, "Temperature": tmp, "Humidity": hum, "Wind (m/s)": wnd})
    df = pd.DataFrame(rows).set_index("Time")

    tab1, tab2, tab3 = st.tabs(["🌡️ Temperature", "💧 Humidity", "💨 Wind"])
    with tab1:
        st.line_chart(df[["Temperature"]], color=["#FF6B6B"])
    with tab2:
        st.line_chart(df[["Humidity"]], color=["#4ECDC4"])
    with tab3:
        st.line_chart(df[["Wind (m/s)"]], color=["#A8E6CF"])

# ══════════════════════════════════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown(
    '<p class="footer">Built with ❤️ using Streamlit · Data: OpenWeatherMap</p>',
    unsafe_allow_html=True,
)
