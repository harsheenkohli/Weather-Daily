# 1. Importing necessary libraries
import streamlit as st  # Import the Streamlit library
import random  # Import the random library
import time  # Import the time library
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import requests

# 2. Creating a title for our Streamlit web application
st.title("Weather Chatbot")  # Set the title of the web application

# 3. Sample weather-related questions and responses for retrieval
data = {
    "What is the weather like today?": "I can't fetch live data, but you can check your local weather app.",
    "Will it rain today?": "I don't have real-time data, but if it looks cloudy, there might be a chance!",
    "What’s the temperature outside?": "I'm not connected to live data, but usually checking a weather app can help.",
    "Should I carry an umbrella?": "If it looks rainy, an umbrella might be a good idea!",
    "What is the weather forecast for tomorrow?": "I can't provide live forecasts, but checking online or an app is a great idea!",
}

# Prepare the dataset
questions = list(data.keys())
responses = list(data.values())


# Define the function to find the closest match
def get_response(user_query):

    # Check if the query requires real-time weather data
    # if any(keyword in user_query.lower() for keyword in ["weather", "temperature", "rain", "forecast"]):
    if True:
        # Assuming you have the user's location or a default location
        user_location =  user_query # Replace with actual location or user input

        # Construct the API URL with your API key and user's location
        api_url = f"http://api.weatherapi.com/v1/current.json?key=ff77f4dadf90414895e164755240511&q={user_location}&aqi=no"

        try:
            response = requests.get(api_url)
            response.raise_for_status()  # Raise an exception for error HTTP statuses
            data = response.json()

            # Extract relevant weather information from the new JSON structure
            location_name = data['location']['name']
            region = data['location']['region']
            country = data['location']['country']
            local_time = data['location']['localtime']
            temp_celsius = data['current']['temp_c']
            weather_condition = data['current']['condition']['text']
            wind_speed_kph = data['current']['wind_kph']
            humidity = data['current']['humidity']
            feels_like_celsius = data['current']['feelslike_c']
            visibility_km = data['current']['vis_km']

            # Construct a response using the extracted data
            return (
                f"The current weather in {location_name}, {region}, {country} (as of {local_time}):\n"
                f"- Condition: {weather_condition}\n"
                f"- Temperature: {temp_celsius}°C (feels like {feels_like_celsius}°C)\n"
                f"- Wind Speed: {wind_speed_kph} kph\n"
                f"- Humidity: {humidity}%\n"
                f"- Visibility: {visibility_km} km"
            )

        except requests.exceptions.RequestException:
            # Return a fallback response in case of an API error
            return "I'm unable to fetch live weather data right now. Please check a weather app for the latest information."
    else:
        return "I'm not sure about that. Can you ask something else related to weather?"

# 4. Initializing the chat history in the session state (how the chatbot tracks things)
if "messages" not in st.session_state:  # Check if "messages" exists in session state
    st.session_state.messages = []  # Initialize "messages" as an empty list

# 5. Displaying the existing chat messages from the user and the chatbot
for message in st.session_state.messages:  # For every message in the chat history
    with st.chat_message(message["role"]):  # Create a chat message box
        st.markdown(message["content"])  # Display the content of the message

# 6. Accepting the user input and adding it to the message history
if prompt := st.chat_input("Ask me about the weather!"):  # If user enters a message
    with st.chat_message("user"):  # Display user's message in a chat message box
        st.markdown(prompt)  # Display the user's message
    st.session_state.messages.append({"role": "user", "content": prompt})  # Add user's message to chat history

    # 7. Generating and displaying the assistant's response
    with st.chat_message("assistant"):  # Create a chat message box for the assistant's response
        message_placeholder = st.empty()  # Create an empty placeholder for the assistant's message
        full_response = ""  # Initialize an empty string for the full response
        
        # Generate the assistant's response based on the retrieval system
        assistant_response = get_response(prompt)
        
        # Simulate "typing" effect by gradually revealing the response
        for chunk in assistant_response.split():  # For each word in the response
            full_response += chunk + " "
            time.sleep(0.05)  # Small delay between each word
            message_placeholder.markdown(full_response + "▌")  # Update placeholder with current full response and a blinking cursor

        message_placeholder.markdown(full_response)  # Remove cursor and display full response
        st.session_state.messages.append({"role": "assistant", "content": full_response})  # Add assistant's response to chat history
