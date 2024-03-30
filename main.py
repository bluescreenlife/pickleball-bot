'''Logs a user into a LifeTime Fitness account and registers for desired Pickleball court times'''
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
from datetime import datetime, timedelta
import os
import time
from pytz import timezone

# ---- create webdriver ---- #
def webdriver_init():
    service = Service(ChromeDriverManager().install())
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("window-size=1200x1200")
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# ---- log in ---- #
def log_in(login_url, username, password):
    driver.get(login_url)

    try:
        # start timing
        pageload_start_time = time.time()

        # wait for username input to load, then proceed
        username_rule = (By.XPATH, ".//input[@id='account-username']")
        username_input = WebDriverWait(driver,15).until(EC.presence_of_element_located(username_rule))
        password_input = driver.find_element(By.XPATH, ".//input[@id='account-password']")
        login_button = driver.find_element(By.XPATH, ".//span[@class='btn-icon-text']")

        # end timing, report element load time
        pageload_end_time = time.time()
        pageload_total_time = pageload_end_time - pageload_start_time
        print(f"Login elements loaded in {pageload_total_time} seconds.")

        if username_input and password_input and login_button:
            username_input.send_keys(username)
            password_input.send_keys(password)
            login_button.click()
            print("Logged in.")
            return True
    except NoSuchElementException:
        print("Login issue: could not locate necessary element.")
        return False

# ---- register ---- #
def register(class_name, date, start_time):
    schedule_url = f"https://my.lifetime.life/clubs/mn/bloomington-north/classes.html?selectedDate={date}&mode=day&location=Bloomington+North"
    driver.get(schedule_url)

    slot_reserved = False

    # start timing
    pageload_start_time = time.time()

    time.sleep(10)
    
    # wait for start time elements, select all
    start_time_elements_rule = (By.XPATH, '//time[@class="time-start"]')
    start_time_elements = WebDriverWait(driver,30).until(EC.presence_of_all_elements_located(start_time_elements_rule))

    # end timing, report element load time
    pageload_end_time = time.time()
    pageload_total_time = pageload_end_time - pageload_start_time
    print(f"Located {len(start_time_elements)} court times in {pageload_total_time} seconds.")

    for element in start_time_elements:
        print(f"Checking for time match: {element.text.strip()}")
        if element.text.strip() == start_time:
            target_time_element = element
            print(f"Located target court time: {start_time}")

            # get the time element's grandparent element, broader div containing url
            target_slot = driver.execute_script("return arguments[0].parentNode.parentNode.parentNode;", target_time_element)
            break

    # if time slot found, continue with registration, else return error message
    if target_slot:
        # get slot name
        slot_link = target_slot.find_element(By.XPATH, f".//a[@data-testid='classLink']")
        slot_title = slot_link.find_element(By.TAG_NAME, "span").text.strip().lower()
        print(f"Slot title: {slot_title}")

        # check slot title against desired class name
        if slot_title == class_name.lower():
            print("Court time name match. Continuing...")

            # click link for target time slot
            slot_link.click()
            print("Clicked target court time link...")

            # wait for reserve button to be present, click reserve button
            try:
                # start timing
                pageload_start_time = time.time()

                reserve_button_rule = (By.XPATH, ".//button[@data-testid='reserveButton']")
                reserve_buttons = WebDriverWait(driver,15).until(EC.presence_of_all_elements_located(reserve_button_rule)) # seemingly 2 of these elements, one hidden
                
                # end timing, report element load time
                pageload_end_time = time.time()
                pageload_total_time = pageload_end_time - pageload_start_time
                print(f"Reserve button located in {pageload_total_time} seconds.")

                # click reserve button
                reserve_buttons[1].click()
                print("Clicked reserve button...")
            except NoSuchElementException:
                print("ERROR: Reserve button not available.")
                return False
            except IndexError:
                print("ERROR: Reserve button not available.")
                return False
            except TimeoutException:
                print("ERROR: Reserve button load timeout.")
                return False

            # wait for agreement box presence, click agreement box

            # start timing
            pageload_start_time = time.time()

            agreement_box_rule = (By.XPATH, ".//span[@class='c-indicator']")
            agreement_box = WebDriverWait(driver,15).until(EC.element_to_be_clickable(agreement_box_rule))

            # end timing, report element load time
            pageload_end_time = time.time()
            pageload_total_time = pageload_end_time - pageload_start_time
            print(f"Agreement box located in {pageload_total_time} seconds.")

            agreement_box.click()
            print("Clicked consent box...")

            # wait for finish button to be clickable, then click
            finish_button_rule = (By.XPATH, ".//button[@data-testid='finishBtn']")
            finish_button = WebDriverWait(driver,15).until(EC.element_to_be_clickable(finish_button_rule))
            finish_button.click()
            print("Clicked finish button. Waiting for confirmation page...")

            confirmation_header_rule = (By.XPATH, ".//h1[@data-testid='confirmationHeader']")
            confirmation_header = WebDriverWait(driver,30).until(EC.presence_of_element_located(confirmation_header_rule))

            if confirmation_header:
                print("Located confirmation header.")
                slot_reserved = True
        else:
            print(f"ERROR: class name and start time mismatch.")
            return False
    else:
        print("Could not locate specified time slot.")
        return False

    # confirm reservation and return status
    if slot_reserved:
        print(f"SUCCESS: Reserved {slot_title} at {start_time} on {date}.")
        return True
    else:
        print(f"ERROR: Could not reserve {slot_title} at {start_time} on {date}.")
        return False

# times: mon & fri 1PM, tues & thurs 9am
# Registration run times: 
    # Sunday @ 3PM for next week's Monday @ 1PM
    # Monday @ 11AM for next week's Tuesday @ 9AM
    # Wednesday @ 11AM for next week's Thursday @ 9AM
    # Thursday @ 3PM for next week's Friday @ 1PM


if __name__ == "__main__":
    # wait to ensure registration is live
    sleep(5)

    # datetime variables
    now = datetime.now(timezone('America/Chicago'))
    weekday = now.strftime("%A")
    date = now.date()

    # login info
    login_url = "https://my.lifetime.life/login.html?resource=%2Fclubs%2Fmn%2Fbloomington-north.html"
    username = os.environ.get("LT_USERNAME")
    password = os.environ.get("LT_PASSWORD")

    # add 7 days and 22 hr (when signup goes live) to current time
    scheduler_timedelta = timedelta(days=7, hours=22)
    class_datetime = now + scheduler_timedelta
    class_date = class_datetime.date()
    class_weekday = class_datetime.strftime("%A")

    # assign appropriate start time for class to register for
    if weekday in ("Sunday", "Thursday"):
        class_start = "1:00"
        class_name = "Pickleball Open Play: DUPR 3.75-4.25 REQUIRED"
    elif weekday in ("Monday", "Wednesday"):
        class_start = "9:00"
        class_name = "Pickleball Open Play-Intermediate (DUPR 3.5-3.9): DUPR 3.45+ Required"
    else:
        print(f"Weekday is currently {weekday}; not a designated registration time.")
        class_start = "NONE"
        class_name = "NONE"

    # print confirmation
    print(f"Timestamp: {weekday}, {date}")
    print(f"Attempt to register for: {class_name} on {class_weekday}, {class_date} at {class_start}...")

    # create driver
    driver = webdriver_init()

    # log in, run relative registration action
    if log_in(login_url, username, password):
        print("Login success. Attempting registration...")
        if register(class_name, class_date, class_start):
            print("RESULT: Success")
        else:
            print("RESULT: Registration failure")
    else:
        print("RESULT: Login failure")

    driver.quit()