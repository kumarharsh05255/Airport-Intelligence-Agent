import json
import os

import requests
from dotenv import load_dotenv
from langchain.tools import tool


load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


@tool
def weather(airport_code: str) -> dict:
    """Get current weather conditions for an airport."""

    if not API_KEY:
        return {"error": "OPENWEATHER_API_KEY is not configured."}

    airport_code = airport_code.strip().upper()

    if not airport_code:
        return {"error": "Airport code is required."}

    try:
        with open("airports.json", "r", encoding="utf-8") as file:
            airports = json.load(file)

        # Support airports.json stored as either a list or dictionary.
        if isinstance(airports, list):
            airport = next(
                (
                    item for item in airports
                    if item.get("iata") == airport_code
                    or item.get("code") == airport_code
                ),
                None
            )
        else:
            airport = airports.get(airport_code)

        if not airport:
            return {"error": f"Airport code '{airport_code}' not found."}

        latitude = airport.get("latitude")
        longitude = airport.get("longitude")

        if latitude is None or longitude is None:
            return {
                "error": f"Coordinates not found for airport '{airport_code}'."
            }

        params = {
            "lat": latitude,
            "lon": longitude,
            "appid": API_KEY,
            "units": "metric"
        }

        response = requests.get(
            BASE_URL,
            params=params,
            timeout=15
        )

        response.raise_for_status()
        data = response.json()

        weather_data = data.get("weather", [{}])[0]
        main = data.get("main", {})
        wind = data.get("wind", {})

        return {
            "airport": airport_code,
            "airport_name": airport.get("name"),
            "location": airport.get("city"),
            "temperature_celsius": main.get("temp"),
            "feels_like_celsius": main.get("feels_like"),
            "humidity_percent": main.get("humidity"),
            "pressure_hpa": main.get("pressure"),
            "weather": weather_data.get("description"),
            "visibility_meters": data.get("visibility"),
            "wind_speed_mps": wind.get("speed"),
            "wind_direction_degrees": wind.get("deg")
        }

    except FileNotFoundError:
        return {"error": "airports.json was not found."}

    except requests.RequestException as e:
        return {
            "error": f"Weather API request failed: {str(e)}"
        }

    except Exception as e:
        return {
            "error": f"Unexpected error: {str(e)}"
        }