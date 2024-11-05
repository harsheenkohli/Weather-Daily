import streamlit as st
import requests
import time
import re

st.set_page_config(
    page_title="Weather Daily",
    page_icon="./assets/logo.png"
)

st.title("Weather Daily")

# Function to parse user input for location and type of request


def parse_query(user_query):
    location = None
    category = "current"  # Default to current weather
    days_requested = 1    # Default to 1 day for single-day forecasts

    user_query = user_query.lower()

    # Adding a prefix if not present
    if "weather in" not in user_query:
        user_query = "weather in " + user_query

    # Determine category of forecast
    if "tomorrow" in user_query:
        category = "specific"
        days_requested = 1
    elif "after" in user_query:
        days_match = re.search(r"after (\d+) days?", user_query)
        if days_match:
            category = "specific"
            days_requested = int(days_match.group(1))
    elif "for" in user_query:
        days_match = re.search(r"for (\d+) days?", user_query)
        if days_match:
            category = "multiple"
            days_requested = int(days_match.group(1))
    elif "in" in user_query:
        days_match = re.search(r"in (\d+) days?", user_query)
        if days_match:
            category = "multiple"
            days_requested = int(days_match.group(1))
    elif "this week" in user_query:
        category = "multiple"
        days_requested = 7

    # Extract the location
    location_match = re.search(r"weather in (.+)", user_query)
    if location_match:
        location = location_match.group(1).strip()
    else:
        location = "unknown location"

    return location, category, days_requested

# Function to get weather data based on category


def get_weather_data(location, category, days_requested):
    if location.lower() == "delhi":
        location = "New Delhi"
    api_key = "ff77f4dadf90414895e164755240511"  # Replace with your API key

    if category == "current":  # Current weather
        api_url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={location}&aqi=no"
    else:  # Future weather forecast (specific or multiple days)
        days_to_fetch = min(days_requested, 10)  # Cap at 10 days
        api_url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={location}&days={days_to_fetch}&aqi=no&alerts=no"

    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        if category == "current":
            # Extract current weather data
            location_name = data['location']['name']
            region = data['location']['region']
            country = data['location']['country']
            temp_celsius = data['current']['temp_c']
            feels_like = data['current']['feelslike_c']
            condition = data['current']['condition']['text']
            humidity = data['current']['humidity']
            wind_speed_kph = data['current']['wind_kph']
            precipitation = data['current']['precip_mm']
            local_time = data['location']['localtime']

            return (f"The current weather in {location_name.title()}, {region}, {country} (as of {local_time}):\n"
                    f"- Condition: {condition}\n"
                    f"- Temperature: {temp_celsius}°C\n"
                    f"- Feels like: {feels_like}°C\n"
                    f"- Humidity: {humidity}%\n"
                    f"- Wind Speed: {wind_speed_kph} kph\n"
                    f"- Precipitation: {precipitation} mm")

        elif category == "specific":
            # Extract forecast for a specific future day
            forecast_day = data['forecast']['forecastday'][-1]
            region = data['location']['region']
            country = data['location']['country']
            date = forecast_day['date']
            condition = forecast_day['day']['condition']['text']
            max_temp = forecast_day['day']['maxtemp_c']
            min_temp = forecast_day['day']['mintemp_c']
            chance_of_rain = forecast_day['day'].get('daily_chance_of_rain', 0)

            return (f"Weather forecast for {location.title()}, {region}, {country} on {date}:\n"
                    f"- Condition: {condition}\n"
                    f"- Max Temperature: {max_temp}°C\n"
                    f"- Min Temperature: {min_temp}°C\n"
                    f"- Chance of Rain: {chance_of_rain}%")

        elif category == "multiple":
            # Extract multi-day forecast data
            forecast_days = data['forecast']['forecastday']
            region = data['location']['region']
            country = data['location']['country']
            forecast_summary = f"Weather forecast for {location.title()}, {region}, {country}: \n\n"

            for day in forecast_days:
                date = day['date']
                condition = day['day']['condition']['text']
                max_temp = day['day']['maxtemp_c']
                min_temp = day['day']['mintemp_c']
                chance_of_rain = day['day'].get('daily_chance_of_rain', 0)
                forecast_summary += (f"Date: {date}\n"
                                     f"- Condition: {condition}\n"
                                     f"- Max Temperature: {max_temp}°C\n"
                                     f"- Min Temperature: {min_temp}°C\n"
                                     f"- Chance of Rain: {chance_of_rain}%\n\n")

            return forecast_summary.strip()

    except requests.exceptions.RequestException:
        return "I'm unable to fetch live weather data right now. Please check a weather app for the latest information."


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask me about the weather!"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Parse user query for location and day
    location, category, days_requested = parse_query(prompt)

    # Fetch and display assistant's response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        # Get response based on parsed data
        if location == "unknown location":
            assistant_response = "Please specify a location."
        else:
            assistant_response = get_weather_data(
                location, category, days_requested)

        # Simulate typing effect
        for chunk in assistant_response.split():
            full_response += chunk + " "
            time.sleep(0.05)
            message_placeholder.markdown(full_response + "▌")

        message_placeholder.markdown(full_response)
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response})
