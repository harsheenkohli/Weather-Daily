"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import secrets
import streamlit as st
import requests
import time
import re
from small_talk import *
from PIL import Image
import pandas as pd
import joblib
from fuzzywuzzy import fuzz, process

api_key = st.secrets['API_KEY']
aqi_key = st.secrets['AQI_KEY']

st.set_page_config(
    page_title="Weather Daily",
    page_icon="./assets/logo.png"
)

st.title("Weather-Daily")
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

cities_df = pd.read_csv('./assets/world-cities.csv')
city_names = set(cities_df["name"].str.lower())


def contains_city(query):
    words = set(re.findall(r'\w+', query.lower()))
    return bool(words & city_names)


welcome_message = secrets.choice(welcome_messages)

model = joblib.load('./assets/svm_model.joblib')


def classify_text(user_input):
    prediction = model.predict([user_input])[0]
    return prediction


def parse_query(user_query):
    location, category, days_requested = None, "current", 1
    user_query = user_query.lower()

    # Add 'weather in' for better parsing if not present
    if "weather in" not in user_query and not user_query.startswith("aqi"):
        user_query = "weather in " + user_query

    # Handle AQI requests
    if "aqi" in user_query:
        category = "aqi"
        location_match = re.search(
            r"aqi in (.+)", user_query) or re.search(r"(.+) aqi", user_query)
        location = location_match.group(1).strip() if location_match else None

    # Handle specific or multiple days forecast
    elif "tomorrow" in user_query:
        category, days_requested = "specific", 2
    elif days_match := re.search(r"(after|for|in) (\d+) days?", user_query):
        days_requested = int(days_match[2]) + 1
        category = "specific" if days_match[1] == "after" else "multiple"
    elif "this week" in user_query:
        category, days_requested = "multiple", 7

    # Extract location
    if not location:
        location_match = re.search(r"weather in (.+)", user_query)
        location = location_match.group(1).strip() if location_match else None

    location = location if location and location.lower(
    ) != "unknown location" else "unknown location"
    return location, category, days_requested


def calc_aqi(location):
    url = f'https://api.waqi.info/feed/{location}/?token={aqi_key}'
    try:
        response = requests.get(url)
        data = response.json()
        if data['status'] != 'ok':
            # error_message = data.get('error', {}).get('message', 'Unknown error occurred')
            return "Unknown", "Unknown"

        aqi_index = data["data"]["aqi"]
        status = ""
        if aqi_index <= 50:
            status = "Good"
        elif aqi_index <= 100:
            status = "Satisfactory"
        elif aqi_index <= 200:
            status = "Moderate"
        elif aqi_index <= 300:
            status = "Poor"
        elif aqi_index <= 400:
            status = "Very Poor"
        elif aqi_index <= 500:
            status = "Severe"
        else:
            status = "Hazardous"
        return aqi_index, status
    except requests.exceptions.RequestException as e:
        return f"Unable to fetch AQI data due to a network error: {str(e)}"
    except KeyError as e:
        return f"Unable to find AQI data for this location."


