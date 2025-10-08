# services/autocomplete/app.py
from fastapi import FastAPI

app = FastAPI(title="Autocomplete Service")

@app.get("/")
def healthcheck():
    return {"status": "ok", "service": "autocomplete"}

@app.get("/autocomplete")
def autocomplete(q: str):
    # Placeholder logic – will connect to Elasticsearch later
    return {
        "query": q,
        "results": [
            {"quote": "The only limit to our realization of tomorrow is our doubts of today.", "author": "Franklin D. Roosevelt"},
            {"quote": "To be or not to be, that is the question.", "author": "William Shakespeare"}
        ]
    }

