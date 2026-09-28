import os

import requests
from dotenv import load_dotenv
from langchain.tools import tool


load_dotenv()

API_KEY = os.getenv("AVIATIONSTACK_API_KEY")
BASE_URL = "https://api.aviationstack.com/v1"


@tool
def flight_status(airport_code: str) -> dict:
    """Get current flight information for departures from an airport."""

    if not API_KEY:
        return {"error": "AVIATIONSTACK_API_KEY is not configured."}

    airport_code = airport_code.strip().upper()

    if not airport_code:
        return {"error": "Airport code is required."}

    params = {
        "access_key": API_KEY,
        "dep_iata": airport_code,
        "limit": 20
    }

    try:
        response = requests.get(
            f"{BASE_URL}/flights",
            params=params,
            timeout=15
        )

        response.raise_for_status()
        data = response.json()

        if "error" in data:
            return {"error": data["error"]}

        flights = []

        for flight in data.get("data", []):
            departure = flight.get("departure", {})
            arrival = flight.get("arrival", {})
            airline = flight.get("airline", {})
            flight_info = flight.get("flight", {})

            flights.append({
                "flight_number": flight_info.get("iata"),
                "airline": airline.get("name"),
                "departure_airport": departure.get("airport"),
                "departure_time": departure.get("scheduled"),
                "departure_estimated": departure.get("estimated"),
                "departure_actual": departure.get("actual"),
                "departure_delay_minutes": departure.get("delay"),
                "departure_terminal": departure.get("terminal"),
                "departure_gate": departure.get("gate"),
                "arrival_airport": arrival.get("airport"),
                "arrival_time": arrival.get("scheduled"),
                "arrival_estimated": arrival.get("estimated"),
                "arrival_delay_minutes": arrival.get("delay"),
                "status": flight.get("flight_status")
            })

        return {
            "airport": airport_code,
            "flight_count": len(flights),
            "flights": flights
        }

    except requests.RequestException as e:
        return {
            "error": f"Flight API request failed: {str(e)}"
        }

    except Exception as e:
        return {
            "error": f"Unexpected error: {str(e)}"
        }