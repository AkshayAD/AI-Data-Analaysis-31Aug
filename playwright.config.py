"""
Playwright configuration for end-to-end testing
"""
import os

# Base configuration
BASE_URL = os.getenv("TEST_URL", "http://localhost:8501")

# Test configuration
config = {
    "base_url": BASE_URL,
    "use": {
        "headless": os.getenv("HEADLESS", "true").lower() == "true",
        "screenshot": "only-on-failure",
        "video": "retain-on-failure",
        "trace": "retain-on-failure",
    },
    "timeout": 30000,  # 30 seconds
    "expect_timeout": 10000,  # 10 seconds
    "projects": [
        {
            "name": "chromium",
            "use": {
                "browser_name": "chromium",
                "viewport": {"width": 1920, "height": 1080},
            }
        },
        {
            "name": "firefox",
            "use": {
                "browser_name": "firefox",
                "viewport": {"width": 1920, "height": 1080},
            }
        },
        {
            "name": "webkit",
            "use": {
                "browser_name": "webkit",
                "viewport": {"width": 1920, "height": 1080},
            }
        }
    ],
    "reporter": [
        ["html", {"outputFolder": "playwright-report", "open": "never"}],
        ["json", {"outputFile": "test-results.json"}]
    ],
    "output_folder": "test-results",
    "retries": 1,
    "workers": 1,  # Run tests serially for Streamlit
}