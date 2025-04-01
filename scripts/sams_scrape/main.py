import requests
import xlwt
import os
from datetime import datetime
import imghdr
from fake_useragent import UserAgent
from driver import CustomWebDriver
from selenium.webdriver.common.by import By

base_url = "https://www.samsclub.com"
products = []
section_id = 1
all_categories = []

def get_departments(driver):
    global base_url
    try:
        driver.get(base_url + "/c?xid=hdr:shop:moredepartments")
        # with open('index.html', 'w', encoding='utf-8') as file:
        #     file.write(response.text)
        links = driver.find_elements(By.CLASS_NAME, "bst-link-primary")
        # links = soup.find_all('a', class_="bst-link bst-link-small bst-link-primary")
        departments = []
        for link in links:
            if link.get_dom_attribute("href").startswith('/c/'):
                departments.append(base_url + link.get_dom_attribute("href"))
        return departments
    except Exception as e:
        print(e)
        
def get_secondaries(driver, departments):
    global base_url
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
        }
        secondary_links = []
        for department in departments:
            driver.get(department)
            secondaries = driver.find_elements(By.CLASS_NAME, "bst-link-primary")
            for secondary in secondaries:
                if secondary.get_dom_attribute("href").startswith('/c/'):
                    secondary_links.append(base_url + secondary.get_dom_attribute("href"))
        return secondary_links
    except Exception as e:
        print(e)
        
def get_categories(driver, secondaries):
    global base_url, all_categories
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
        }
        category_links = []
        secondary_links = []
        for secondary in secondaries:
            response = driver.get(secondary)
            categories = driver.find_elements(By.CLASS_NAME, "bst-link-primary")
            for category in categories:
                if category.get_dom_attribute("href").startswith('/b/'):
                    category_links.append(base_url + category.get_dom_attribute("href"))
                    href = category.get_dom_attribute("href").split('?')[0]
                    full_url = base_url + href
                    if(full_url not in all_categories):
                        all_categories.append(base_url + href)
                    print(base_url + href)
                elif category.get_dom_attribute("href").startswith('/c/'):
                    secondary_links.append(base_url + category.get_dom_attribute("href"))
        return secondary_links
    except Exception as e:
        print(e)
    

# Step 3: Main function
if __name__ == '__main__':
    driver = CustomWebDriver()

    departments = get_departments(driver)
    secondaries = get_secondaries(driver, departments)
    other_secondaries = get_categories(driver, secondaries)
    if(other_secondaries is not None):
        get_categories(driver, other_secondaries)
    
    unique_list = list(set(category.strip() for category in all_categories))
    with open("stores.txt", "w") as file:
        for item in unique_list:
            file.write(f"{item}\n")
    
    
    
