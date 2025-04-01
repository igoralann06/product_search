import re
import json
from datetime import datetime, timedelta
import os
import xlwt
import random

import requests
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options

from driver import CustomWebDriver

section_id = 1
products = []

def scrap_address_and_image(driver, product_url):
    global section_id

    cookies = driver.get_cookies()
    for cookie in cookies:
        driver.add_cookie(cookie)
    
    driver.get(product_url)
    
    if(section_id == 1):
        time.sleep(60)
    else:
        time.sleep(random.randint(3,5))
    price = ""

    try:
        price_element = driver.find_element(By.CLASS_NAME, "Price-group")
        price_title = price_element.get_attribute("title").strip()
        price_splits = price_title.split(":")
        price = price_splits[1].strip()
    except:
        price = ""

    record = [
        str(section_id),
        product_url,
        price,
    ]
    
    products.append(record)
    print(record)
    with open('prices.txt', 'a') as file:
        file.write(price + '\n')
    section_id = section_id + 1

    return products


if __name__ == "__main__":
    # driver = CustomWebDriver(is_eager=True)
    options = uc.ChromeOptions()
    # options.add_argument("--headless=new")  # Enable headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--start-maximized")  # Debugging support
    driver = uc.Chrome(options=options)
    titleData = ["id", "Product item page link", "Price"]
    product_urls = []
    widths = [10,150,50]
    style = xlwt.easyxf('font: bold 1; align: horiz center')

    if(not os.path.isdir("no_prices")):
        os.mkdir("no_prices")

    now = datetime.now()
    current_time = now.strftime("%m-%d-%Y-%H-%M-%S")
    prefix = now.strftime("%Y%m%d%H%M%S%f_")
    os.mkdir("no_prices/"+current_time)
    # os.mkdir("no_prices/"+current_time+"/images")
    
    if(os.path.isfile("no-price1.txt")):
        with open('no-price1.txt', 'r') as file:
            lines = file.readlines()
            for line in lines:
                cleaned_text = re.sub(r'\n', '', line)
                product_urls.append(cleaned_text)

    for product_url in product_urls:
        # print(events)
        records = scrap_address_and_image(driver, product_url)
    
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet('Sheet1')

    for col_index, value in enumerate(titleData):
        first_col = sheet.col(col_index)
        first_col.width = 256 * widths[col_index]
        sheet.write(0, col_index, value, style)
        
    for row_index, row in enumerate(records):
        for col_index, value in enumerate(row):
            sheet.write(row_index+1, col_index, value)

    # Save the workbook
    workbook.save("no_prices/"+current_time+"/products.xls")

    driver.quit()

