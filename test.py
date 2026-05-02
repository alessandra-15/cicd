import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# Default PHP file to test
test_file = os.getenv("TARGET_PHP_FILE", "index.php")

# Configure Chrome options
options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Set up Chrome WebDriver
service = Service("/usr/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=options)

try:
    url = f"http://localhost/staging/{test_file}"
    print(f"🚀 Auditing: {url}")

    driver.get(url)
    content = driver.page_source
    lower_content = content.lower()

    # 1. HARD BLOCK: Check for PHP Error Strings
    errors = ["fatal error", "parse error", "warning:", "stack trace:", "xdebug-error"]
    found_errors = [e for e in errors if e in lower_content]

    if found_errors:
        print(f"❌ DEPLOYMENT BLOCKED: Found PHP errors: {found_errors}")
        sys.exit(1)

    # 2. HARD BLOCK: Check for Raw PHP Leakage
    if "<?php" in content or "<?=" in content:
        print("❌ DEPLOYMENT BLOCKED: Raw PHP code leaked! Apache is not executing PHP.")
        sys.exit(1)

    # 3. SOFT BLOCK: Check for Empty Body
    body_text = driver.find_element("tag name", "body").text.strip()
    if not body_text and "img" not in lower_content:
        print("❌ DEPLOYMENT BLOCKED: Page is blank. Possible silent PHP crash.")
        sys.exit(1)

    print(f"✅ PASS: {test_file} rendered without errors.")

except Exception as e:
    print(f"⚠️ TEST SYSTEM ERROR: {e}")
    sys.exit(1)

finally:
    driver.quit()
