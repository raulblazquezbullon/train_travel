# coding: utf-8


# Imports
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import logging
import os
import argparse
import datetime
import pytz
import re
import json


# Functions
def datetime_to_epoch(date: str) -> int:
    """Convert a datetime object to epoch time in milliseconds"""

    date_timestamp = datetime.datetime.strptime(date, "%d-%m-%Y")
    date_timestamp = date_timestamp.replace(tzinfo=pytz.UTC)

    return int(date_timestamp.timestamp()*1000)


def delete_cookie_banner(driver: webdriver.Chrome) -> None:
    """Delete the cookie banner that appears in the Renfe website"""

    cookie_banner = driver.find_element(By.ID, "onetrust-banner-sdk")
    driver.execute_script("arguments[0].style.display = 'none';", cookie_banner)


def convert_to_seconds(time_string):
    # Extract hours and minutes using regex
    match = re.search(r'(\d+)\s*horas\s*(\d+)\s*minutos', time_string)
    if match:
        hours = int(match.group(1))
        minutes = int(match.group(2))
        
        # Convert hours and minutes to seconds
        total_seconds = hours*3600 + minutes*60
        return total_seconds
    
    return None


# argparse configuration
parser = argparse.ArgumentParser(description="Train travel scraper")
parser.add_argument("--origin", type=str, help="Origin city", required=True)
parser.add_argument("--destination", type=str, help="Destination city", required=True)
parser.add_argument("--date_origin", type=str, help="Date of travel (dd-mm-yyyy)", required=True)
parser.add_argument("--date_destination", type=str, help="Date of return (dd-mm-yyyy)", default=None)
parser.add_argument("--travelers", type=str, help="Number of travelers", default=1)
args = parser.parse_args()


# Travel details
origin = args.origin
destination = args.destination
date_origin = datetime_to_epoch(args.date_origin)
date_destination = datetime_to_epoch(args.date_destination) if args.date_destination else None
travelers = args.travelers


