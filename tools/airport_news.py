import os

import requests
from dotenv import load_dotenv
from langchain.tools import tool


load_dotenv()

API_KEY = os.getenv("NEWSAPI_KEY")
BASE_URL = "https://newsapi.org/v2/everything"


@tool
def airport_news(airport_code: str) -> dict:
    """Get recent news related to an airport."""

    if not API_KEY:
        return {"error": "NEWSAPI_KEY is not configured."}

    airport_code = airport_code.strip().upper()

    if not airport_code:
        return {"error": "Airport code is required."}

    airport_names = {
        "DEL": "Indira Gandhi International Airport Delhi",
        "BOM": "Chhatrapati Shivaji Maharaj International Airport Mumbai",
        "BLR": "Kempegowda International Airport Bengaluru",
        "HYD": "Rajiv Gandhi International Airport Hyderabad",
        "MAA": "Chennai International Airport",
        "CCU": "Netaji Subhas Chandra Bose International Airport Kolkata",
        "COK": "Cochin International Airport Kochi",
        "AMD": "Sardar Vallabhbhai Patel International Airport Ahmedabad",
        "PNQ": "Pune International Airport",
        "GOI": "Manohar International Airport Goa",
        "JAI": "Jaipur International Airport",
        "LKO": "Chaudhary Charan Singh International Airport Lucknow",
        "IXC": "Chandigarh International Airport",
        "SXR": "Sheikh ul-Alam International Airport Srinagar",
        "PAT": "Jay Prakash Narayan International Airport Patna",
        "GAU": "Lokpriya Gopinath Bordoloi International Airport Guwahati",
        "VNS": "Lal Bahadur Shastri International Airport Varanasi",
        "TRV": "Trivandrum International Airport",
        "IXB": "Bagdogra Airport",
        "BBI": "Biju Patnaik International Airport Bhubaneswar",
    }

    airport_name = airport_names.get(airport_code)

    if not airport_name:
        return {
            "error": f"Airport code '{airport_code}' is not supported."
        }

    params = {
        "q": f'"{airport_name}"',
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 10,
        "apiKey": API_KEY,
    }

    try:
        response = requests.get(
            BASE_URL,
            params=params,
            timeout=15
        )

        response.raise_for_status()
        data = response.json()

        if data.get("status") != "ok":
            return {
                "error": data.get("message", "News API request failed.")
            }

        articles = []

        for article in data.get("articles", []):
            articles.append({
                "title": article.get("title"),
                "description": article.get("description"),
                "source": article.get("source", {}).get("name"),
                "published_at": article.get("publishedAt"),
                "url": article.get("url"),
            })

        return {
            "airport": airport_code,
            "airport_name": airport_name,
            "article_count": len(articles),
            "articles": articles,
        }

    except requests.RequestException as e:
        return {
            "error": f"News API request failed: {str(e)}"
        }

    except Exception as e:
        return {
            "error": f"Unexpected error: {str(e)}"
        }