import re
import json
from datetime import datetime, timedelta
import os
import xlwt

import requests
import time
import imghdr
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from driver import CustomWebDriver

base_url = "https://samsclub.com"
section_id = 1
products = []
offset = 45

def scrap_address_and_image(driver, store_url):
    global section_id
    
    # driver.implicitly_wait(10)
    links = []
    group = -1
    
    driver.get(store_url)
    
    try:
        count_string = driver.find_element(By.CLASS_NAME, "sc-page-title-results-total").text
        splits = count_string.split("+")
        total = int(splits[0].strip())
        print(total)
        group = int(total/offset) + 1

        category_element = driver.find_element(By.CLASS_NAME, "sc-page-title-heading")
        category = category_element.text.strip()
    except:
        group = -1

    for i in range(0, group):
        time.sleep(1.5)
        driver.get(store_url+"?offset="+str(offset*i))

        elements = driver.find_elements(By.CLASS_NAME, "sc-pc-medium-desktop-card-canary")
        print(len(elements))

        for element in elements:
            # links.append(link.get_attribute("href"))
            image_url = ""
            title = ""
            rating = ""
            rating_count = ""
            product_link = ""
            price = ""
            download_url = ""

            driver.execute_script("arguments[0].scrollIntoView();", element)
            
            try:
                img_element = element.find_element(By.TAG_NAME, "img")
                image_url = img_element.get_attribute("src")
            except:
                image_url = ""
            
            if(image_url):
                try:
                    responseImage = requests.get(image_url)
                    image_type = imghdr.what(None, responseImage.content)
                    if responseImage.status_code == 200:
                        img_url = "products/"+current_time+"/images/"+prefix+str(section_id)+'.'+image_type
                        with open(img_url, 'wb') as file:
                            file.write(responseImage.content)
                            download_url = img_url
                    # download_url = "products/"+current_time+"/images/"+prefix+str(section_id)+'.'+"jpg"
                except Exception as e:
                    print(e)

            try:
                title_element = element.find_element(By.TAG_NAME, "h3")
                title = title_element.get_attribute("innerHTML")
            except:
                title = ""

            try:
                rating_elements = element.find_elements(By.CLASS_NAME, "bst-rating-star")
                for rating_element in rating_elements:
                    rating_val = rating_element.get_attribute("aria-checked")
                    rating_label = rating_element.get_attribute("aria-label")
                    if(rating_val == "true"):
                        rating = rating_label
                        break
            except:
                rating = ""

            try:
                rating_count_element = element.find_element(By.CLASS_NAME, "bst-rating")
                rating_count = rating_count_element.text.strip().replace("(", "").replace(")", "")
            except:
                rating_count = ""
            
            try:
                product_link_element = element.find_element(By.TAG_NAME, "a")
                product_link = product_link_element.get_attribute("href")
            except:
                product_link = ""

            try:
                price_element = element.find_element(By.CLASS_NAME, "Price-group")
                price_title = price_element.get_attribute("title").strip()
                price_splits = price_title.split(":")
                price = price_splits[1].strip()
            except:
                price = ""

            record = [
                str(section_id),
                base_url,
                product_link,
                "Sam's Club",
                category,
                "",
                title,
                "",
                "",
                price,
                download_url,
                image_url,
                "",
                "",
                rating,
                rating_count,
                "2101 SE Simple Savings Dr Bentonville, Arkansas 72712",
                "+1(888)746-7726",
                "36.3526",
                "-94.2088",
                "",
            ]
            
            products.append(record)
            print(record)
            section_id = section_id + 1

    return products


if __name__ == "__main__":
    driver = CustomWebDriver(is_eager=True)
    titleData = ["id","Store page link", "Product item page link", "Store_name", "Category", "Product_description", "Product Name", "Weight/Quantity", "Units/Counts", "Price", "image_file_names", "Image_Link", "Store Rating", "Store Review number", "Product Rating", "Product Review number", "Address", "Phone number", "Latitude", "Longitude", "Description Detail"]
    store_urls = []
    widths = [10,50,50,60,45,70,35,25,25,20,130,130,30,30,30,30,60,50,60,60,80]
    style = xlwt.easyxf('font: bold 1; align: horiz center')

    if(not os.path.isdir("products")):
        os.mkdir("products")

    now = datetime.now()
    current_time = now.strftime("%m-%d-%Y-%H-%M-%S")
    prefix = now.strftime("%Y%m%d%H%M%S%f_")
    os.mkdir("products/"+current_time)
    os.mkdir("products/"+current_time+"/images")
    
    if(os.path.isfile("stores2.txt")):
        with open('stores2.txt', 'r') as file:
            lines = file.readlines()
            for line in lines:
                cleaned_text = re.sub(r'\n', '', line)
                store_urls.append(cleaned_text)

    for store_url in store_urls:

        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('Sheet1')
        
        for col_index, value in enumerate(titleData):
            first_col = sheet.col(col_index)
            first_col.width = 256 * widths[col_index]  # 20 characters wide
            sheet.write(0, col_index, value, style)

        # print(events)
        records = scrap_address_and_image(driver, store_url)
        
    for row_index, row in enumerate(records):
        for col_index, value in enumerate(row):
            sheet.write(row_index+1, col_index, value)

    # Save the workbook
    workbook.save("products/"+current_time+"/products.xls")

    driver.quit()

