import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

test_file = os.getenv("TARGET_PHP_FILE", "index.php")

options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# DITO ANG HACK: Walang Service path! Selenium na ang maghahanap.
driver = webdriver.Chrome(options=options)

try:
    url = f"http://localhost/staging/{test_file}"
    print(f"Auditing: {url}")
    
    # MAG-INTAY NA MAGING AVAILABLE ANG WEB SERVER
    print("Checking if web server is available...")
    for i in range(10):
        try:
            driver.get(url)
            print(f"Connected to web server successfully!")
            break
        except WebDriverException as e:
            if "ERR_CONNECTION_REFUSED" in str(e) or "net::ERR_CONNECTION_REFUSED" in str(e):
                print(f"Waiting for web server... attempt {i+1}/10")
                time.sleep(2)
            else:
                # Iba pang error, i-raise agad
                raise
    else:
        print("ERROR: Web server not available after 10 attempts")
        print("Make sure Apache/Nginx is running and configured for /var/www/html/staging")
        sys.exit(1)
    
    content = driver.page_source
    lower_content = content.lower()

    errors = ["fatal error", "parse error", "warning:", "stack trace:", "xdebug-error"]
    found_errors = [e for e in errors if e in lower_content]
    
    if found_errors:
        print(f"DEPLOYMENT BLOCKED: Found PHP errors: {found_errors}")
        sys.exit(1)

    if "<?php" in content or "<?=" in content:
        print("DEPLOYMENT BLOCKED: Raw PHP code leaked!")
        sys.exit(1)

    body_text = driver.find_element("tag name", "body").text.strip()
    if not body_text and "img" not in lower_content:
        print("DEPLOYMENT BLOCKED: Page is blank.")
        sys.exit(1)

    print(f"PASS: {test_file} rendered without errors.")

except Exception as e:
    print(f"TEST SYSTEM ERROR: {e}")
    sys.exit(1)
finally:
    driver.quit()
