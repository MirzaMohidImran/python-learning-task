import requests
import csv

API_URL = "https://admin.metro-online.pk/api/read/Categories?filter=storeId&filterValue=10"

def fetch_categories():
    resp = requests.get(API_URL)
    resp.raise_for_status()
    return resp.json()

def build_category_structure(data):
    """Return a dict: {main_category: [subcategories]}"""
    structure = {}

    # Get top categ
    top_categories = [cat for cat in data if cat.get("parentId") is None]

    for top in top_categories:
        top_name = top.get("category_name", "").strip()
        top_id = top.get("id")

        # Find subcate
        subcats = [
            sub.get("category_name", "").strip()
            for sub in data
            if sub.get("parentId") == top_id
        ]

        structure[top_name] = subcats

    return structure

def save_to_csv(structure, filename="metro_categories.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Main Category", "Subcategory"])
        for main_cat, subcats in structure.items():
            if subcats:
                for sub in subcats:
                    writer.writerow([main_cat, sub])
            else:
                writer.writerow([main_cat, ""])
    print(f"Saved to {filename}")

if __name__ == "__main__":
    json_data = fetch_categories()

    # API response "data"
    if isinstance(json_data, dict) and "data" in json_data:
        json_data = json_data["data"]

    category_structure = build_category_structure(json_data)

    # Print terminal
    for main_cat, subcats in category_structure.items():
        print(f"\n=== {main_cat} ===")
        if subcats:
            for sub in subcats:
                print("  ->", sub)
        else:
            print("  (No subcategories)")

    # Save CSV
    save_to_csv(category_structure)
