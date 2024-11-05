import streamlit as st
import requests
import time
import re

# Title for the Streamlit web app
st.set_page_config(
    page_title="Weather Daily",
    page_icon="./assets/logo.png"  # You can also use an emoji or provide a URL or local path to an icon file
)

# st.title("Weather Daily")
st.markdown(
    """
    <div style="display: flex; align-items: center;">
        <img src="./assets/logo.png" width="40" style="margin-right: 10px;">
        <h1 style="display: inline;">Weather Daily</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# Function to parse user input for location and day
def parse_query(user_query):
    location = None
    day = 0  # Default to current day
    user_query = user_query.lower()

    # Adding a prefix if not present
    if "weather in" not in user_query:
        user_query = "weather in " + user_query

    # Determine day requested
    if "tomorrow" in user_query:
        day = 1
    elif "after" in user_query:
        days_match = re.search(r"after (\d+) days?", user_query)
        if days_match:
            day = int(days_match.group(1))

    # Extract the location
    location_match = re.search(r"weather in (.+)", user_query)
    if location_match:
        location = location_match.group(1).strip()
    else:
        location = "unknown location"

    return location, day

# Function to get weather data


def get_weather_data(location, day):
    if location.lower() == "delhi":
        location = "New Delhi"
    api_key = "ff77f4dadf90414895e164755240511"  # Replace with your API key
    if day == 0:  # Current weather
        api_url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={location}&aqi=no"
    else:  # Future weather forecast
        api_url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={location}&days={day+1}&aqi=no&alerts=no"

    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()

        if day == 0:
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

        else:
            # Extract future weather forecast data
            forecast = data['forecast']['forecastday'][-1]
            forecast_date = forecast['date']
            max_temp = forecast['day']['maxtemp_c']
            min_temp = forecast['day']['mintemp_c']
            condition = forecast['day']['condition']['text']
            chance_of_rain = forecast['day']['daily_chance_of_rain']

            return (f"Weather forecast for {location.title()}, on {forecast_date}:\n"
                    f"- Condition: {condition}\n"
                    f"- Max Temperature: {max_temp}°C\n"
                    f"- Min Temperature: {min_temp}°C\n"
                    f"- Chance of Rain: {chance_of_rain}%")

    except requests.exceptions.RequestException as e:
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
    location, day = parse_query(prompt)

    # Fetch and display assistant's response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        # Get response based on parsed data
        if location == "unknown location":
            assistant_response = "Please specify a location."
        else:
            assistant_response = get_weather_data(location, day)

        # Simulate typing effect
        for chunk in assistant_response.split():
            full_response += chunk + " "
            time.sleep(0.05)
            message_placeholder.markdown(full_response + "▌")

        message_placeholder.markdown(full_response)
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response})
