from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from time import sleep
import os

# create webdriver
def webdriver_init():
    service = Service(ChromeDriverManager().install())
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("window-size=1200x1200")
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# ---- log in ----
def log_in(login_url, username, password):
    driver.get(login_url)

    try:
        username_input = driver.find_element(By.ID, "account-username")
        password_input = driver.find_element(By.ID, "account-password")
        login_button = driver.find_element(By.ID, "login-btn")

        username_input.send_keys(username)
        password_input.send_keys(password)

        login_button.click()
        print("Logged in.")
        return True
    except NoSuchElementException:
        print("Login issue.")
    
    return False


# ---- register ----
# times: mon & fri 1PM, tues & thurs 9am

def register(date, start_time):
    schedule_url = f"https://my.lifetime.life/clubs/mn/bloomington-north/classes.html?selectedDate={date}&mode=day&location=Bloomington+North"
    driver.get(schedule_url)

    sleep(2)

    # find all time slot elements
    all_rows = driver.find_elements(By.XPATH, '//div[@class="planner-row"]')

    rownum = 0

    for row in all_rows:
        print(f"Trying row {rownum}...")

        try:
            row.find_element(By.XPATH, f'.//time[text()="{start_time}" and contains(@class, "time-start")]')
            print(f"Found {start_time} time slot.")
            reserve_link = row.find_element(By.XPATH, './/a[@data-testid="reserveLink"]')
            print(f"Found reserve link.")
            
            reserve_link.click()
        
            sleep(2)

            # TODO navigate through page to confirm register for class

            driver.find_element()

            return True

        except NoSuchElementException:
            pass

        rownum += 1
    
    print(f"No reservation link found for {start_time}")
    return False


# login info
login_url = "https://my.lifetime.life/login.html?resource=%2Fclubs%2Fmn%2Fbloomington-north.html"
username = os.environ.get("LIFETIME_USERNAME")
password = os.environ.get("LIFETIME_PASSWORD")

# class info
date = "2024-03-25"
start_time = "1:00"

# create driver
driver = webdriver_init()

# log in
log_in(login_url, username, password)

if log_in:
    register(date, start_time)


driver.quit()