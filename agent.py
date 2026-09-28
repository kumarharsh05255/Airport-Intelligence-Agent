import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_groq import ChatGroq

from prompts import SYSTEM_PROMPT
from tools.airport_news import airport_news
from tools.current_datetime import current_datetime
from tools.flight_status import flight_status
from tools.hotel_search import hotel_search
from tools.weather import weather
from tools.web_search import web_search


load_dotenv()


llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY"),
)

tools = [
    flight_status,
    weather,
    airport_news,
    web_search,
    hotel_search,
    current_datetime,
]


agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=SYSTEM_PROMPT,
)


def run_agent_with_sources(query: str) -> dict:
    """Run the agent and return the answer with the tools it used."""

    response = agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": query,
            }
        ]
    })

    messages = response["messages"]

    tool_names = []

    for message in messages:
        if message.type == "tool":
            tool_name = getattr(message, "name", None)

            if tool_name and tool_name not in tool_names:
                tool_names.append(tool_name)

    if tool_names:
        sources = tool_names
    else:
        sources = ["Agent's general knowledge"]

    return {
        "answer": messages[-1].content,
        "sources": sources,
    }