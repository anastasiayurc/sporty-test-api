"""
Location test data — all inputs and expected outputs for the location endpoint.
Add new cases here; no changes to test or client layers required.
Segregated into HAPPY_CASES (200) and NEGATIVE_CASES (404) for targeted parametrize.
"""

# ---------------------------------------------------------------------------
# Happy path — valid country + zip combinations expected to return 200
# ---------------------------------------------------------------------------
HAPPY_CASES = [
    {
        "id":                            "TC_01 | HappyPath_US_ValidZip",
        "country_code":                  "us",
        "zip_code":                      "90210",
        "expected_place":                "Beverly Hills",
        "expected_country":              "United States",
        "expected_country_abbreviation": "US",
        "marks":                         ["smoke", "regression"],
    },
    {
        "id":                            "TC_02 | HappyPath_DE_ValidZip",
        "country_code":                  "de",
        "zip_code":                      "10115",
        "expected_place":                "Berlin",
        "expected_country":              "Germany",
        "expected_country_abbreviation": "DE",
        "marks":                         ["smoke", "regression"],
    },
    {
        "id":                            "TC_03 | HappyPath_FR_ValidZip",
        "country_code":                  "fr",
        "zip_code":                      "75001",
        "expected_place":                "Paris 01 Louvre",
        "expected_country":              "France",
        "expected_country_abbreviation": "FR",
        "marks":                         ["regression"],
    },
]

# ---------------------------------------------------------------------------
# Negative — invalid inputs expected to return 404
# ---------------------------------------------------------------------------
NEGATIVE_CASES = [
    {
        "id":           "TC_04 | Negative_NonExistentZip",
        "country_code": "us",
        "zip_code":     "00000",
        "marks":        ["regression"],
    },
    {
        "id":           "TC_05 | Negative_InvalidCountryCode",
        "country_code": "invalid",
        "zip_code":     "12345",
        "marks":        ["regression"],
    },
    {
        "id":           "TC_06 | Negative_CountryZipMismatch",
        "country_code": "de",
        "zip_code":     "90210",
        "marks":        ["regression"],
    },
]

# Performance threshold is environment-driven — see config/settings.py
# Access via the app_settings fixture: app_settings.performance_threshold_ms
