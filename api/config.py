"""Centralized configuration, overridable via environment variables."""
import os

OS_HOST = os.getenv("OS_HOST", "localhost")
OS_PORT = int(os.getenv("OS_PORT", "9200"))
OS_USER = os.getenv("OS_USER", "admin")
OS_PASS = os.getenv("OS_PASS", "SearchDemo123!")
INDEX = os.getenv("OS_INDEX", "products")
