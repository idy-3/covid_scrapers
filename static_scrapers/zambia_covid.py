import os
import re
import sys
import time
from typing import List
import glob
import cv2
import pandas as pd
import pytesseract
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

script_dir = os.path.abspath(os.path.dirname(sys.argv[0]) or '.')
resource_path = os.path.join(script_dir, 'resources')


def fb_screen_shot():
    website = "https://www.facebook.com/mohzambia/posts" \
              "/pfbid02QKhxq9KMp1pTNA8J9QZPHM9gSkAwM7vhGDMmrngiFzh3xqqDV9QNWbapvkR5mBadl?__cft__[" \
              "0]=AZUwZgyNzX1fdVHUXNpHI0CDP7jdYyGIftLYnRc_" \
              "xjGJaP3FXzCS4Sf4PPmovUdZqceF0iAoHCS55J37zT5BL12ILTjgzUSAhRF7Ux733gA7NtiojUCJjyzjMwMhLTAicvFrTt88sqGZ" \
              "-9H04WtlKyRnnPvnPzVltInBr1NPsHGK_oOxQ6E1Pax2FAAkeitA6X0&__tn__=%2CO%2CP-R "

    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # options.headless = True
    options.add_argument('window-size=1920x1080')

    driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
    driver.get(website)
    driver.maximize_window()
    time.sleep(3)

    fb_img = driver.find_elements(By.XPATH, "//img[@class='_46-i img']/ancestor::node()/a")
    fb_img[0].click()
    time.sleep(3)
    driver.get_screenshot_as_file(f"{resource_path}\\temp\\zb_fb.jpg")

    driver.quit()


# get a screenshot of the post
# fb_screen_shot()


# # get all images
images = glob.glob(f"{resource_path}\\temp\\*.jpg")

# # load the original image
text_data = ''
for img in images:
    try:
        image = cv2.imread(img)

        # convert the image to black and white for better OCR
        ret, thresh1 = cv2.threshold(image, 120, 255, cv2.THRESH_BINARY)

        # pytesseract image to string to get results
        text = str(pytesseract.image_to_string(thresh1, config='--psm 6'))
        text_data = text
    except FileNotFoundError:
        print("file not found")

# print(text_data)

data = text_data.split('\n')

confirmed_cases = []
covid_tests = []
covid_deaths = []
total_data = {}

pat = '[\d]+[.,\d]+'
for row in data:
    num = row.find("CONFIRMED CASES")
    if num != -1:
        out = re.findall(pat, row[num:])
        confirmed_cases.append(out[1] if 1 < len(out) else out[0])

    num = row.find("TESTS")
    if num != -1:
        out = re.findall(pat, row[num:])
        covid_tests.append(out[1] if 1 < len(out) else out[0])

    num = row.find("COVID-19 DEATHS")
    if num != -1:
        out = re.findall(pat, row[num:])
        covid_deaths.append(out[1] if 1 < len(out) else out[0])

total_data['confirmed_cases'] = confirmed_cases
total_data['covid_tests'] = covid_tests
total_data['covid_deaths'] = covid_deaths

# print(total_data)

csv_path = os.path.join(script_dir, '../output')
df = pd.DataFrame(total_data)
df.to_csv(f'{csv_path}//covid_total(Zambia).csv', index=False)
