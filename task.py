import requests
from bs4 import BeautifulSoup
import psycopg2
from datetime import datetime

# DB connection details
DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "dbname": "rahim_store",
    "user": "postgres",
    "password": "mohid8907"
}

url = "https://www.rahimstore.com/actionShopping.php"
payload = {
    "shopping_main_page_dealoftheweek": "1"
}
headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.post(url, data=payload, headers=headers)

if response.status_code != 200:
    print(f"Failed to fetch data. Status code: {response.status_code}")
    exit()

soup = BeautifulSoup(response.text, "html.parser")
product_divs = soup.find_all("div", class_="item")
print(f"Found {len(product_divs)} products.")

# DB connection
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
except Exception as db_err:
    print(f"Database connection failed: {db_err}")
    exit()

inserted_count = 0
for i, item in enumerate(product_divs, 1):
    try:
        img_tag = item.find("img")
        name = img_tag["alt"].strip() if img_tag and "alt" in img_tag.attrs else "N/A"

        button = item.find("button")
        data_attr = button.get("data", "")
        parts = data_attr.split("~")
        price_str = parts[4].strip() if len(parts) >= 5 else "0"
        price = float(price_str.replace(",", ""))

        scrap_date = datetime.now()
        source = "Rahim Store"
        cursor.execute("""
            INSERT INTO scrapped_products (name, price, source, scrapdate)
            VALUES (%s, %s, %s, %s)
        """, (name, price, source, scrap_date))

        inserted_count += 1
        print(f"{i}. Inserted: {name} — Rs. {price}")
    except Exception as e:
        print(f"{i}. Skipped due to error: {e}")

# close DB connection
conn.commit()
cursor.close()
conn.close()

print(f"\nTotal products inserted: {inserted_count}")
