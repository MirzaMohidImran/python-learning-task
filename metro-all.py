import requests
import time
import psycopg2
from datetime import datetime

# db
DB_CONFIG = {
    "dbname": "rahim_store",
    "user": "postgres",
    "password": "mohid8907",
    "host": "localhost",
    "port": "5432"
}

# api
CATEGORIES_API = "https://admin.metro-online.pk/api/read/Categories?filter=storeId&filterValue=10"
LIMIT = 500

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/115.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.metro-online.pk/",
}

FILTER_KEYS = [
    "promotion_tier1_id",
    "promotion_tier2_id",
    "tier1Id",
    "tier2Id",
    "tier3Id",
    "tier4Id"
]

# scrap function
def fetch_categories():
    try:
        resp = requests.get(CATEGORIES_API, headers=HEADERS)
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", [])
    except Exception as e:
        print(f"Error fetching categories: {e}")
        return []

def get_children(categories, parent_id):
    return [cat for cat in categories if cat.get("parentId") == parent_id]

def fetch_products_for_filter(category_id, filter_key):
    products = []
    offset = 0
    while True:
        url = (
            "https://admin.metro-online.pk/api/read/Products"
            "?type=Products_nd_associated_Brands"
            "&order=product_scoring__DESC"
            f"&filter={filter_key}&filterValue={category_id}"
            f"&offset={offset}&limit={LIMIT}"
            "&filter=active&filterValue=true"
            "&filter=storeId&filterValue=10"
            "&filter=!url&filterValue=!null"
            "&filter=Op.available_stock&filterValue=Op.gt__0"
        )
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"Error fetching products for {filter_key}={category_id} offset {offset}: {e}")
            break

        items = data.get("data", [])
        if not items:
            break

        for item in items:
            name = item.get("product_name", "").strip()
            price = item.get("sale_price") or item.get("price") or "N/A"
            if name:
                products.append((name, price))

        if len(items) < LIMIT:
            break

        offset += LIMIT
        time.sleep(0.3)

    return products

def fetch_all_products(category_id, category_path, cur):
    seen = set()
    for filter_key in FILTER_KEYS:
        print(f"    Fetching products with filter '{filter_key}' for category ID {category_id}...")
        prods = fetch_products_for_filter(category_id, filter_key)
        for name, price in prods:
            if name not in seen:
                seen.add(name)
                cur.execute("""
                    INSERT INTO scrapped_products (Name, Price, Source, ScrapDate)
                    VALUES (%s, %s, %s, %s)
                """, (name, float(price) if price != "N/A" else 0.0, " > ".join(category_path), datetime.now()))
        time.sleep(0.3)

def recursive_scrape(categories, parent_id=None, path=None, cur=None):
    if path is None:
        path = []

    children = get_children(categories, parent_id)

    if not children:
        if parent_id is None:
            return
        print(f"  Leaf category reached: {' > '.join(path)} - fetching products...")
        fetch_all_products(parent_id, path, cur)
        return

    for child in children:
        child_name = child.get("category_name", "").strip()
        child_id = child.get("id")
        print(f"  Descending into category: {' > '.join(path + [child_name])}")
        recursive_scrape(categories, child_id, path + [child_name], cur)

#  main
def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    categories = fetch_categories()
    if not categories:
        print("⚠ No categories found, exiting.")
        return

    top_categories = [cat for cat in categories if cat.get("parentId") is None]
    print(f"Found {len(top_categories)} top-level categories.")

    for top_cat in top_categories:
        top_name = top_cat.get("category_name", "").strip()
        top_id = top_cat.get("id")
        print(f"Starting scrape for top category: {top_name}")
        recursive_scrape(categories, top_id, [top_name], cur)

    conn.commit()
    cur.close()
    conn.close()
    print("Scraping completed and data inserted into db")

if __name__ == "__main__":
    main()
