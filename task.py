# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.common.exceptions import NoSuchElementException
# from openpyxl import Workbook
# import time

# driver = webdriver.Chrome()

# driver.get("https://www.rahimstore.com/")
# time.sleep(5)  

# workbook = Workbook()
# sheet = workbook.active
# sheet.title = "Products"
# sheet.append(["Product Name", "Price"])  

# page_number = 1

# while True:
#     print(f"Scraping Page {page_number}...")

#     time.sleep(3)  

#     products = driver.find_elements(By.CLASS_NAME, "product")

#     for product in products:
#         try:
#             name = product.find_element(By.CLASS_NAME, "woocommerce-loop-product__title").text
#         except:
#             name = "N/A"

#         try:
#             price = product.find_element(By.CLASS_NAME, "woocommerce-Price-amount").text
#         except:
#             price = "N/A"

#         print(f"{name} - {price}")
#         sheet.append([name, price])  

#     try:
#         next_button = driver.find_element(By.CSS_SELECTOR, "a.next.page-numbers")
#         next_button.click()
#         page_number += 1
#     except NoSuchElementException:
#         print("No more pages. Scraping finished.")
#         break  

# workbook.save("rahim_store_all_products.xlsx")
# print("Excel file saved as 'rahim_store_all_products.xlsx'")

# driver.quit()

# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import NoSuchElementException, TimeoutException
# from openpyxl import Workbook
# from openpyxl.styles import Font
# import time
# from datetime import datetime

# def setup_driver():
#     options = webdriver.ChromeOptions()
#     options.add_argument('--disable-blink-features=AutomationControlled')
#     options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     options.add_experimental_option('useAutomationExtension', False)
#     driver = webdriver.Chrome(options=options)
#     driver.maximize_window()
#     return driver

# def scrape_rahim_store():
#     driver = setup_driver()
    
#     try:
#         print("Navigating to Rahim Store...")
#         driver.get("https://www.rahimstore.com/")
        
#         # Wait for either products or timeout
#         try:
#             WebDriverWait(driver, 15).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, "li.product"))
#             )
#         except TimeoutException:
#             print("Timed out waiting for products to load")
#             return

#         # Create Excel workbook
#         workbook = Workbook()
#         sheet = workbook.active
#         sheet.title = "Products"
#         headers = ["No.", "Product Name", "Price"]
#         sheet.append(headers)
        
#         # Format header row
#         for cell in sheet[1]:
#             cell.font = Font(bold=True)

#         page_number = 1
#         product_count = 0

#         while True:
#             print(f"\nScraping Page {page_number}...")
            
#             # Wait for products to load
#             time.sleep(3)
#             products = driver.find_elements(By.CSS_SELECTOR, "li.product")
            
#             if not products:
#                 print("No products found on this page.")
#                 break

#             for product in products:
#                 product_count += 1
                
#                 # Get product name
#                 try:
#                     name = product.find_element(By.CSS_SELECTOR, "h2.woocommerce-loop-product__title").text.strip()
#                 except NoSuchElementException:
#                     name = "N/A"
                
#                 # Get product price
#                 try:
#                     price = product.find_element(By.CSS_SELECTOR, "span.price").text.strip()
#                 except NoSuchElementException:
#                     price = "N/A"
                
#                 print(f"{product_count}. {name} - {price}")
#                 sheet.append([product_count, name, price])

#             # Try to go to next page
#             try:
#                 next_button = WebDriverWait(driver, 5).until(
#                     EC.element_to_be_clickable((By.CSS_SELECTOR, "a.next.page-numbers"))
#                 )
#                 driver.execute_script("arguments[0].scrollIntoView();", next_button)
#                 time.sleep(1)
#                 driver.execute_script("arguments[0].click();", next_button)
#                 page_number += 1
#                 time.sleep(3)  # Wait for next page to load
#             except (NoSuchElementException, TimeoutException):
#                 print("\nReached the last page or couldn't find next button.")
#                 break

#         # Auto-adjust column widths
#         for col in sheet.columns:
#             max_length = 0
#             column = col[0].column_letter
#             for cell in col:
#                 try:
#                     if len(str(cell.value)) > max_length:
#                         max_length = len(str(cell.value))
#                 except:
#                     pass
#             adjusted_width = (max_length + 2) * 1.2
#             sheet.column_dimensions[column].width = adjusted_width

#         # Save with timestamp
#         timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
#         filename = f"RahimStore_Products_{timestamp}.xlsx"
#         workbook.save(filename)
#         print(f"\nSuccess! Saved {product_count} products to '{filename}'")

#     except Exception as e:
#         print(f"\nAn error occurred during scraping: {str(e)}")

#     finally:
#         driver.quit()
#         print("Browser closed.")

# if __name__ == "__main__":
#     scrape_rahim_store()