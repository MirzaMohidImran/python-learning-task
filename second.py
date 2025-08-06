import requests
import time
import psycopg2
from datetime import datetime

#DB connection
conn = psycopg2.connect(
    host="localhost",
    database="alfatah_store",
    user="postgres",
    password="mohid8907"
)
cursor = conn.cursor()

# Scrapin
base_url = "https://alfatah.pk/products.json"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

all_products = []
page = 1
limit = 250
source_url = "https://alfatah.pk"
scrap_time = datetime.now()

while True:
    print(f"Fetching page {page}...")
    params = {"limit": limit, "page": page}

    response = requests.get(base_url, headers=headers, params=params)

    if response.status_code != 200:
        print(f"Failed to fetch page {page}. Status code: {response.status_code}")
        break

    data = response.json()
    products = data.get("products", [])

    if not products:
        print("No more products. Scraping complete.")
        break

    for product in products:
        name = product["title"]
        variant = product.get("variants", [{}])[0]
        price = variant.get("price", "0")

        # Save DB
        try:
            cursor.execute(
                """
                INSERT INTO scrapped_products (name, price, source, scrapdate)
                VALUES (%s, %s, %s, %s)
                """,
                (name, float(price), source_url, scrap_time)
            )
            conn.commit()
        except Exception as e:
            print(f"Error inserting product '{name}': {e}")
            conn.rollback()

        print(f"{len(all_products) + 1}. {name} - Rs. {price}")
        all_products.append((name, price))

    page += 1
    time.sleep(1)

print(f"\nScraped total {len(all_products)} products.")

# Close DB connec
cursor.close()
conn.close()
