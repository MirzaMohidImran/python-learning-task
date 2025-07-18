from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from openpyxl import Workbook
import time

driver = webdriver.Chrome()

driver.get("https://www.rahimstore.com/")
time.sleep(5)  

workbook = Workbook()
sheet = workbook.active
sheet.title = "Products"
sheet.append(["Product Name", "Price"])  

page_number = 1

while True:
    print(f"Scraping Page {page_number}...")

    time.sleep(3)  

    products = driver.find_elements(By.CLASS_NAME, "product")

    for product in products:
        try:
            name = product.find_element(By.CLASS_NAME, "woocommerce-loop-product__title").text
        except:
            name = "N/A"

        try:
            price = product.find_element(By.CLASS_NAME, "woocommerce-Price-amount").text
        except:
            price = "N/A"

        print(f"{name} - {price}")
        sheet.append([name, price])  

    try:
        next_button = driver.find_element(By.CSS_SELECTOR, "a.next.page-numbers")
        next_button.click()
        page_number += 1
    except NoSuchElementException:
        print("No more pages. Scraping finished.")
        break  

workbook.save("rahim_store_all_products.xlsx")
print("Excel file saved as 'rahim_store_all_products.xlsx'")

driver.quit()
