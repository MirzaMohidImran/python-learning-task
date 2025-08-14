import requests
import time
import psycopg2
from datetime import datetime

# Database conf
DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "dbname": "rahim_store",
    "user": "postgres",
    "password": "mohid8907"
}

# Connect  DB
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    print("Connected to database successfully.")
except Exception as db_err:
    print(f" Database connection failed: {db_err}")
    exit()

# Scraping setup
base_url = "https://alfatah.pk/products.json"
headers = {"User-Agent": "Mozilla/5.0"}
source_url = "https://alfatah.pk"
scrap_time = datetime.now()

all_products = []
page = 1
limit = 250

while True:
    print(f"Fetching page {page}...")
    params = {"limit": limit, "page": page}

    try:
        response = requests.get(base_url, headers=headers, params=params)
    except Exception as req_err:
        print(f"Request error on page {page}: {req_err}")
        break

    if response.status_code != 200:
        print(f"Failed to fetch page {page}. Status code: {response.status_code}")
        break

    data = response.json()
    products = data.get("products", [])

    if not products:
        print("No more products. Scraping complete.")
        break

    for product in products:
        try:
            name = product["title"]
            variant = product.get("variants", [{}])[0]
            price = float(variant.get("price", "0"))

            cursor.execute("""
                INSERT INTO scrapped_products (name, price, source, scrapdate)
                VALUES (%s, %s, %s, %s)
            """, (name, price, source_url, scrap_time))

            conn.commit()
            all_products.append((name, price))
            print(f"{len(all_products)}. Inserted: {name} — Rs. {price}")
        except Exception as e:
            print(f"⚠️ Error inserting product '{product.get('title', 'Unknown')}': {e}")
            conn.rollback()

    page += 1
    time.sleep(1)

# Close DB 
cursor.close()
conn.close()
print(f"\n Scraped total {len(all_products)} products and saved to database.")
