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

base_url = "https://www.upwork.com/nx/search/jobs/?is_sts_vector_search_result=false&nav_dir=pop&per_page=50&sort=recency"
section_id = 1
page = 1
products = []
product_links = []

def is_relative_url(string):
    # Check if the string starts with '/' and matches a valid URL path
    pattern = r"^\/([a-z0-9\-._~!$&'()*+,;=:%]+\/?)*$"
    return bool(re.match(pattern, string))

def get_product_list(driver):
    global section_id
    
    driver.get("https://www.upwork.com/ab/account-security/login")
    time.sleep(50)
    start_page = input("Enter your start page number: ")
    end_page = input("Enter your end page number: ")

    if(start_page > end_page):
        return []

    num = int(start_page)

    while(num <= int(end_page) and num >= int(start_page)):
        driver.get(base_url+"&page="+str(num))
        driver.execute_script("document.body.style.zoom='80%'")
        elements = driver.find_elements(By.TAG_NAME, "article")
        print(len(elements))

        now = datetime.now()
        current_time = now.strftime("%m-%d-%Y-%H-%M-%S")
        
        for element in elements:
            title = ""
            categories = ""
            duration = ""
            level = ""
            description = ""
            work_type = ""
            hourly_rate = ""
            estimated_hours = ""
            budget = ""
            url = ""
            payment_verification = ""
            date_posted = ""
            reviews = ""
            funds_spent = ""
            client_location = ""

            driver.execute_script("arguments[0].scrollIntoView();", element)

            try:
                heading = element.find_element(By.TAG_NAME, "h2")
                title = heading.text.strip()
            except:
                title = ""
            
            try:
                job_type_label = element.find_element(By.XPATH, './/li[@data-test="job-type-label"]')
                work_type = job_type_label.text.strip()
            except:
                work_type = ""
            
            try:
                experience_level = element.find_element(By.XPATH, './/li[@data-test="experience-level"]')
                level = experience_level.text.strip()
            except:
                level = ""

            try:
                description_element = element.find_element(By.XPATH, './/div[@data-test="UpCLineClamp JobDescription"]')
                description = description_element.text.strip()
            except:
                description = ""

            try:
                experience_level = element.find_element(By.XPATH, './/li[@data-test="experience-level"]')
                level = experience_level.text.strip()
            except:
                level = ""

            try:
                duration_label = element.find_element(By.XPATH, './/li[@data-test="duration-label"]')
                duration = duration_label.text.strip()
            except:
                duration = ""

            try:
                is_fixed_price = element.find_element(By.XPATH, './/li[@data-test="is-fixed-price"]')
                budget = is_fixed_price.text.strip()
            except:
                budget = ""

            try:
                category_elements = element.find_elements(By.XPATH, './/button[@data-test="token"]')
                for category_element in category_elements:
                    categories = categories + category_element.text.strip() + ","
            except:
                categories = ""

            try:
                url_element = element.find_element(By.XPATH, './/a[@data-test="job-tile-title-link UpLink"]')
                url = url_element.get_attribute("href")
            except:
                url = ""

            try:
                payment_element = element.find_element(By.XPATH, './/li[@data-test="payment-verified"]')
                payment_verification = payment_element.text.strip()
            except:
                payment_verification = ""

            try:
                date_element = element.find_element(By.XPATH, './/small[@data-test="job-pubilshed-date"]')
                date_posted = date_element.text.strip()
            except:
                date_posted = ""

            try:
                review_element = element.find_element(By.XPATH, './/div[@data-test="feedback-rating UpCRating"]')
                reviews = review_element.text.strip()
            except:
                reviews = ""

            try:
                total_element = element.find_element(By.XPATH, './/li[@data-test="total-spent"]')
                funds_spent = total_element.text.strip().replace("spent", "")
            except:
                funds_spent = ""

            try:
                location_element = element.find_element(By.XPATH, './/li[@data-test="location"]')
                client_location = location_element.text.strip()
            except:
                client_location = ""

            if "Hourly" in work_type:
                budget = work_type.replace("Hourly:", "")
                work_type = "Hourly"

            record = [
                str(section_id),
                title,
                categories,
                work_type,
                level,
                description,
                duration,
                budget,
                url,
                payment_verification,
                current_time,
                date_posted,
                reviews,
                funds_spent,
                client_location,
            ]
            
            products.append(record)
            print(record)
            section_id = section_id + 1
        num = num + 1

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
    titleData = ["id", "title", "tech_stack_details", "job_type_label", "experience_level", "description", "duration_label", "budget", "url", "payment_verification", "date_posted", "time_since_posted", "reviews", "funds_spent", "client_location"]
    widths = [10,90,90,90,90,90,90,90,90,90,90,90,90,90,90]
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



