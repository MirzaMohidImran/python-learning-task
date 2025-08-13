import requests
import csv
import time

CATEGORIES_API = "https://admin.metro-online.pk/api/read/Categories?filter=storeId&filterValue=10"

LIMIT = 500  # API max limit per request

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
            break  # No more pages

        offset += LIMIT
        time.sleep(0.3)  # delay

    return products

def fetch_all_products(category_id):
    seen = set()
    all_products = []

    for filter_key in FILTER_KEYS:
        print(f"    Fetching products with filter '{filter_key}' for category ID {category_id}...")
        prods = fetch_products_for_filter(category_id, filter_key)
        for name, price in prods:
            if name not in seen:
                seen.add(name)
                all_products.append((name, price))
        time.sleep(0.3)

    return all_products

def recursive_scrape(categories, parent_id=None, path=None, all_rows=None):
    if path is None:
        path = []
    if all_rows is None:
        all_rows = []

    children = get_children(categories, parent_id)

    if not children:
        # leaf category: fetch all products for this category via all filters
        if parent_id is None:
            return all_rows  # no categories, no products
        print(f"  Leaf category reached: {' > '.join(path)} - fetching products...")
        products = fetch_all_products(parent_id)
        for name, price in products:
            all_rows.append(path + [name, price])
        return all_rows

    for child in children:
        child_name = child.get("category_name", "").strip()
        child_id = child.get("id")
        print(f"  Descending into category: {' > '.join(path + [child_name])}")
        recursive_scrape(categories, child_id, path + [child_name], all_rows)

    return all_rows

def main():
    categories = fetch_categories()
    if not categories:
        print("⚠ No categories found, exiting.")
        return

    top_categories = [cat for cat in categories if cat.get("parentId") is None]
    print(f"Found {len(top_categories)} top-level categories.")

    all_data = []

    for top_cat in top_categories:
        top_name = top_cat.get("category_name", "").strip()
        top_id = top_cat.get("id")
        print(f"Starting scrape for top category: {top_name}")
        all_data.extend(recursive_scrape(categories, top_id, [top_name]))

    max_depth = 0
    for row in all_data:
        depth = len(row) - 2
        if depth > max_depth:
            max_depth = depth

    headers = [f"Category Level {i+1}" for i in range(max_depth)] + ["Product Name", "Product Price"]

    with open("metro_complete_products.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for row in all_data:
            cat_levels = row[:-2]
            product_name = row[-2]
            product_price = row[-1]
            padded = cat_levels + [""] * (max_depth - len(cat_levels)) + [product_name, product_price]
            writer.writerow(padded)

    print(f"Scraped {len(all_data)} products. Saved to metro_complete_products.csv")

if __name__ == "__main__":
    main()
