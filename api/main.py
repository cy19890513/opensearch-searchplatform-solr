"""FastAPI search service entrypoint."""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api import config
from api.client import get_client
from api.search import router as search_router
from api.suggest import router as suggest_router
from api.similar import router as similar_router
from api.hybrid import router as hybrid_router

app = FastAPI(title="Product Search API", version="0.4.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(search_router)
app.include_router(suggest_router)
app.include_router(similar_router)
app.include_router(hybrid_router)

UI_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ui")
if os.path.isdir(UI_DIR):
    app.mount("/ui", StaticFiles(directory=UI_DIR, html=True), name="ui")


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
