import requests
import csv
import time

# API URL
CATEGORIES_API = "https://admin.metro-online.pk/api/read/Categories?filter=storeId&filterValue=10"
PRODUCTS_API_TEMPLATE = (
    "https://admin.metro-online.pk/api/read/Products"
    "?type=Products_nd_associated_Brands"
    "&order=product_scoring__DESC"
    "&filter=promotion_tier2_id&filterValue={category_id}"
    "&offset=0&limit=500"  # Increase product limit 
    "&filter=active&filterValue=true"
    "&filter=storeId&filterValue=10"
    "&filter=!url&filterValue=!null"
    "&filter=Op.available_stock&filterValue=Op.gt__0"
)

def fetch_categories():
    resp = requests.get(CATEGORIES_API)
    resp.raise_for_status()
    data = resp.json()
    return data["data"]

def get_subcategories(data):
    """Return all categories that have a parentId (subcategories)."""
    return [cat for cat in data if cat.get("parentId") is not None]

def fetch_products_for_category(category_id):
    url = PRODUCTS_API_TEMPLATE.format(category_id=category_id)
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    if "data" in data:
        data = data["data"]
    return [
        {
            "name": item.get("product_name", "").strip(),
            "price": item.get("sale_price", item.get("price")),
        }
        for item in data
        if item.get("product_name")
    ]

def main():
    categories = fetch_categories()
    subcategories = get_subcategories(categories)

    all_products = []

    for sub in subcategories:
        sub_name = sub.get("category_name", "").strip()
        sub_id = sub.get("id")
        print(f" Fetching products for: {sub_name} (ID: {sub_id})")

        try:
            products = fetch_products_for_category(sub_id)
        except Exception as e:
            print(f"⚠ Error fetching {sub_name}: {e}")
            continue

        for p in products:
            all_products.append([sub_name, p["name"], p["price"]])

        time.sleep(0.5)  # avoid hitting server too fast

    # Save  CSV
    with open("metro_products.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Subcategory", "Product Name", "Product Price"])
        writer.writerows(all_products)

    print(f"Saved {len(all_products)} products to metro_products.csv")

if __name__ == "__main__":
    main()
