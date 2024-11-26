import re
import streamlit as st

api_key = st.secrets['API_KEY']


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