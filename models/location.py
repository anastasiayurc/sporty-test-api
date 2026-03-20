"""
Location response models — parse and validate the Zippopotam API response.
Tests assert on these typed objects, never on raw dicts.
Schema changes are caught here in one place, not scattered across assertions.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List

import requests


@dataclass
class Place:
    place_name: str
    state: str
    state_abbreviation: str
    latitude: str
    longitude: str

    @classmethod
    def from_dict(cls, d: dict) -> Place:
        return cls(
            place_name=d["place name"],
            state=d.get("state", ""),
            state_abbreviation=d.get("state abbreviation", ""),
            latitude=d.get("latitude", ""),
            longitude=d.get("longitude", ""),
        )


@dataclass
class LocationResponse:
    post_code: str
    country: str
    country_abbreviation: str
    places: List[Place]

    @classmethod
    def from_response(cls, response: requests.Response) -> LocationResponse:
        data = response.json()
        return cls(
            post_code=data["post code"],
            country=data["country"],
            country_abbreviation=data["country abbreviation"],
            places=[Place.from_dict(p) for p in data["places"]],
        )
