import requests
import tkinter as tk
from tkinter import font as tkfont
from datetime import datetime
import calendar
import random
import threading

# API Configuration
WEATHER_API_KEY = "WeatherAPI"  # Replace with your actual API key
NEWS_API_KEY = "YOUR_NEWS_API_KEY"        # Replace with your actual News API key
CITY = "Ottawa"

def is_garbage_week():
    """Determine if it's garbage collection week in Ottawa based on the week number."""
    current_week = datetime.now().isocalendar()[1]
    return current_week % 2 == 0

def get_weather():
    """Fetches forecast data from WeatherAPI, including temperature, AQI, alerts, and more."""
    try:
        url = f"http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={CITY}&days=1&aqi=yes&alerts=yes"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        # Parse current weather details
        current = data.get("current", {})
        forecast = data.get("forecast", {}).get("forecastday", [{}])[0]
        astro = forecast.get("astro", {})
        alerts = data.get("alerts", {}).get("alert", [])
        
        return {
            "temperature": current.get("temp_c"),
            "description": current.get("condition", {}).get("text"),
            "humidity": current.get("humidity"),
            "wind_speed": current.get("wind_kph"),
            "sunrise": astro.get("sunrise"),
            "sunset": astro.get("sunset"),
            "aqi": current.get("air_quality", {}).get("us-epa-index", "N/A"),
            "alerts": [alert.get("headline") for alert in alerts] if alerts else ["No alerts"]
        }
    except requests.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None

def get_daily_quote():
    """Fetches a daily quote from the ZenQuotes API."""
    try:
        url = "https://zenquotes.io/api/random"
        response = requests.get(url, timeout=5, verify=False)
        response.raise_for_status()
        data = response.json()
        return f"'{data[0]['q']}' - {data[0]['a']}"
    except requests.RequestException as e:
        print(f"Error fetching quote: {e}")
    return "Could not fetch a quote."

def get_exchange_rate():
    """Fetches the current CAD exchange rates."""
    try:
        url = "https://api.exchangerate-api.com/v4/latest/CAD"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return {
            "USD": data["rates"]["USD"],
            "EUR": data["rates"]["EUR"],
            "GBP": data["rates"]["GBP"]
        }
    except requests.RequestException as e:
        print(f"Error fetching exchange rate: {e}")
    return {}

def get_covid_data():
    """Fetches COVID-19 cases data for Canada."""
    try:
        url = "https://disease.sh/v3/covid-19/countries/Canada"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return f"COVID-19 Cases in Canada: {data['cases']}"
    except requests.RequestException as e:
        print(f"Error fetching COVID-19 data: {e}")
    return "Could not fetch COVID-19 data."

def check_starbucks_status():
    """Determines if Starbucks is open based on the current day and time."""
    current_hour = datetime.now().hour
    return "Open" if 6 <= current_hour < 22 else "Closed"

def get_health_tip():
    """Returns a random health tip."""
    tips = [
        "Drink plenty of water to stay hydrated.",
        "Get at least 7-8 hours of sleep each night.",
        "Take short breaks during work to avoid burnout.",
        "Include fruits and vegetables in your diet.",
        "Exercise for at least 30 minutes every day.",
        "Practice deep breathing to reduce stress."
    ]
    return random.choice(tips)

def get_local_news():
    """Fetches the latest local news headlines."""
    try:
        url = f"https://newsapi.org/v2/top-headlines?country=ca&apiKey=ReplaceWithAPIKey"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        headlines = [article["title"] for article in data.get("articles", [])[:3]]
        return " | ".join(headlines) if headlines else "No recent news available."
    except requests.RequestException as e:
        print(f"Error fetching news data: {e}")
        return "Could not fetch news data."

def get_fun_fact():
    """Returns a random fun fact."""
    facts = [
        "Did you know? Honey never spoils.",
        "Bananas are berries, but strawberries aren't!",
        "Wombat poop is cube-shaped.",
        "The Eiffel Tower can be 15 cm taller in summer due to heat expansion.",
        "A shrimp's heart is in its head."
    ]
    return random.choice(facts)

