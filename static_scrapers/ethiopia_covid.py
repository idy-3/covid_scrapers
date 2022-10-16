import os
import re
import sys
import time
from typing import List

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager

script_dir = os.path.abspath(os.path.dirname(sys.argv[0]) or '.')

website = "https://twitter.com/FMoHealth"

options = webdriver.ChromeOptions()
# options.add_experimental_option("detach", True)
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.headless = True
options.add_argument('window-size=1920x1080')

driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
driver.get(website)
# driver.maximize_window()
time.sleep(3)
last_page_height = driver.execute_script("return document.body.scrollHeight")
itemTargetCount = 100


def scrape() -> List[WebElement]:
    return driver.find_elements(By.XPATH, "//*[contains(text(), 'covid19ethiopia')]//parent::node("
                                          ")//preceding-sibling::span")


reports = []

while itemTargetCount > len(reports):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    time.sleep(1)

    new_page_height = driver.execute_script("return document.body.scrollHeight")

    if new_page_height == last_page_height:
        break
    last_page_height = new_page_height

    for data in scrape():
        reports.append(data.text)

pat = '[\d]+[.,\d]+'

total_tested = []
total_confirmed = []
total_infected = []

total_data = {}
for data in reports:
    nums = re.findall(pat, data)
    total_tested.append(nums[1] if 1 < len(nums) else None)
    total_confirmed.append(nums[2] if 2 < len(nums) else None)
    total_infected.append(nums[3] if 3 < len(nums) else None)

total_data['total_tested'] = total_tested
total_data['total_confirmed'] = total_confirmed
total_data['total_infected'] = total_infected

# print(total_data)

csv_path = os.path.join(script_dir, '../output')
df = pd.DataFrame(total_data)
df.to_csv(f'{csv_path}//covid_total(Ethiopia).csv', index=False)

driver.quit()
