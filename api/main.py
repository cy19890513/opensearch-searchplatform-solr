"""FastAPI search service entrypoint."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import config
from api.client import get_client
from api.search import router as search_router

app = FastAPI(title="Product Search API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(search_router)


@app.get("/health")
def health():
    client = get_client()
    info = client.info()
    return {
        "status": "ok",
        "cluster": info.get("cluster_name"),
        "version": info.get("version", {}).get("number"),
        "index": config.INDEX,
    }
