# coding: utf-8


# Imports
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import logging
import os


# Logger
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

# Renfe URL
url = "https://www.renfe.com/es/es"
driver.get(url)
time.sleep(5)

# Find button with id 'origin'
origin_button = driver.find_element(By.ID, "origin")
origin_button.click()
time.sleep(2)

# Write in input with id 'origin' the name of the origin
origin_input = driver.find_element(By.ID, "origin")
origin_input.send_keys("MADRID (TODAS)")
time.sleep(2)

# Click on li item with role 'option' and id 'awesomplete_list_1_item_0'
origin_option = driver.find_element(By.ID, "awesomplete_list_1_item_0")
origin_option.click()

# Find button with id 'destination'
destination_button = driver.find_element(By.ID, "destination")
destination_button.click()
time.sleep(2)

# Write in input with id 'destination' the name of the destination
destination_input = driver.find_element(By.ID, "destination")
destination_input.send_keys("BARCELONA (TODAS)")
time.sleep(2)

# Click on li item with role 'option' and id 'awesomplete_list_1_item_0'
destination_option = driver.find_element(By.ID, "awesomplete_list_2_item_0")
destination_option.click()

# Click on button with class 'mdc-button__touch sc-rf-button'
search_button = driver.find_element(By.CLASS_NAME, "mdc-button__touch")
search_button.click()
time.sleep(5)

# Close driver
driver.close()
driver.quit()