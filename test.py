from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
 
options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
 
service = Service("/usr/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=options)
 
driver.get("http://localhost")
time.sleep(2)
 
assert "Hello CI/CD World" in driver.page_source
print("TEST PASSED")
 
driver.quit()