def get_weather_data(location, category, days_requested):
    if location.lower() == "delhi":
        location = "New Delhi"

    days_to_fetch = min(days_requested, 10)
    api_url = (
        f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={location}&aqi={'yes' if category == 'aqi' else 'no'}"
        if category in ["current", "aqi"]
        else f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={location}&days={days_to_fetch}&aqi=no&alerts=no"
    )

    try:
        response = requests.get(api_url)
        data = response.json()
        if response.status_code != 200 or 'error' in data:
            error_message = data.get('error', {}).get(
                'message', 'Unknown error occurred')
            return f"Error fetching weather data: {error_message}"
        if 'location' not in data:
            return "Error: Unable to retrieve location information."

        location_info = f"{data['location']['name'].title()}, {data['location']['region']}, {data['location']['country']}"

        if category == "current":
            curr = data['current']
            return f"Current weather in {location_info} (as of {data['location']['localtime']}):\n--• {curr['condition']['text']}\n\n--• Temp: {curr['temp_c']}°C\n--• Feels like: {curr['feelslike_c']}°C\n--• Humidity: {curr['humidity']}%\n--• Wind: {curr['wind_kph']} kph\n--• Precipitation: {curr['precip_mm']} mm"
        elif category == "specific":
            forecast = data['forecast']['forecastday'][min(
                days_requested - 1, len(data['forecast']['forecastday']) - 1)]
            return f"Forecast for {location_info} on {forecast['date']}:\n--• {forecast['day']['condition']['text']}\n--• Max Temp: {forecast['day']['maxtemp_c']}°C\n--• Min Temp: {forecast['day']['mintemp_c']}°C\n--• Chance of Rain: {forecast['day'].get('daily_chance_of_rain', 0)}%"
        elif category == "multiple":
            forecast_summary = f"Multi-day forecast for {location_info}:"
            for day in data['forecast']['forecastday']:
                forecast_summary += f"\n--• Date: {day['date']} - {day['day']['condition']['text']} - Max: {day['day']['maxtemp_c']}°C - Min: {day['day']['mintemp_c']}°C - Rain: {day['day'].get('daily_chance_of_rain', 0)}%\n"
            return forecast_summary.strip()
        elif category == "aqi":
            aq = data['current']['air_quality']
            aqi_index, status = calc_aqi(data['location']['name'])
            return f"AQI for {location_info}:\n--• AQI Index: {aqi_index}\n--• Status: {status}\n--• PM 2.5: {aq['pm2_5']}\n--• PM 10: {aq['pm10']}\n--• CO: {aq['co']}\n--• NO₂: {aq['no2']}\n--• O₃: {aq['o3']}\n--• SO₂: {aq['so2']}"
    except requests.exceptions.RequestException as e:
        return f"Unable to fetch weather data due to a network error: {str(e)}"
    except KeyError as e:
        return f"Unable to find weather data for this location."


person, chatbot = Image.open(
    'assets/person.png'), Image.open('assets/chatbot.png')

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": welcome_message}]

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=person if message["role"] == "user" else chatbot):
        st.markdown(message["content"])


def get_best_match(prompt, category_list, threshold=75):
    match, score = process.extractOne(
        prompt.lower(), category_list, scorer=fuzz.ratio)
    return match if score >= threshold else None


if prompt := st.chat_input("Ask me about the weather!"):
    with st.chat_message("user", avatar=person):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    user_query_type = classify_text(prompt)

    if user_query_type == "weather":
        location, category, days_requested = parse_query(prompt)
        assistant_response = get_weather_data(
            location, category, days_requested) if location != "unknown location" else "Please specify a location."
    else:
        # Fuzzy matching for small talk
        if get_best_match(prompt, greetings):
            assistant_response = secrets.choice(greeting_responses) 
            assistant_response = secrets.choice(greeting_responses) 
        elif get_best_match(prompt, general_queries):
            assistant_response = secrets.choice(general_query_responses)
            assistant_response = secrets.choice(general_query_responses)
        elif get_best_match(prompt, thanks_phrases):
            assistant_response = secrets.choice(thanks_responses)
            assistant_response = secrets.choice(thanks_responses)
        elif get_best_match(prompt, farewells):
            assistant_response = secrets.choice(farewell_responses)
            assistant_response = secrets.choice(farewell_responses)
        else:
            assistant_response = "I'm here to help! Ask me anything about the weather."

    with st.chat_message("assistant", avatar=chatbot):
        message_placeholder = st.empty()
        full_response = ""
        for chunk in assistant_response.split("--"):
            for char in chunk:  # Iterate through each character in the chunk
                full_response += char
                message_placeholder.markdown(full_response + "▌")
                time.sleep(0.01)  # Adjust delay for typewriter effect
            full_response += "\n "  # Add a newline after each chunk
        message_placeholder.markdown(full_response)
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response})
