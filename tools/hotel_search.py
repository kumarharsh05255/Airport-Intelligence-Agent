import os

import requests
from dotenv import load_dotenv
from langchain.tools import tool


load_dotenv()

API_KEY = os.getenv("STAYINGAPI_KEY")
BASE_URL = "https://api.stayingapi.com/v1/search"


@tool
def hotel_search(
    location: str,
    check_in: str,
    check_out: str,
    adults: int = 1
) -> dict:
    """Search for hotels near an airport or location."""

    if not API_KEY:
        return {"error": "STAYINGAPI_KEY is not configured."}

    location = location.strip()

    if not location:
        return {"error": "Location is required."}

    if not check_in or not check_out:
        return {
            "error": "Check-in and check-out dates are required."
        }

    params = {
        "location": location,
        "checkIn": check_in,
        "checkOut": check_out,
        "adults": adults,
        "platforms": "booking",
        "limit": 5,
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    try:
        response = requests.get(
            BASE_URL,
            params=params,
            headers=headers,
            timeout=20
        )

        response.raise_for_status()
        data = response.json()

        hotels = []

        for hotel in data.get("data", []):
            location_data = hotel.get("location", {})
            price = hotel.get("price", {})

            hotels.append({
                "name": hotel.get("name"),
                "property_type": hotel.get("propertyType"),
                "city": location_data.get("city"),
                "rating": hotel.get("guestRating"),
                "rating_scale": hotel.get("ratingScale"),
                "star_rating": hotel.get("starRating"),
                "review_count": hotel.get("reviewCount"),
                "nightly_price": price.get("nightlyPrice"),
                "total_price": price.get("totalPrice"),
                "currency": price.get("currency"),
                "url": hotel.get("url"),
            })

        return {
            "location": location,
            "check_in": check_in,
            "check_out": check_out,
            "hotel_count": len(hotels),
            "hotels": hotels,
        }

    except requests.RequestException as e:
        return {
            "error": f"Hotel API request failed: {str(e)}"
        }

    except Exception as e:
        return {
            "error": f"Unexpected error: {str(e)}"
        }