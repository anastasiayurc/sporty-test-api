"""
Base HTTP client — session management, base URL, and shared headers.
All endpoint clients inherit from this class.
"""

import logging
import requests

from config.settings import settings as _default_settings

logger = logging.getLogger(__name__)


class BaseClient:
    def __init__(self, settings=None):
        s = settings or _default_settings
        self.base_url = s.api_base_url
        self.timeout = s.api_timeout
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def get(self, path: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}{path}"
        logger.info(f"GET {url}")
        response = self.session.get(url, timeout=self.timeout, **kwargs)
        logger.info(f"Response: {response.status_code}")
        return response
