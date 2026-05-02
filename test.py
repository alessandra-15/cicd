cd ~/cicd

cat > test.py << 'EOF'
import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# TANGGAL NATIN ANG "Service" IMPORT

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
    
    driver.get(url)
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
EOF
