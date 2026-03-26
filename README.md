# 🌤️ SkySense – AI Weather Dashboard

A beautiful, full-featured weather dashboard built with **Streamlit** and powered by **OpenWeatherMap** + **Claude AI**.

---

## ✨ Features

| Feature | Details |
|---|---|
| 🌡️ Real-time Weather | Temperature, feels-like, humidity, pressure, visibility |
| 📍 Auto Location Detection | IP-based city detection on first load |
| 💨 Wind Info | Speed and direction |
| 🌅 Sunrise / Sunset | Local times with timezone correction |
| ⚠️ Smart Alerts | Rule-based warnings for heat, cold, wind, storms |
| 📅 5-Day Forecast | Daily high/low, conditions, humidity, wind |
| 📈 Interactive Charts | Temperature / humidity / wind trend tabs |
| 🤖 AI Insights | Claude generates contextual weather analysis |
| 🔄 Auto Refresh | Optional 5-minute auto-refresh |
| 🌡️ Unit Toggle | Switch between °C and °F |

---

## 🚀 Quick Start

### 1. Clone / open in VS Code

```bash
git clone <your-repo-url>
cd weather_dashboard
code .
```

### 2. Create virtual environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add API keys

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Then open `.streamlit/secrets.toml` and fill in:

```toml
OPENWEATHER_API_KEY = "your_key_here"   # https://openweathermap.org/api
ANTHROPIC_API_KEY   = "your_key_here"   # https://console.anthropic.com
IPINFO_KEY          = ""                # optional
```

> **Free tier on OpenWeatherMap** includes Current Weather + 5-day Forecast APIs.

### 5. Run locally

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## ☁️ Deploy to Streamlit Cloud

1. Push your project to **GitHub** (`.gitignore` already excludes secrets).
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**.
3. Select your repo and set `app.py` as the entry point.
4. Under **Advanced settings → Secrets**, paste your secrets in TOML format:
   ```toml
   OPENWEATHER_API_KEY = "..."
   ANTHROPIC_API_KEY   = "..."
   ```
5. Click **Deploy** 🎉

---

## 📁 Project Structure

```
weather_dashboard/
├── app.py                        ← Main Streamlit app
├── style.css                     ← Custom dark-mode CSS
├── requirements.txt
├── .gitignore
└── .streamlit/
    ├── config.toml               ← Theme & server config
    └── secrets.toml.example      ← Copy → secrets.toml and fill keys
```

---

## 🔑 API Keys

| Service | Free Tier | Link |
|---|---|---|
| OpenWeatherMap | 60 calls/min, current + forecast | [openweathermap.org/api](https://openweathermap.org/api) |
| Anthropic Claude | Pay-as-you-go | [console.anthropic.com](https://console.anthropic.com) |
| ipinfo.io | 50k req/month (no key needed) | [ipinfo.io](https://ipinfo.io) |

---

## 🛠️ VS Code Tips

- Install the **Python** and **Pylance** extensions.
- Use the integrated terminal to run `streamlit run app.py`.
- The **Streamlit** VS Code extension (by Streamlit) gives you a live preview button.
