import logging
import pytest
from datetime import datetime
from pathlib import Path
from client.location_client import LocationClient
from config.settings import settings as _settings

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def app_settings():
    """Expose the loaded Settings object to all tests."""
    return _settings


@pytest.fixture(scope="session", autouse=True)
def _log_environment(app_settings):
    """Print the active environment config once at the start of the session."""
    logger.info("=" * 60)
    logger.info(f"  Environment : {app_settings.env}")
    logger.info(f"  API Base URL: {app_settings.api_base_url}")
    logger.info(f"  Timeout     : {app_settings.api_timeout}s")
    logger.info(f"  Perf. limit : {app_settings.performance_threshold_ms}ms")
    logger.info("=" * 60)


@pytest.fixture(scope="session")
def location_client(app_settings):
    return LocationClient(app_settings)


@pytest.fixture(scope="session")
def response_cache(location_client):
    """Fetch each unique (country_code, zip_code) once per session and cache the Response.
    All test functions share the same cached object — zero duplicate API calls.
    """
    _cache: dict = {}

    def _get(country_code: str, zip_code: str):
        key = (country_code, zip_code)
        if key not in _cache:
            _cache[key] = location_client.get_location(country_code, zip_code)
        return _cache[key]

    return _get


def pytest_html_report_title(report):
    report.title = "Sporty Group - API Automation Report"

def pytest_html_results_summary(postfix, prefix, summary,):
    # Read and embed SVG logo inline
    logo_path = Path(__file__).parent / "img" / "logo.svg"
    logo_html = ""
    if logo_path.exists():
        svg_content = logo_path.read_text()
        logo_html = f'<div style="margin-bottom: 10px;">{svg_content}</div>'

    # Injects a branded header at the top of the report
    prefix.extend([
        f"""
        <div style="background-color: #1b1e25; padding: 20px; text-align: center; border-radius: 8px; margin-bottom: 20px;">
            {logo_html}
            <h2 style="color: #fff; margin: 0;">Sporty Group QA Assignment</h2>
            <p style="color: #E41B23; font-weight: bold;">Automated API Test Suite Results</p>
        </div>
        """
    ])

    # Clean up test names: show only TC_XX | ... part
    postfix.extend([
        r"""
        <script>
            function cleanTestNames() {
                var cells = document.querySelectorAll("#results-table .col-testId");
                if (cells.length === 0) {
                    setTimeout(cleanTestNames, 300);
                    return;
                }
                cells.forEach(function(cell) {
                    var text = cell.innerText || cell.textContent;
                    var match = text.match(/\[(.+)\]/);
                    if (match) { cell.innerText = match[1]; }
                });
            }
            document.addEventListener("DOMContentLoaded", function() {
                setTimeout(cleanTestNames, 500);
            });
        </script>
        """
    ])

@pytest.hookimpl(optionalhook=True)
def pytest_metadata(metadata):
    metadata.pop("JAVA_HOME", None) # Clean up sensitive info
    metadata["Project"] = "Sporty Group QA"
    metadata["Execution Time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")