import requests
import streamlit as st
import secrets
from error_texts import *

api_key = st.secrets['API_KEY']
aqi_key = st.secrets['AQI_KEY']

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
        secrets.choice(request_exception_responses)
        return secrets.choice(request_exception_responses) + " 😔"
    except KeyError as e:
        secrets.choice(key_error_responses)
        return secrets.choice(key_error_responses) + " 😐"


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
            return f"Error fetching weather data. My apolie"
        if 'location' not in data:
            return "Error: Unable to retrieve location information."
        
        if data['location']['name'].title() == "Athens Eleftherios Venizelos International Airport":
            raise KeyError
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
        secrets.choice(request_exception_responses)
        return secrets.choice(request_exception_responses) + " 😔"
    except KeyError as e:
        secrets.choice(key_error_responses)
        return secrets.choice(key_error_responses) + " 😐"