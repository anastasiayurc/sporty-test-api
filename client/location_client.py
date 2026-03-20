"""
Location Client — endpoint methods for the Zippopotam location API.
Each method maps to one API endpoint. No HTTP logic lives here.
"""

import requests
from .base_client import BaseClient


class LocationClient(BaseClient):
    def __init__(self, settings=None):
        super().__init__(settings)

    def get_location(self, country_code: str, zip_code: str) -> requests.Response:
        """Fetch location data by country code and zip code."""
        return self.get(f"/{country_code}/{zip_code}")
