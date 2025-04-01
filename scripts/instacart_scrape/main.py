import requests
import xlwt
from datetime import datetime, timedelta
import os
import imghdr

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import re
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options

base_url = "https://www.costco.com"
section_id = 1
page = 1
products = []
product_links = []

categories = [
    "https://www.instacart.com/store/costco/collections/rc-a-34561-kirkland-signature?unauth-refresh=1",
    "https://www.instacart.com/store/costco/collections/snacks-and-candy",
    "https://www.instacart.com/store/costco/collections/9859-deli-dairy",
    "https://www.instacart.com/store/costco/collections/produce",
    "https://www.instacart.com/store/costco/collections/beverages",
    "https://www.instacart.com/store/costco/collections/1365-pantry-gen-merch",
    "https://www.instacart.com/store/costco/collections/frozen",
    "https://www.instacart.com/store/costco/collections/household",
    "https://www.instacart.com/store/costco/collections/9909-health-personal-care",
    "https://www.instacart.com/store/costco/collections/meat-and-seafood",
    "https://www.instacart.com/store/costco/collections/9886-paper-goods",
    "https://www.instacart.com/store/costco/collections/9904-cleaning-laundry",
    "https://www.instacart.com/store/costco/collections/pets",
    "https://www.instacart.com/store/costco/collections/baked-goods",
    "https://www.instacart.com/store/costco/collections/9809-home-goods",
    "https://www.instacart.com/store/costco/collections/electronics",
    "https://www.instacart.com/store/costco/collections/baby",
    "https://www.instacart.com/store/costco/collections/9929-other-goods",
    "https://www.instacart.com/store/costco/collections/dynamic_collection-sales",
    "https://www.instacart.com/store/costco/collections/rc-cakes",
    "https://www.instacart.com/store/costco/collections/rc-whats-new",
    "https://www.instacart.com/store/costco/collections/rc-fall-favorites",
    "https://www.instacart.com/store/costco/collections/rc-large-item-delivery",
    "https://www.instacart.com/store/costco/collections/rc-get-ready-for-fall-2024"
]

category_titles = [
    "Kirkland Signature",
    "Snacks & Candy",
    "Deli & Dairy",
    "Produce",
    "Beverages",
    "Pantry",
    "Frozen",
    "Household",
    "Health & Personal Care",
    "Meat & Seafood",
    "Paper Goods",
    "Cleaning & Laundry",
    "Pets",
    "Bakery",
    "Home Goods",
    "Electronics",
    "Baby",
    "Other Goods",
    "Sales",
    "Cakes",
    "New",
    "Fall Favorites",
    "Large Item Delivery",
    "Get ready for Fall"
]

def is_relative_url(string):
    # Check if the string starts with '/' and matches a valid URL path
    pattern = r"^\/([a-z0-9\-._~!$&'()*+,;=:%]+\/?)*$"
    return bool(re.match(pattern, string))

def scroll_to_bottom_multiple_times(driver, scroll_pause_time=2, max_scrolls=10):
    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_count = 0

    while scroll_count < max_scrolls:
        # Scroll down to the bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)  # Wait for new content to load

        # Calculate new scroll height and check if we've reached the bottom
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break  # Exit loop if no new content loads
        last_height = new_height
        scroll_count += 1

def get_product_list(driver):
    global section_id, categories
    num = 0
    driver.get(categories[0])
    driver.execute_script("document.body.style.zoom='25%'")
    time.sleep(120)

    for category in categories:
        driver.get(category)
        driver.execute_script("document.body.style.zoom='25%'")
        scroll_to_bottom_multiple_times(driver, 2, 100)
        elements = driver.find_elements(By.XPATH, "//div[@aria-label='Product']")
        for element in elements:

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
                image_url = img_element.get_attribute("srcset").split(", ")[0]
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
                title_element = element.find_element(By.CLASS_NAME, "e-1pnf8tv")
                title = title_element.text.strip()
            except:
                title = ""
            
            try:
                product_link_element = element.find_element(By.TAG_NAME, "a")
                product_link = product_link_element.get_attribute("href")
            except:
                product_link = ""

            try:
                informations = element.find_element(By.CLASS_NAME, "screen-reader-only").text
                price_splits = informations.split(":")
                price = price_splits[1].strip()
            except:
                price = ""

            record = [
                str(section_id),
                "https://instacart.com",
                product_link,
                "Instacart",
                category_titles[num],
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
                "50 Beale St # 600, San Francisco, California 94105, US",
                "+18882467822",
                "37.7914",
                "122.3960",
                "",
            ]
            
            products.append(record)
            print(record)
            section_id = section_id + 1
        num = num + 1
    
    index = 0
    for product in products:
        time.sleep(2)
        driver.get(product[2])
        try:
            description_element = driver.find_element(By.CLASS_NAME, "e-tluef2")
            driver.execute_script("arguments[0].scrollIntoView();", description_element)
            products[index][5] = description_element.text.strip()
        except:
            print("no description")
        try:
            rating_element = driver.find_element(By.CLASS_NAME, "e-1qqnk49")
            driver.execute_script("arguments[0].scrollIntoView();", rating_element)
            products[index][14] = rating_element.text.strip()
        except:
            print("no rating")
        try:
            rating_count_element = driver.find_element(By.CSS_SELECTOR, "button[data-testid='product-rating-count'] span")
            driver.execute_script("arguments[0].scrollIntoView();", rating_count_element)
            products[index][15] = rating_count_element.text
        except:
            print("no rating count")
        print(products[index])
        index = index + 1

    return products

if __name__ == "__main__":
    options = uc.ChromeOptions()
    # options.add_argument("--headless=new")  # Enable headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--start-maximized")  # Debugging support
    driver = uc.Chrome(options=options)
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
    
    records = get_product_list(driver=driver)
        
    for row_index, row in enumerate(records):
        for col_index, value in enumerate(row):
            sheet.write(row_index+1, col_index, value)

    # Save the workbook
    workbook.save("products/"+current_time+"/products.xls")



