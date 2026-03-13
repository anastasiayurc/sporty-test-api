"""
Test data store — add new test cases here without touching test logic.
"""

TEST_CASES = [
    {
        "id":              "TC_01 | HappyPath_US_ValidZip",
        "country_code":    "us",
        "zip_code":        "90210",
        "expected_status": 200,
        "expected_place":  "Beverly Hills",
        "marks":           ["smoke", "regression"],
    },
    {
        "id":              "TC_02 | HappyPath_DE_ValidZip",
        "country_code":    "de",
        "zip_code":        "10115",
        "expected_status": 200,
        "expected_place":  "Berlin",
        "marks":           ["smoke", "regression"],
    },
    {
        "id":              "TC_03 | Negative_InvalidZip",
        "country_code":    "us",
        "zip_code":        "00000",
        "expected_status": 404,
        "expected_place":  None,
        "marks":           ["regression"],
    },
    {
        "id":              "TC_04 | Negative_InvalidCountry",
        "country_code":    "invalid",
        "zip_code":        "12345",
        "expected_status": 404,
        "expected_place":  None,
        "marks":           ["regression"],
    },
]