# Logger configuration
log_dir = "./data/logs/"
os.makedirs(log_dir, exist_ok=True)
num_logs = len([f for f in os.listdir(log_dir) if f.endswith(".log")])
log_file = f"{log_dir}/train_travel_{num_logs}.log"
logging.basicConfig(
    level=logging.INFO,
    filename=log_file,
    filemode='w',
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


# Driver options
options = webdriver.ChromeOptions()
options.add_argument('--ignore-ssl-errors=yes')
options.add_argument('--ignore-certificate-errors')


# Set up the remote WebDriver
driver = webdriver.Remote(
    command_executor="http://localhost:4444/wd/hub",
    options=options,
)
driver.maximize_window()

logger.info(f"Arguments were parsed successfully: ({origin}, {destination}, {date_origin}, {date_destination}, {travelers})")

try:

    # Renfe URL
    logger.info("selenium is getting your request")
    url = "https://www.renfe.com/es/es"
    driver.get(url)
    time.sleep(1)

    # Find button with id 'origin'
    logger.info("Selecting origin")
    origin_button = driver.find_element(By.CLASS_NAME, "rf-input-autocomplete-alternative__input")
    origin_button.click()

    # Write in input with id 'origin' the name of the origin
    origin_input = driver.find_element(By.ID, "origin")
    origin_input.send_keys(origin)

    # Click on li item with role 'option' and id 'awesomplete_list_1_item_0'
    origin_option = driver.find_element(By.ID, "awesomplete_list_1_item_0")
    origin_option.click()
    logger.info("Origin was selected")

    # Find button with id 'destination'
    logger.info("Selecting destination")
    destination_button = driver.find_element(By.ID, "destination")
    destination_button.click()

    # Write in input with id 'destination' the name of the destination
    destination_input = driver.find_element(By.ID, "destination")
    destination_input.send_keys(destination)

    # Click on li item with role 'option' and id 'awesomplete_list_1_item_0'
    destination_option = driver.find_element(By.ID, "awesomplete_list_2_item_0")
    destination_option.click()
    logger.info("Destination was selected")

    logger.info("Origin and destination were selected")

    # Find input with id 'first-input'
    logger.info("Selecting origin date")
    date_input = driver.find_element(By.ID, "first-input")
    date_input.click()

    # Only travel one way
    if not date_destination:
        logger.info("Selecting one way ticket")
        one_way_button = driver.find_element(By.CLASS_NAME, "lightpick__label")
        one_way_button.click()
        logger.info("Traveling one way")
        time.sleep(1)

    # Get all the elements by class 'lightpick__day'
    days_available_origin = list(map(lambda x: int(x.get_attribute("data-time")), driver.find_elements(By.CLASS_NAME, "lightpick__day")))
    logger.info(f"Days available are {days_available_origin}")

    # TODO: Handle dates that are too far in the future

    # Check dates in days_available origin
    if not date_origin in days_available_origin:
        logger.error("The date selected is not available (probably due to unhandled future dates)")
        raise ValueError("The date selected is not available (probably due to unhandled future dates)")

    logger.info("Removing cookie banner")
    cookie_banner = driver.find_element(By.ID, "onetrust-banner-sdk")
    delete_cookie_banner(driver)
    
    # Click on the date with data-time equal to date_origin
    date_option = driver.find_element(By.XPATH, f"//div[@data-time='{date_origin}']")
    date_option.click()

    logger.info("Origin date was selected")

    # Check if date_destination is available
    if date_destination:
        logger.info("Selecting destination date")
        date_input = driver.find_element(By.ID, "second-input")
        date_input.click()

        # Get all the elements by class 'lightpick__day'
        days_available_destination = list(map(lambda x: int(x.get_attribute("data-time")), driver.find_elements(By.CLASS_NAME, "lightpick__day")))
        logger.info(f"Days available are {days_available_destination}")

        # TODO: Handle dates that are too far in the future

        # Check dates in days_available destination
        if not date_destination in days_available_destination:
            logger.error("The date selected is not available (probably due to unhandled future dates)")
            raise ValueError("The date selected is not available (probably due to unhandled future dates)")

        # Click on the date with data-time equal to date_destination
        date_option = driver.find_element(By.XPATH, f"//div[@data-time='{date_destination}']")
        date_option.click()
        logger.info("Destination date was selected")

    # Click on button with class 'lightpick__apply-action-sub'
    search_button = driver.find_element(By.CLASS_NAME, "lightpick__apply-action-sub")
    search_button.click()

    # Click on button with class 'mdc-button__touch sc-rf-button'
    search_button = driver.find_element(By.CLASS_NAME, "mdc-button__touch")
    search_button.click()
    logger.info("Searching for available trains")
    time.sleep(1)

    # Gather all the trains available
    logger.info("Gathering all the trains available")
    delete_cookie_banner(driver)
    trains = driver.find_element(By.CLASS_NAME, "row")

    time.sleep(1)

    trains_info = trains.text
    logger.info("Extracting train information")

    # Extract train information
    trains_info = trains_info.split("\n")
    pattern = re.compile(r'\d\d:\d\d h|\d+ horas \d+ minutos|\d*,\d* €')
    trains_info = list(filter(pattern.match, trains_info))

    logger.info(f"Train information: {trains_info}")

    if len(trains_info) % 4 != 0 or len(trains_info) == 0:
        logger.error("The train information is not correct")
        raise ValueError("The train information is not correct")
    
    # Save in a json file the train information
    logger.info("Saving train information in a json file")
    train_info = []
    for i in range(0, len(trains_info), 4):
        train_info.append({
            "departure_time": trains_info[i].replace(" h", ""),
            "arrival_time": trains_info[i+2].replace(" h", ""),
            "duration": convert_to_seconds(trains_info[i+1]),
            "price": float(trains_info[i+3].replace(" €", "").replace(",", ".")),
        })

    logger.info(f"Train information: {train_info}")

    output_dir = "./data/output/"
    os.makedirs(output_dir, exist_ok=True)
    
    if not date_destination:
        with open(f"{output_dir}train_info_{origin}_{destination}_{date_origin}.json", "w") as f:
            json.dump(train_info, f)

    else:
        with open(f"{output_dir}train_info_{origin}_{destination}_{date_origin}_{date_destination}.json", "w") as f:
            json.dump(train_info, f)


    # Close driver
    driver.close()
    driver.quit()

except Exception as e:
    logger.error(f"An error occurred: {e}")
    driver.close()
    driver.quit()
    raise e
