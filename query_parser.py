import re
import streamlit as st
import nltk
from nltk.corpus import stopwords
import pandas as pd
from fuzzywuzzy import fuzz, process

nltk.download('stopwords')

stop_words = set(stopwords.words('english'))

api_key = st.secrets['API_KEY']

cities_df = pd.read_csv('./assets/world-cities.csv')
city_names = set(cities_df["name"].str.lower())


def remove_stopwords_nltk(query):
    filtered_query = " ".join(
        word for word in query.split() if word.lower() not in stop_words)
    return filtered_query


def parse_query(user_query):
    location, category, days_requested = None, "current", 1
    user_query = user_query.lower()

    # Handle AQI requests
    if "aqi" in user_query:
        category = "aqi"

    # Handle specific or multiple days forecast
    elif "tomorrow" in user_query:
        category, days_requested = "specific", 2
    elif days_match := re.search(r"(after|for|in) (\d+) days?", user_query):
        days_requested = int(days_match[2]) + 1
        category = "specific" if days_match[1] == "after" else "multiple"
    elif "this week" in user_query:
        category, days_requested = "multiple", 7

    # Remove stopwords from the query
    query = remove_stopwords_nltk(user_query)

    # Extract location using fuzzy matching
    location = find_location_in_query(query, city_names) or "unknown location"
    return location, category, days_requested


def find_location_in_query(query, city_names, threshold=90):
    query_words = query.split()
    # Direct match for efficiency
    for word in query_words:
        if word.lower() in city_names:
            return word.title()

    # Fuzzy match for more flexible search
    match, score = process.extractOne(
        query.lower(), city_names, scorer=fuzz.partial_ratio)
    if score >= threshold:
        return match.title()

    return None
