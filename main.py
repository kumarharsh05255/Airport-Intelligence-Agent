from fastapi import FastAPI
from pydantic import BaseModel

from agent import run_agent_with_sources


app = FastAPI(
    title="AI Airport Intelligence Agent",
    description="API for the AI Airport Intelligence and Assistance Agent",
    version="1.0.0",
)


class QueryRequest(BaseModel):
    query: str


@app.get("/")
def root():
    return {
        "message": "AI Airport Intelligence Agent API is running."
    }


@app.post("/ask")
def ask_agent(request: QueryRequest):
    return run_agent_with_sources(request.query)