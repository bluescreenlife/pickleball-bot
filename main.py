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

    # sleep(2)

    try:
        username_input = driver.find_element(By.XPATH, ".//input[@id='account-username']")
        password_input = driver.find_element(By.XPATH, ".//input[@id='account-password']")
        login_button = driver.find_element(By.XPATH, ".//span[@class='btn-icon-text']")

        username_input.click()
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
    all_slots = driver.find_elements(By.XPATH, '//div[@class="planner-row"]')

    slot_num = 1
    slot_located = False
    slot_reserved = False

    for slot in all_slots:
        print(f"Trying slot {slot_num}...")

        try:
            # check if element has target start time
            slot.find_element(By.XPATH, f'.//time[text()="{start_time}" and contains(@class, "time-start")]')
            print(f"Found {start_time} time slot.")
            target_slot = slot
            slot_located = True

        except NoSuchElementException:
            slot_num +=1

    if slot_located:
        # get slot name
        slot_link = target_slot.find_element(By.XPATH, f".//a[@data-testid='classLink']")
        slot_title = slot_link.find_element(By.TAG_NAME, "span").text
        print(f"Slot title: {slot_title}")

        # click link for target time slot
        slot_link.click()
        print("Clicked reserve link.")

        sleep(2)

        reserve_button = driver.find_elements(By.XPATH, ".//button[@data-testid='reserveButton']") # seemingly 2 of these elements, one hidden
        reserve_button[1].click()
        print("Clicked reserve button.")

        sleep(2)

        agreement_box = driver.find_element(By.XPATH, ".//span[@class='c-indicator']")
        agreement_box.click()

        finish_button = driver.find_element(By.XPATH, ".//button[@data-testid='finishBtn']")
        finish_button.click()

        print("Check for reservation. Sleeping 60...")
        sleep(60)

        slot_reserved = True
    else:
        print("Could not locate specified time slot.")
        return False

    if slot_reserved:
        print(f"SUCCESS: Reserved {slot_title} at {start_time} on {date}.")
        return True
    else:
        print(f"ERROR: Could not reserve {slot_title} at {start_time} on {date}.")
        return False


# login info
login_url = "https://my.lifetime.life/login.html?resource=%2Fclubs%2Fmn%2Fbloomington-north.html"
username = os.environ.get("LIFETIME_USERNAME")
password = os.environ.get("LIFETIME_PASSWORD")

# class info
# date = "2024-03-25"
date = "2024-03-13"
start_time = "7:00"

# create driver
driver = webdriver_init()

# log in
log_in(login_url, username, password)

if log_in:
    register(date, start_time)


driver.quit()