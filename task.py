import requests
from bs4 import BeautifulSoup
import csv

url = "https://www.rahimstore.com/actionShopping.php"

payload = {
    "shopping_main_page_dealoftheweek": "1"
}

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.post(url, data=payload, headers=headers)

if response.status_code != 200:
    print(f" Failed to fetch data. Status code: {response.status_code}")
    exit()

soup = BeautifulSoup(response.text, "html.parser")

product_divs = soup.find_all("div", class_="item")

print(f" Found {len(product_divs)} products.")

products = []

for i, item in enumerate(product_divs, 1):
    try:
        img_tag = item.find("img")
        name = img_tag["alt"].strip() if img_tag and "alt" in img_tag.attrs else "N/A"

        button = item.find("button")
        data_attr = button.get("data", "")
        parts = data_attr.split("~")
        price = parts[4].strip() if len(parts) >= 5 else "N/A"  

        print(f"{i}. {name} — Rs. {price}")
        products.append([name, price])
    except Exception as e:
        print(f"{i}. Skipped due to error: {e}")

if products:
    with open("deal_of_week_products.csv", "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Product Name", "Price (PKR)"])
        writer.writerows(products)
    print(" Data saved to deal_of_week_products.csv")
else:
    print(" No product data extracted.")