def get_traffic_info():
    """Returns a simple traffic status message."""
    traffic_levels = ["Light", "Moderate", "Heavy"]
    return f"Traffic is currently: {random.choice(traffic_levels)}"

def update_gui():
    """Update the GUI with the latest data."""
    now = datetime.now()
    date_label.config(text=f"{now.strftime('%A, %B %d, %Y')}")
    time_label.config(text=f"{now.strftime('%I:%M %p')}")
    week_label.config(text=f"Week of Year: {now.isocalendar()[1]}")
    leap_label.config(text=f"Leap Year: {'Yes' if calendar.isleap(now.year) else 'No'}")

    # Garbage collection schedule
    today = now.strftime("%A")
    collection_type = "Recycling & Green Bin"
    if today == "Wednesday" and is_garbage_week():
        collection_type += " & Garbage"
    schedule_label.config(text=f"Today is {today}. Collection: {collection_type if today == 'Wednesday' else 'No Collection Today'}")

    # Fetch data in threads to avoid blocking the UI
    threading.Thread(target=update_weather).start()
    threading.Thread(target=update_quote).start()
    threading.Thread(target=update_covid_data).start()
    threading.Thread(target=update_exchange_rate).start()
    threading.Thread(target=update_starbucks_status).start()
    threading.Thread(target=update_news).start()
    threading.Thread(target=update_fun_fact).start()
    threading.Thread(target=update_traffic_info).start()

    # Refresh every minute for real-time data like time or Starbucks status
    root.after(60000, update_gui)

def update_weather():
    weather_data = get_weather()
    if weather_data:
        weather_label.config(text=f"{weather_data['temperature']}°C, {weather_data['description']}")
        humidity_label.config(text=f"Humidity: {weather_data['humidity']}%")
        wind_label.config(text=f"Wind: {weather_data['wind_speed']} km/h")
        sunrise_label.config(text=f"Sunrise: {weather_data['sunrise']}")
        sunset_label.config(text=f"Sunset: {weather_data['sunset']}")
        aqi_label.config(text=f"AQI: {weather_data['aqi']}")
        alerts_text = "\n".join(weather_data["alerts"])
        weather_alerts_label.config(text=f"Weather Alerts: {alerts_text}")
    else:
        weather_label.config(text="Weather data not available.")

def update_quote():
    quote_label.config(text=get_daily_quote())

def update_covid_data():
    covid_label.config(text=get_covid_data())

def update_exchange_rate():
    exchange_rates = get_exchange_rate()
    if exchange_rates:
        exchange_label.config(text=f"CAD to USD: {exchange_rates['USD']}\nCAD to EUR: {exchange_rates['EUR']}\nCAD to GBP: {exchange_rates['GBP']}")
    else:
        exchange_label.config(text="Exchange rates not available.")

def update_starbucks_status():
    starbucks_label.config(text=f"Starbucks Status: {check_starbucks_status()}")

def update_news():
    news_label.config(text=f"Local News: {get_local_news()}")

def update_fun_fact():
    fun_fact_label.config(text=f"Fun Fact: {get_fun_fact()}")

def update_traffic_info():
    traffic_label.config(text=get_traffic_info())

# Set up the main window
root = tk.Tk()
root.title("Ottawa Dashboard")
root.geometry("700x800")
root.configure(bg="#f2f2f7")

# Custom Fonts
sf_font_large = tkfont.Font(family="Helvetica", size=16, weight="bold")
sf_font_medium = tkfont.Font(family="Helvetica", size=14)
sf_font_small = tkfont.Font(family="Helvetica", size=12)

