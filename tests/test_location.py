"""
Location endpoint tests.

Design principles:
  - One assertion per test function (Single Responsibility)
  - Test classes group tests by concern, not by test case
  - response_cache fixture ensures each unique (country, zip) is fetched once
  - Test data lives exclusively in data/location_data.py
"""

import pytest
import logging

from models.location import LocationResponse
from data.location_data import HAPPY_CASES, NEGATIVE_CASES

logger = logging.getLogger(__name__)


def _params(cases: list) -> list:
    """Build a pytest.param list from a test-case dict list, preserving id and marks."""
    return [
        pytest.param(
            tc,
            id=tc["id"],
            marks=[getattr(pytest.mark, m) for m in tc.get("marks", [])],
        )
        for tc in cases
    ]


# ---------------------------------------------------------------------------
# Happy path — valid inputs → 200
# ---------------------------------------------------------------------------

class TestLocationHappyPath:
    """Validates status, content, schema, and headers for known-good inputs."""

    @pytest.mark.parametrize("tc", _params(HAPPY_CASES))
    def test_status_code_is_200(self, response_cache, tc):
        response = response_cache(tc["country_code"], tc["zip_code"])
        logger.info(f"[{tc['id']}] status={response.status_code}")
        assert response.status_code == 200, (
            f"Expected 200 but got {response.status_code} "
            f"for {tc['country_code']}/{tc['zip_code']}"
        )

    @pytest.mark.parametrize("tc", _params(HAPPY_CASES))
    def test_place_name(self, response_cache, tc):
        location = LocationResponse.from_response(response_cache(tc["country_code"], tc["zip_code"]))
        actual = location.places[0].place_name
        logger.info(f"[{tc['id']}] place='{actual}'")
        assert actual == tc["expected_place"], (
            f"Expected place '{tc['expected_place']}' but got '{actual}'"
        )

    @pytest.mark.parametrize("tc", _params(HAPPY_CASES))
    def test_post_code_echoed_in_response(self, response_cache, tc):
        location = LocationResponse.from_response(response_cache(tc["country_code"], tc["zip_code"]))
        logger.info(f"[{tc['id']}] post_code='{location.post_code}'")
        assert location.post_code == tc["zip_code"], (
            f"Response post code '{location.post_code}' "
            f"does not match requested zip '{tc['zip_code']}'"
        )

    @pytest.mark.parametrize("tc", _params(HAPPY_CASES))
    def test_country_name(self, response_cache, tc):
        location = LocationResponse.from_response(response_cache(tc["country_code"], tc["zip_code"]))
        logger.info(f"[{tc['id']}] country='{location.country}'")
        assert location.country == tc["expected_country"], (
            f"Expected country '{tc['expected_country']}' but got '{location.country}'"
        )

    @pytest.mark.parametrize("tc", _params(HAPPY_CASES))
    def test_country_abbreviation(self, response_cache, tc):
        location = LocationResponse.from_response(response_cache(tc["country_code"], tc["zip_code"]))
        logger.info(f"[{tc['id']}] country_abbreviation='{location.country_abbreviation}'")
        assert location.country_abbreviation.upper() == tc["expected_country_abbreviation"].upper(), (
            f"Expected abbreviation '{tc['expected_country_abbreviation']}' "
            f"but got '{location.country_abbreviation}'"
        )

    @pytest.mark.parametrize("tc", _params(HAPPY_CASES))
    def test_response_schema(self, response_cache, tc):
        """All required top-level and place-level fields must be present."""
        data = response_cache(tc["country_code"], tc["zip_code"]).json()
        logger.info(f"[{tc['id']}] validating schema")
        for field in ("post code", "country", "country abbreviation", "places"):
            assert field in data, f"Top-level field missing: '{field}'"
        assert len(data["places"]) > 0, "'places' list must not be empty"
        place = data["places"][0]
        for field in ("place name", "state", "latitude", "longitude"):
            assert field in place, f"Place field missing: '{field}'"

    @pytest.mark.parametrize("tc", _params(HAPPY_CASES))
    def test_content_type_is_json(self, response_cache, tc):
        content_type = response_cache(tc["country_code"], tc["zip_code"]).headers.get("Content-Type", "")
        logger.info(f"[{tc['id']}] Content-Type='{content_type}'")
        assert "application/json" in content_type, (
            f"Expected 'application/json' in Content-Type but got '{content_type}'"
        )


# ---------------------------------------------------------------------------
# Negative — invalid inputs → 404
# ---------------------------------------------------------------------------

class TestLocationNegative:
    """Validates 404 status and empty body for non-existent/mismatched inputs."""

    @pytest.mark.parametrize("tc", _params(NEGATIVE_CASES))
    def test_status_code_is_404(self, response_cache, tc):
        response = response_cache(tc["country_code"], tc["zip_code"])
        logger.info(f"[{tc['id']}] status={response.status_code}")
        assert response.status_code == 404, (
            f"Expected 404 but got {response.status_code} "
            f"for {tc['country_code']}/{tc['zip_code']}"
        )

    @pytest.mark.parametrize("tc", _params(NEGATIVE_CASES))
    def test_404_body_is_empty_json(self, response_cache, tc):
        body = response_cache(tc["country_code"], tc["zip_code"]).json()
        logger.info(f"[{tc['id']}] 404 body={body}")
        assert body == {}, f"Expected empty JSON {{}} for 404 but got: {body}"


# ---------------------------------------------------------------------------
# Performance — response time stays under threshold
# ---------------------------------------------------------------------------

class TestLocationPerformance:
    """Response time must remain under PERFORMANCE_THRESHOLD_MS for all happy-path inputs."""

    @pytest.mark.performance
    @pytest.mark.parametrize("tc", _params(HAPPY_CASES))
    def test_response_time_under_threshold(self, response_cache, app_settings, tc):
        response = response_cache(tc["country_code"], tc["zip_code"])
        elapsed_ms = response.elapsed.total_seconds() * 1000
        threshold = app_settings.performance_threshold_ms
        logger.info(f"[{tc['id']}] elapsed={elapsed_ms:.0f}ms (threshold={threshold}ms)")
        assert elapsed_ms < threshold, (
            f"Response took {elapsed_ms:.0f}ms, "
            f"exceeds threshold of {threshold}ms"
        )
