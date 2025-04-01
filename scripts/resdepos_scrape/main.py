import requests
import xlwt
from datetime import datetime, timedelta
import os
import imghdr

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from driver import CustomWebDriver

import sys

sys.path.append("../..")
from google_shopping_api import get_products, create_database_table

base_url = "https://member.restaurantdepot.com/customer/account/login/"
section_id = 1
page = 1
products = []

def scrap_address_and_image(driver: CustomWebDriver):
    global section_id
    
    driver.get(base_url)
    email_field = driver.find_element(By.ID, "email")
    password_field = driver.find_element(By.ID, "pass")
    
    email_field.send_keys("sabirajafer@gmail.com")
    password_field.send_keys("Welcome1@3")
    
    password_field.send_keys(Keys.RETURN)
    
    driver.get("https://member.restaurantdepot.com/products?sort=saleranking&it=product&pg=1")
    page_content = driver.find_element(By.CLASS_NAME, "total").text.strip()
    pages = page_content.split("of")
    max_page = int(pages[1])
    print(max_page)
    
    # driver.implicitly_wait(10)
    
    for i in range(1, max_page):
        driver.get("https://member.restaurantdepot.com/products?sort=saleranking&it=product&pg="+str(i))
        
        # Locate the script tag containing the JSON data
        elements = driver.find_elements(By.CLASS_NAME, "custom-listing-table")
        print(len(elements))
        # Extract the script content
        for element in elements:
            try:
                image = element.find_element(By.CLASS_NAME, "product-image-photo")
                image_url = image.get_attribute("src")
                price = ""
                category = ""
                binStr = ""
                upc = ""
                weight = ""
                unit = ""
                title = ""
                item = ""
                download_url = ""
                info = element.find_element(By.CLASS_NAME, "custom-listing-info")
                flag = element.find_element(By.CLASS_NAME, "custom-listing-flag")
                category_element = element.find_element(By.CLASS_NAME, "category-name")
                category = category_element.text.strip()
                
                driver.execute_script("arguments[0].scrollIntoView();", element)
                props = info.find_elements(By.TAG_NAME, "li")
                try:
                    price_element = flag.find_element(By.CLASS_NAME, "select-price")
                    price = price_element.get_attribute("data-item-price")
                    price = price.strip()
                except:
                    try:
                        price_element = flag.find_element(By.CLASS_NAME, "product-package-select")
                        price = price_element.text.strip()
                        price = " ".join(price.split())
                    except Exception as e:
                        print(e)
                        price = ""
                if(image_url):
                    try:
                        # responseImage = requests.get(image_url)
                        # image_type = imghdr.what(None, responseImage.content)
                        # if responseImage.status_code == 200:
                        #     img_url = "products/"+current_time+"/images/"+prefix+str(section_id)+'.'+image_type
                        #     with open(img_url, 'wb') as file:
                        #         file.write(responseImage.content)
                        #         download_url = img_url
                        download_url = "products/"+current_time+"/images/"+prefix+str(section_id)+'.'+"jpg"
                    except Exception as e:
                        print(e)
                
                for prop in props:
                    items = prop.text.split(":")
                    key = items[0].strip()
                    if(len(items) == 1):
                        title = items[0]
                    elif "Item" in key:
                        item = items[1]
                    elif "UPC" in key:
                        upc = items[1]
                    elif "unit" in key:
                        unit = unit + "," + items[1]
                    elif "case" in key:
                        weight = items[1]
                    elif "BIN" in key:
                        binStr = items[1]
                record = [
                    str(section_id),
                    "https://www.restaurantdepot.com",
                    base_url,
                    "Restaurant Depot",
                    category,
                    "",
                    title,
                    weight,
                    unit,
                    price,
                    download_url,
                    image_url,
                    "",
                    "",
                    "",
                    "",
                    "Corporate Headquarters 1710 Whitestone Expressway, Whitestone, NY 11357",
                    "+1(718)762-8700",
                    "40.782",
                    "-73.829",
                    "",
                    item,
                    upc,
                    binStr
                ]
                
                products.append(record)
                print(record)
                section_id = section_id + 1
            except Exception as e:
                print(e)
    
    driver.quit()
    
    # try:
    #     link: WebElement = driver.wait_for(
    #         "visibility_of_element_located",
    #         By.CLASS_NAME,
    #         "bst-link bst-link-small bst-link-primary",
    #         timeout=12,
    #     )
    #     # image_div = driver.find_element(By.CLASS_NAME, 'ys-event-details__hero-section__image')
    #     style_attribute = link.get_attribute("href")
    #     # print(style_attribute)
    #     print(style_attribute)
    # except Exception as e:
    #     print(e)
    return products


if __name__ == "__main__":
    driver = CustomWebDriver(is_eager=True)
    titleData = ["id","Store page link", "Product item page link", "Store_name", "Category", "Product_description", "Product Name", "Weight/Quantity", "Units/Counts", "Price", "image_file_names", "Image_Link", "Store Rating", "Store Review number", "Product Rating", "Product Review number", "Address", "Phone number", "Latitude", "Longitude", "Description Detail", "Item", "UPC", "BIN"]
    widths = [10,50,50,60,45,70,35,25,25,20,130,130,30,30,30,30,60,50,60,60,80,40,40,40]
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
    
    records = scrap_address_and_image(driver=driver)

    create_database_table("product_search.db", "google_store_data")
    for row_index, row in enumerate(records):
        get_products(driver, row[6], "product_search.db", "google_store_data", current_time, prefix, 10)
        
    for row_index, row in enumerate(records):
        for col_index, value in enumerate(row):
            sheet.write(row_index+1, col_index, value)

    # Save the workbook
    workbook.save("products/"+current_time+"/products.xls")



