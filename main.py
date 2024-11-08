import streamlit as st
import requests
import time
import re
import random
from small_talk import *
from PIL import Image
import pandas as pd
import joblib
# import kagglehub

# # Download latest version
# path = kagglehub.dataset_download('./assets')

# print("Path to dataset files:", path)

st.set_page_config(
    page_title="Weather Daily",
    page_icon="./assets/logo.png"
)

st.title("Weather Daily")
st.caption(
    "Find the current weather, forecast the future or find the AQI in your region seamlessly.")

# Theme configuration setup
ms = st.session_state
if "themes" not in ms:
    ms.themes = {
        "current_theme": "light",
        "refreshed": True,
        "light": {
            "theme.base": "dark",
            "theme.backgroundColor": "#2c313c",
            "theme.primaryColor": "#c98bdb",
            "theme.secondaryBackgroundColor": "#5591f5",
            "theme.textColor": "white",
            "button_face": "🌙"
        },
        "dark": {
            "theme.base": "light",
            "theme.backgroundColor": "white",
            "theme.primaryColor": "#5591f5",
            "theme.secondaryBackgroundColor": "#DEFCF9",
            "theme.textColor": "#0a1464",
            "button_face": "☀️"
        },
    }

# Theme toggle function


def ChangeTheme():
    previous_theme = ms.themes["current_theme"]
    tdict = ms.themes["light"] if ms.themes["current_theme"] == "light" else ms.themes["dark"]
    for vkey, vval in tdict.items():
        if vkey.startswith("theme"):
            st._config.set_option(vkey, vval)

    ms.themes["refreshed"] = False
    ms.themes["current_theme"] = "dark" if previous_theme == "light" else "light"


btn_face = ms.themes["light"]["button_face"] if ms.themes["current_theme"] == "light" else ms.themes["dark"]["button_face"]
st.button(btn_face, on_click=ChangeTheme)

if ms.themes["refreshed"] == False:
    ms.themes["refreshed"] = True
    st.rerun()


# Load city data
cities_df = pd.read_csv('./assets/world-cities.csv')
city_names = set(cities_df["name"].str.lower())

# Helper function to check for city name in query


def contains_city(query):
    words = set(re.findall(r'\w+', query.lower()))
    return bool(words & city_names)


# Welcome message
welcome_message = random.choice(welcome_messages)

model = joblib.load('./assets/svm_model.joblib') 

def classify_text(user_input):
    prediction = model.predict([user_input])[0]
    return prediction


# Parsing query for location and forecast type


def parse_query(user_query):
    location, category, days_requested = None, "current", 1

    user_query = user_query.lower()
    if "weather in" not in user_query:
        user_query = "weather in " + user_query

    # Determine category of forecast
    if "aqi" in user_query:
        category, location = "aqi", re.search(
            r"aqi in (.+)", user_query) or re.search(r"(.+) aqi", user_query)
    elif "tomorrow" in user_query:
        category, days_requested = "specific", 1
    elif days_match := re.search(r"(after|for|in) (\d+) days?", user_query):
        category, days_requested = "specific" if days_match[1] == "after" else "multiple", int(
            days_match[2])
    elif "this week" in user_query:
        category, days_requested = "multiple", 7

    # Extract location if not set
    if not location:
        location = re.search(r"weather in (.+)", user_query)
    location = location.group(1).strip() if location else "unknown location"

    return location, category, days_requested

# Retrieve weather data based on category


def get_weather_data(location, category, days_requested):
    if location.lower() == "delhi":
        location = "New Delhi"
    api_key = "ff77f4dadf90414895e164755240511"  # Replace with your actual API key

    # API URL setup based on forecast type
    days_to_fetch = min(days_requested, 10)
    api_url = (
        f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={location}&aqi={'yes' if category == 'aqi' else 'no'}"
        if category == "current" or category == "aqi"
        else f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={location}&days={days_to_fetch}&aqi=no&alerts=no"
    )

    try:
        response = requests.get(api_url)
        data = response.json()

        # Check for API error response
        if response.status_code != 200 or 'error' in data:
            error_message = data.get('error', {}).get(
                'message', 'Unknown error occurred')
            return f"Error fetching weather data: {error_message}"

        # Ensure 'location' key exists
        if 'location' not in data:
            return "Error: Unable to retrieve location information."

        location_info = f"{data['location']['name'].title()}, {data['location']['region']}, {data['location']['country']}"

        # Handle different categories
        if category == "current":
            curr = data['current']
            return f"Current weather in {location_info} (as of {data['location']['localtime']}):\n- {curr['condition']['text']}\n- Temp: {curr['temp_c']}°C\n- Feels like: {curr['feelslike_c']}°C\n- Humidity: {curr['humidity']}%\n- Wind: {curr['wind_kph']} kph\n- Precipitation: {curr['precip_mm']} mm"
        elif category == "specific":
            forecast = data['forecast']['forecastday'][-1]
            return f"Forecast for {location_info} on {forecast['date']}:\n- {forecast['day']['condition']['text']}\n- Max Temp: {forecast['day']['maxtemp_c']}°C\n- Min Temp: {forecast['day']['mintemp_c']}°C\n- Chance of Rain: {forecast['day'].get('daily_chance_of_rain', 0)}%"
        elif category == "multiple":
            forecast_summary = f"Multi-day forecast for {location_info}:\n\n"
            for day in data['forecast']['forecastday']:
                forecast_summary += f"Date: {day['date']} - {day['day']['condition']['text']} - Max: {day['day']['maxtemp_c']}°C, Min: {day['day']['mintemp_c']}°C, Rain: {day['day'].get('daily_chance_of_rain', 0)}%\n"
            return forecast_summary.strip()
        elif category == "aqi":
            aq = data['current']['air_quality']
            return f"AQI for {location_info}:\n- PM 2.5: {aq['pm2_5']}\n- PM 10: {aq['pm10']}\n- CO: {aq['co']}\n- NO₂: {aq['no2']}\n- O₃: {aq['o3']}\n- SO₂: {aq['so2']}"
    except requests.exceptions.RequestException as e:
        return f"Unable to fetch weather data due to a network error: {str(e)}"
    except KeyError as e:
        return f"Unable to find weather data for this location."


# Chat history and user input handling
person, chatbot = Image.open(
    'assets/person.png'), Image.open('assets/chatbot.png')

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": welcome_message}]

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=person if message["role"] == "user" else chatbot):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me about the weather!"):
    with st.chat_message("user", avatar=person):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Classify the user input
    user_query_type = classify_text(prompt)

    if user_query_type == "weather":
        # Weather-related response
        location, category, days_requested = parse_query(prompt)
        assistant_response = get_weather_data(
            location, category, days_requested) if location != "unknown location" else "Please specify a location."
    else:
        # Casual response (small talk)
        if any(greet in prompt.lower() for greet in greetings):
            assistant_response = random.choice(greeting_responses)
        elif any(query in prompt.lower() for query in general_queries):
            assistant_response = random.choice(general_query_responses)
        elif any(thank in prompt.lower() for thank in thanks_phrases):
            assistant_response = random.choice(thanks_responses)
        elif any(farewell in prompt.lower() for farewell in farewells):
            assistant_response = random.choice(farewell_responses)
        else:
            assistant_response = "I'm here to help! Ask me anything about the weather."

    # Display the response in the chat
    with st.chat_message("assistant", avatar=chatbot):
        message_placeholder = st.empty()
        full_response = ""
        for chunk in assistant_response.split():
            full_response += chunk + " "
            time.sleep(0.05)
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response})
