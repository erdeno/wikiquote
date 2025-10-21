from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Wikiquote Autocomplete API")

# Connect to Elasticsearch
ES_URI = os.getenv("ES_URI", "http://localhost:9200")
INDEX_NAME = "wikiquote"

es = Elasticsearch(ES_URI)

@app.get("/autocomplete")
def autocomplete(text: str = Query(..., min_length=2, description="Text to search for")):
    """
    Search for quotes matching a given text query.
    """
    try:
        response = es.search(
            index=INDEX_NAME,
            body={
                "query": {
                    "multi_match": {
                        "query": text,
                        "fields": ["quote^3", "author"],
                        "fuzziness": "AUTO"
                    }
                },
                "size": 5,
                "_source": ["quote", "author"]
            }
        )

        results = [
            {
                "quote": hit["_source"]["quote"],
                "author": hit["_source"]["author"],
                "score": hit["_score"]
            }
            for hit in response["hits"]["hits"]
        ]

        return JSONResponse(content={"matches": results})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/")
def root():
    return {"message": "Wikiquote Autocomplete API is running 🚀"}

