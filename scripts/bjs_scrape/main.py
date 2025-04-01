import requests
from bs4 import BeautifulSoup
import xlwt
import os
from datetime import datetime
import imghdr
from fake_useragent import UserAgent
import json
import urllib.parse
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options

import sys

sys.path.append("../..")
from google_shopping_api import get_products, create_database_table

base_url = "https://www.bjs.com"
section_id = 1
page = 1
length = 1

def get_lists(current_time, prefix):
    global base_url, length, page, section_id
    ua = UserAgent()
    headers = {
        'User-Agent': ua.random
    }
    products = []
    # response = requests.get("https://www.bjs.com/product/wellsley-farms-purified-water-40-pk169-oz/3000000000000427090", headers=headers)
    # with open('index.html', 'w', encoding='utf-8') as file:
    #     file.write(response.text)
    
    while page <= 320:
        print("page : " + str(page))
        params = {
            "c": "ciojs-client-2.53.1",
            "key": "key_2i36vP8QTs3Ati4x",
            "i": "10b89e05-00d7-4c19-8cd4-8f49913a8cd8",
            "s": 1,
            "page": page,
            "num_results_per_page": 50,
            "pre_filter_expression": json.dumps({"or":[{"name":"avail_stores","value":"online"},{"name":"avail_stores","value":"0096"},{"and":[{"name":"avail_stores","value":"0096"},{"name":"avail_sdd","value":"0096"}]},{"name":"out_of_stock","value":"Y"}]})
        }
        response = requests.get("https://ac.cnstrc.com/browse/group_id/all", params=params, headers=headers)
        
        data = response.json()
        for result in data["response"]["results"]:
            try:
                response = requests.get(base_url + result["data"]["url"], params=params, headers=headers)
                soup = BeautifulSoup(response.content, 'html.parser')
                script_tag = soup.find('script', type='application/ld+json')
                if script_tag:
                    script_content = script_tag.string
                    decoded_content = urllib.parse.unquote(script_content)
                    json_data = json.loads(decoded_content)
                    soup = BeautifulSoup(json_data["description"], 'html.parser')
                    product_id = result["data"]["url"].split('/')[-1]
                    image_url = json_data.get("image")
                    download_url = ""
                    print(product_id)
                    
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
                    
                    record = [
                        str(section_id),
                        base_url,
                        base_url + result["data"]["url"],
                        "BJS",
                        json_data["brand"].get("name", ""),
                        soup.get_text(),
                        json_data.get("name", ""),
                        "",
                        "",
                        json_data["offers"][0].get("price", ""),
                        download_url,
                        json_data["image"],
                        "",
                        "",
                        json_data["aggregateRating"].get("ratingValue", ""),
                        json_data["aggregateRating"].get("reviewCount", ""),
                        "Miami,FL",
                        "+1(800)257-2582",
                        "42.2695",
                        "-71.6162",
                        "",
                    ]
                
                    products.append(record)
                    print(record)
                    section_id = section_id + 1
            except Exception as e:
                print(e)
        length = len(data["response"]["results"])
        page = page + 1
    return products
        
    

# Step 3: Main function
if __name__ == '__main__':
    titleData = ["id","Store page link", "Product item page link", "Store_name", "Category", "Product_description", "Product Name", "Weight/Quantity", "Units/Counts", "Price", "image_file_names", "Image_Link", "Store Rating", "Store Review number", "Product Rating", "Product Review number", "Address", "Phone number", "Latitude", "Longitude", "Description Detail"]
    widths = [10,50,50,60,45,70,35,25,25,20,130,130,30,30,30,30,60,50,60,60,80]
    style = xlwt.easyxf('font: bold 1; align: horiz center')
    products = []

    options = uc.ChromeOptions()
    # options.add_argument("--headless=new")  # Enable headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--start-maximized")  # Debugging support
    driver = uc.Chrome(options=options)

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
    
    records = get_lists(current_time, prefix)

    create_database_table("product_search.db", "google_store_data")
    for row_index, row in enumerate(records):
        get_products(driver, row[6], "product_search.db", "google_store_data", current_time, prefix, 10)
        
    for row_index, row in enumerate(records):
        for col_index, value in enumerate(row):
            sheet.write(row_index+1, col_index, value)

    # Save the workbook
    workbook.save("products/"+current_time+"/products.xls")
    
    
    
    
