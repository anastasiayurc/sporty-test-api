import pytest
from datetime import datetime
from pathlib import Path

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
        """
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