import secrets
import streamlit as st
import time
from small_talk import *
from PIL import Image
import joblib
from fuzzywuzzy import fuzz, process
from query_parser import parse_query
from weather_forecaster import get_weather_data

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
    

welcome_message = secrets.choice(welcome_messages)
model = joblib.load('./assets/svm_model.joblib')


def classify_text(user_input):
    prediction = model.predict([user_input])[0]
    return prediction


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
