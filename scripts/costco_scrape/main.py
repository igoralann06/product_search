import requests
import xlwt
from datetime import datetime, timedelta
import os
import imghdr

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from driver import CustomWebDriver
import re
import time

import sys

sys.path.append("../..")
from google_shopping_api import get_products, create_database_table

base_url = "https://www.costco.com"
section_id = 1
page = 1
products = []
perPage = 24

categories = [
    "https://www.costco.com/appliances.html",
    "https://www.costco.com/baby-kids.html",
    "https://www.costco.com/beauty.html",
    "https://www.costco.com/clothing.html",
    "https://www.costco.com/computers.html",
    "https://www.costco.com/electronics.html",
    "https://www.costco.com/holiday-gifts.html",
    "https://www.costco.com/furniture.html",
    "https://www.costco.com/gift-cards-tickets.html",
    "https://www.costco.com/grocery-household.html",
    "https://www.costco.com/health-beauty.html",
    "https://www.costco.com/seasonal.html",
    "https://www.costco.com/installed-products.html",
    "https://www.costco.com/home-and-decor.html",
    "https://www.costco.com/hardware.html",
    "https://www.costco.com/jewelry.html",
    "https://www.costco.com/mattresses.html",
    "https://www.costco.com/office-products.html",
    "https://www.costco.com/patio-lawn-garden.html",
    "https://www.costco.com/pet-supplies.html",
    "https://www.costco.com/sports-fitness.html",
    "https://www.costco.com/auto-tires.html",
    "https://www.costco.com/special-events.html"
    "https://www.costco.com/toys.html"
]

def is_relative_url(string):
    # Check if the string starts with '/' and matches a valid URL path
    pattern = r"^\/([a-z0-9\-._~!$&'()*+,;=:%]+\/?)*$"
    return bool(re.match(pattern, string))

def get_categories(driver: CustomWebDriver):
    global categories

    driver.get("https://www.costco.com/LogonForm")

    email_field = driver.find_element(By.ID, "signInName")
    password_field = driver.find_element(By.ID, "password")
    
    email_field.send_keys("dearjafer@gmail.com")
    password_field.send_keys("Welcome1@3")
    
    password_field.send_keys(Keys.RETURN)
    time.sleep(30)

    urls = []
    for category in categories:
        driver.get(category)
        elements = driver.find_elements(By.CLASS_NAME, "external")
        for element in elements:
            driver.execute_script("arguments[0].scrollIntoView();", element)
            if(is_relative_url(element.get_dom_attribute("href"))):
                urls.append(base_url + element.get_dom_attribute("href"))
                print(base_url + element.get_dom_attribute("href"))
        
    return urls

def get_product_list(driver: CustomWebDriver, urls):
    global section_id
    
    count = 1
    print("Category Count : " + str(len(urls)))
    for url in urls:
        print("Category : " + str(count))
        driver.get(url)
        try:
            page_content = driver.find_element(By.XPATH, '//span[@automation-id="totalProductsOutputText"]').text
            pages = page_content.split("of")
            total_products = int(pages[1])
            if(not total_products):
                max_page = 1
            else :
                max_page = int(total_products / perPage) + 1
        except:
            max_page = 1
        print(max_page)
        
        for i in range(1, max_page + 1):
            driver.get(url + "?pageSize=24&currentPage=" + str(i))
            
            # Locate the script tag containing the JSON data
            elements = driver.find_elements(By.CLASS_NAME, "product-tile-set")
            print(len(elements))
            # Extract the script content
            for element in elements:
                try:
                    driver.execute_script("arguments[0].scrollIntoView();", element)

                    image_url = ""

                    try:
                        image = element.find_element(By.CLASS_NAME, "img-responsive")
                        image_url = image.get_dom_attribute("src")
                    except:
                        image_url = ""

                    download_url = ""
                    price = ""
                    category = ""
                    weight = ""
                    unit = ""
                    download_url = ""
                    rating = ""
                    rating_count = ""
                    product_link = ""
                    title = ""

                    try:
                        descriptionElement = element.find_element(By.CLASS_NAME, "description")
                        anchor = descriptionElement.find_element(By.TAG_NAME, 'a')
                        product_link = anchor.get_dom_attribute("href")
                        title = anchor.text
                    except:
                        product_link = ""
                        title = ""
                    category = url

                    try:
                        description = element.find_element(By.CLASS_NAME, "product-features").text
                    except:
                        description = ""
                    try:
                        price = element.find_element(By.CLASS_NAME, "price").text
                    except:
                        price = ""

                    try:
                        rating_string = element.find_element(By.CLASS_NAME, "offscreen").text
                        pattern = r"Rated ([0-9.]+) out of 5 stars based on (\d+) reviews\."
                        match = re.search(pattern, rating_string)

                        if match:
                            rating = match.group(1) 
                            rating_count = match.group(2)
                        else:
                            rating = ""
                            rating_count = ""
                    except:
                        rating = ""
                        rating_count = ""
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
                    # print(rating)

                    record = [
                        str(section_id),
                        "https://www.costco.com",
                        product_link,
                        "Costco",
                        category,
                        description,
                        title,
                        weight,
                        unit,
                        price,
                        download_url,
                        image_url,
                        "",
                        "",
                        rating,
                        rating_count,
                        "999 Lake Drive Issaquah, WA 98027",
                        "+1(425)313-8100",
                        "47.530101",
                        "-122.032619",
                        "",
                    ]
                    
                    products.append(record)
                    print(record)
                    section_id = section_id + 1
                except Exception as e:
                    print(e)
        count = count + 1
    
    driver.quit()

    return products


if __name__ == "__main__":
    driver = CustomWebDriver()
    titleData = ["id","Store page link", "Product item page link", "Store_name", "Category", "Product_description", "Product Name", "Weight/Quantity", "Units/Counts", "Price", "image_file_names", "Image_Link", "Store Rating", "Store Review number", "Product Rating", "Product Review number", "Address", "Phone number", "Latitude", "Longitude", "Description Detail"]
    widths = [10,50,50,60,45,70,35,25,25,20,130,130,30,30,30,30,60,50,60,60,80]
    style = xlwt.easyxf('font: bold 1; align: horiz center')
    
    if(not os.path.isdir("products")):
        os.mkdir("products")

    now = datetime.now()
    current_time = now.strftime("%m-%d-%Y-%H-%M-%S")
    prefix = now.strftime("%Y%m%d%H%M%S%f_")
    os.mkdir("products/"+current_time)
    os.mkdir("products/"+current_time+"/images")
    
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet('Sheet1')
    
    for col_index, value in enumerate(titleData):
        first_col = sheet.col(col_index)
        first_col.width = 256 * widths[col_index]  # 20 characters wide
        sheet.write(0, col_index, value, style)
    
    urls = get_categories(driver=driver)
    records = get_product_list(driver=driver, urls=urls)

    create_database_table("product_search.db", "google_store_data")
    for row_index, row in enumerate(records):
        get_products(driver, row[6], "product_search.db", "google_store_data", current_time, prefix, 10)
        
    for row_index, row in enumerate(records):
        for col_index, value in enumerate(row):
            sheet.write(row_index+1, col_index, value)

    # Save the workbook
    workbook.save("products/"+current_time+"/products.xls")



