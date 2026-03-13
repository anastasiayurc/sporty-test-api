"""
API Client — reusable HTTP methods.
All direct requests.get() calls live here, not in test files.
"""

import requests
import logging

logger = logging.getLogger(__name__)

BASE_URL = "http://api.zippopotam.us"
TIMEOUT  = 10


def get_location(country_code: str, zip_code: str) -> requests.Response:
    """Send GET request to fetch location data by country and zip code."""
    url = f"{BASE_URL}/{country_code}/{zip_code}"
    logger.info(f"Sending GET request to: {url}")
    response = requests.get(url, timeout=TIMEOUT)
    logger.info(f"Response Status Code: {response.status_code}")
    return response