# UI Components (Date, Time, Weather, Quote, etc.)
top_frame = tk.Frame(root, bg="#f2f2f7")
top_frame.pack(pady=10)
date_label = tk.Label(top_frame, font=sf_font_large, bg="#f2f2f7", fg="#333333")
date_label.pack(side="left", padx=10)
time_label = tk.Label(top_frame, font=sf_font_large, bg="#f2f2f7", fg="#333333")
time_label.pack(side="left", padx=10)

# General Information Frame
info_frame = tk.LabelFrame(root, text="General Info", font=sf_font_medium, bg="#e0e0e0", fg="#333333", padx=10, pady=10)
info_frame.pack(fill="x", padx=20, pady=10)

# Date and Week Information
week_label = tk.Label(info_frame, text="", font=sf_font_small, bg="#e0e0e0", fg="#333333")
week_label.pack(anchor="w")
leap_label = tk.Label(info_frame, text="", font=sf_font_small, bg="#e0e0e0", fg="#333333")
leap_label.pack(anchor="w")

# Add Garbage Collection Schedule Label
schedule_label = tk.Label(info_frame, text="", font=sf_font_small, bg="#e0e0e0", fg="#333333")
schedule_label.pack(anchor="w")

# Weather Frame
weather_frame = tk.LabelFrame(root, text="Weather", font=sf_font_medium, bg="#e0e0e0", fg="#333333", padx=10, pady=10)
weather_frame.pack(fill="x", padx=20, pady=10)
weather_label = tk.Label(weather_frame, font=sf_font_small, bg="#e0e0e0", fg="#333333")
weather_label.pack(anchor="w")
humidity_label = tk.Label(weather_frame, font=sf_font_small, bg="#e0e0e0", fg="#333333")
humidity_label.pack(anchor="w")
wind_label = tk.Label(weather_frame, font=sf_font_small, bg="#e0e0e0", fg="#333333")
wind_label.pack(anchor="w")
sunrise_label = tk.Label(weather_frame, font=sf_font_small, bg="#e0e0e0", fg="#333333")
sunrise_label.pack(anchor="w")
sunset_label = tk.Label(weather_frame, font=sf_font_small, bg="#e0e0e0", fg="#333333")
sunset_label.pack(anchor="w")
aqi_label = tk.Label(weather_frame, font=sf_font_small, bg="#e0e0e0", fg="#333333")
aqi_label.pack(anchor="w")
weather_alerts_label = tk.Label(weather_frame, font=sf_font_small, bg="#e0e0e0", fg="#333333")
weather_alerts_label.pack(anchor="w")

# Additional Info Frames
quote_label = tk.Label(root, font=sf_font_small, bg="#f2f2f7", fg="#333333")
quote_label.pack(pady=5)
covid_label = tk.Label(root, font=sf_font_small, bg="#f2f2f7", fg="#333333")
covid_label.pack(pady=5)
health_tip_label = tk.Label(root, text=f"Health Tip: {get_health_tip()}", font=sf_font_small, bg="#f2f2f7", fg="#333333")
health_tip_label.pack(pady=5)
exchange_label = tk.Label(root, font=sf_font_small, bg="#f2f2f7", fg="#333333")
exchange_label.pack(pady=5)
starbucks_label = tk.Label(root, font=sf_font_small, bg="#f2f2f7", fg="#333333")
starbucks_label.pack(pady=5)

# New Features Frames
news_label = tk.Label(root, font=sf_font_small, bg="#f2f2f7", fg="#333333")
news_label.pack(pady=5)
fun_fact_label = tk.Label(root, font=sf_font_small, bg="#f2f2f7", fg="#333333")
fun_fact_label.pack(pady=5)
traffic_label = tk.Label(root, font=sf_font_small, bg="#f2f2f7", fg="#333333")
traffic_label.pack(pady=5)

# Refresh Button
refresh_button = tk.Button(root, text="Refresh Data", command=update_gui, bg="#007aff", fg="white", font=sf_font_medium, relief="flat", bd=0, padx=20, pady=10)
refresh_button.pack(pady=20)

# Initial Update and Start Main Loop
update_gui()
root.mainloop()
