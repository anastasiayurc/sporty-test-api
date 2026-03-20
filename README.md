![logo](img/logo.svg)

## Test Cases

### Happy Path — 200 OK

| **ID** | **Description** | **Input** | **Assertions** | **Markers** |
|:---|:---|:---|:---|:---|
| TC_01 | Valid US zip code | us / 90210 | status, place name, post code echo, country, country abbreviation, schema, Content-Type | smoke, regression |
| TC_02 | Valid DE zip code | de / 10115 | status, place name, post code echo, country, country abbreviation, schema, Content-Type | smoke, regression |
| TC_03 | Valid FR zip code | fr / 75001 | status, place name, post code echo, country, country abbreviation, schema, Content-Type | regression |

### Negative Path — 404 Not Found

| **ID** | **Description** | **Input** | **Assertions** | **Markers** |
|:---|:---|:---|:---|:---|
| TC_04 | Non-existent zip code | us / 00000 | status 404, body is `{}` | regression |
| TC_05 | Invalid country code | invalid / 12345 | status 404, body is `{}` | regression |
| TC_06 | Country / zip mismatch | de / 90210 | status 404, body is `{}` | regression |

### Performance

| **Scope** | **Threshold** | **Markers** |
|:---|:---|:---|
| All happy-path inputs (TC_01–TC_03) | < `PERFORMANCE_THRESHOLD_MS` (default 3000ms, env-driven) | performance |

**Total: 6 test cases → 30 test functions** (one assertion per function)

---

## Validations Applied (per 200 response)

- **Status code** — `200` for valid inputs, `404` for invalid
- **Place name** — first place in response matches expected city
- **Post code echo** — `post code` in response matches the requested zip
- **Country name** — full country name matches expected value
- **Country abbreviation** — ISO abbreviation matches expected value
- **Schema completeness** — all required top-level and place-level fields present
- **Content-Type** — response header contains `application/json`
- **404 body** — error responses return an empty JSON object `{}`
- **Response time** — under configurable threshold (default 3000ms)

---

## Installation

```bash
# 1. Copy environment config
cp .env.example .env

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the full suite
pytest
```

The HTML report is generated automatically at `api_test_report.html`.

---

## Running Tests

```bash
# Full suite
pytest

# By marker
pytest -m smoke           # TC_01, TC_02 only
pytest -m regression      # all functional tests
pytest -m performance     # response-time tests only
pytest -m "not performance"

# By class
pytest tests/test_location.py::TestLocationHappyPath
pytest tests/test_location.py::TestLocationNegative
pytest tests/test_location.py::TestLocationPerformance

# Quick output (no live logs)
pytest --no-header -q
```

## Environment Overrides

All settings are driven by environment variables. Override at runtime without editing any code:

```bash
# Target a staging server
ENV=staging API_BASE_URL=https://staging.api.example.com pytest -m smoke

# Stricter performance threshold
PERFORMANCE_THRESHOLD_MS=500 pytest -m performance

# Shorter timeout
API_TIMEOUT=5 pytest
```

| Variable | Default | Purpose |
|:---|:---|:---|
| `ENV` | `local` | Environment name (logged at session start) |
| `API_BASE_URL` | `https://api.zippopotam.us` | API target URL |
| `API_TIMEOUT` | `10` | HTTP request timeout in seconds |
| `PERFORMANCE_THRESHOLD_MS` | `3000` | Max acceptable response time in ms |

---

## Framework Design

### Architecture

```
sporty-test-api/
├── .env.example             # Committed env variable template
├── .env                     # Local overrides — gitignored, never committed
├── pytest.ini               # Global settings, markers, addopts
├── requirements.txt         # Pinned dependencies
├── conftest.py              # Session fixtures, report hooks
│
├── config/
│   └── settings.py          # Settings dataclass — single source of truth
│
├── client/
│   ├── base_client.py       # BaseClient — requests.Session, timeout, base URL
│   └── location_client.py   # LocationClient — one method per endpoint
│
├── models/
│   └── location.py          # LocationResponse + Place dataclasses
│
├── data/
│   └── location_data.py     # HAPPY_CASES, NEGATIVE_CASES dicts
│
├── tests/
│   └── test_location.py     # TestLocationHappyPath / Negative / Performance
│
└── assets/
    └── style.css            # HTML report custom styling
```

### Layers

```
┌──────────────────────────────────────────────┐
│   CONFIG LAYER  (config/settings.py)         │  ← Env vars, .env, frozen dataclass
├──────────────────────────────────────────────┤
│     DATA LAYER  (data/location_data.py)      │  ← HAPPY_CASES, NEGATIVE_CASES dicts
├──────────────────────────────────────────────┤
│   CLIENT LAYER  (client/location_client.py)  │  ← Endpoint methods, no HTTP detail
│                 (client/base_client.py)       │  ← requests.Session, timeout, URL
├──────────────────────────────────────────────┤
│    MODEL LAYER  (models/location.py)         │  ← Typed response objects
├──────────────────────────────────────────────┤
│     TEST LAYER  (tests/test_location.py)     │  ← One assertion per test function
├──────────────────────────────────────────────┤
│   FIXTURE LAYER (conftest.py)                │  ← app_settings, location_client,
│                                              │    response_cache (session-scoped)
├──────────────────────────────────────────────┤
│  SETTINGS LAYER (pytest.ini)                 │  ← Log level, markers, addopts
├──────────────────────────────────────────────┤
│ REPORTING LAYER (HTML report)                │  ← Results, live logs, custom style
└──────────────────────────────────────────────┘
```

### Adding a new test case

Edit **only** `data/location_data.py` — no other file needs to change:

```python
# data/location_data.py
HAPPY_CASES = [
    # ... existing cases ...
    {
        "id":                            "TC_07 | HappyPath_GB_ValidZip",
        "country_code":                  "gb",
        "zip_code":                      "SW1A1AA",
        "expected_place":                "London",
        "expected_country":              "United Kingdom",
        "expected_country_abbreviation": "GB",
        "marks":                         ["smoke", "regression"],
    },
]
```

All 7 test functions in `TestLocationHappyPath` automatically pick it up — 7 new tests with zero code changes.

### Request Flow

```
pytest collects tests
        │
        ▼
conftest.py — app_settings loaded from .env / env vars
        │         _log_environment prints session banner
        ▼
location_client (session-scoped) — LocationClient(settings)
        │
        ▼
response_cache (session-scoped) — fetches each (country, zip) once,
        │         caches Response object for all test functions
        ▼
For each test function:
  response_cache(country_code, zip_code)   ← cached, no duplicate HTTP calls
        │
        ▼
  LocationResponse.from_response(response) ← typed model, no raw dict access
        │
        ▼
  Single assertion → PASS / FAIL
        │
        ▼
pytest-html generates api_test_report.html
```