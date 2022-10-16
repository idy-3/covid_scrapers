import glob
import os
import re
import sys
import time
import urllib.request

import cv2
import pandas as pd
import pytesseract
from pdf2image import convert_from_path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

script_dir = os.path.abspath(os.path.dirname(sys.argv[0]) or '.')
resource_path = os.path.join(script_dir, 'resources')


# ---------
def download_press_releases():
    website = "http://sante.gouv.sn/actualites"

    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.headless = True
    options.add_argument('window-size=1920x1080')

    driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
    driver.get(website)
    # driver.maximize_window()

    time.sleep(6)
    # # pagination
    pagination = driver.find_element(By.XPATH, '//li[@class="pager-last last"]/a')
    current_page = 1
    # last_page = int(pagination.get_attribute('href').split("=")[1])
    last_page = 1
    links = []

    # Get press release links and navigate to next page
    while current_page <= last_page:
        time.sleep(6)
        press_releases = driver.find_elements(By.XPATH, "//a[@class='see-more-mininal']")

        time.sleep(1)
        for release in press_releases:
            link = release.get_attribute('href')
            links.append(link)

        current_page += 1
        try:
            next_page = driver.find_element(By.XPATH, '//li[@class="pager-next"]/a')
            next_page.click()
        except:
            pass

    # get pdf links from the press releases
    pdf_links = []
    for link in links:
        driver.get(link)

        pdf_link = WebDriverWait(driver, 4).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@type, 'application/pdf')]")))

        pdf_links.append(pdf_link.get_attribute('href'))

    # download pdf for analysis
    idx = 1
    for pdf_link in pdf_links:
        print("beginning pdfs download")
        response = urllib.request.urlopen(pdf_link)
        time.sleep(3)
        file = open(f"{resource_path}\\img\\senegel_press_release_{idx}.pdf", 'wb')
        file.write(response.read())
        file.close()

    driver.quit()


# Find and Download press releases
# --------------
# download_press_releases()

# -----------
# convert pdf to image and read


def pdf_to_img(pdfs: str, uid: int) -> None:
    pages = convert_from_path(pdfs, 350)

    idx = 1
    for page in pages:
        image_name = f"Page_{str(uid)}_{str(idx)}.jpg"
        page.save(f"{resource_path}\\img\\{image_name}", "JPEG")
        idx = idx + 1


my_pdfs = glob.glob(f"{resource_path}\\img\\*.pdf")

for i, pdf in enumerate(my_pdfs):
    pdf_to_img(pdf, i)

# # get all images
images = glob.glob(f"{resource_path}\\img\\*.jpg")
# print(images)

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

total_test = []
total_cases = []
total_positivity = []

total_data = {}

total_test.append(re.findall('([\d]+[.,\d]+) tests', text_data)[0])
total_cases.append(re.findall('([\d]+[.,\d]+) cas', text_data)[0])
total_positivity.append(re.findall('([\d]+[.,\d]+)%', text_data)[0])

total_data['total_test'] = total_test
total_data['total_cases'] = total_cases
total_data['total_positivity'] = total_positivity

print(total_data)

csv_path = os.path.join(script_dir, '../output')
df = pd.DataFrame(total_data)
df.to_csv(f'{csv_path}//covid_total(Senegal).csv', index=False)
