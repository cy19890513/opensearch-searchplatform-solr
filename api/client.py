"""Shared OpenSearch client (singleton)."""
from opensearchpy import OpenSearch

from api import config

_client = None


def get_client() -> OpenSearch:
    global _client
    if _client is None:
        _client = OpenSearch(
            hosts=[{"host": config.OS_HOST, "port": config.OS_PORT, "scheme": "https"}],
            http_auth=(config.OS_USER, config.OS_PASS),
            verify_certs=False,
            ssl_show_warn=False,
        )
    return _client
