import os

from dotenv import load_dotenv
from langchain.tools import tool
from tavily import TavilyClient


load_dotenv()

API_KEY = os.getenv("TAVILY_API_KEY")


@tool
def web_search(query: str) -> dict:
    """Search the web for current airport-related information."""

    if not API_KEY:
        return {"error": "TAVILY_API_KEY is not configured."}

    query = query.strip()

    if not query:
        return {"error": "Search query is required."}

    try:
        client = TavilyClient(api_key=API_KEY)

        response = client.search(
            query=query,
            search_depth="basic",
            max_results=5
        )

        results = []

        for result in response.get("results", []):
            results.append({
                "title": result.get("title"),
                "url": result.get("url"),
                "content": result.get("content"),
            })

        return {
            "query": query,
            "result_count": len(results),
            "results": results,
        }

    except Exception as e:
        return {
            "error": f"Web search failed: {str(e)}"
        }