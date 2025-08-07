import requests
import csv

# API Endpoint 
url = "https://shop.imtiaz.com.pk/api/items-by-subsection"

# API Query Parameters 
params = {
    'restId': '55126',
    'rest_brId': '54934',
    'sub_section_id': '43239',  # category
    'delivery_type': '0',
    'source': '',
    'brand_name': '',
    'min_price': '0',
    'max_price': '',
    'sort_by': '',
    'sort': '',
    'page_no': '1',
    'per_page': '24',
    'start': '0',
    'limit': '24',
}

# Request Headers 
headers = {
    'sec-ch-ua-platform': '"Windows"',
    'App-name': 'imtiazsuperstore',
    'Referer': 'https://shop.imtiaz.com.pk/catalog/health--beauty-4101/oral-care-40581/mouthwash-43239',
    'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
    'Rest-Id': '55126',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
}

#  API Request 
response = requests.get(url, params=params, headers=headers)

#  Check Errors 
if response.status_code != 200:
    print(" Failed to fetch data:", response.status_code)
    print("Response:", response.text)
    exit()

#  JSON Data 
data = response.json()
products = data.get("data", [])

#First Product Debugging
if products:
    print("First product sample:")
    print(products[0])

# Save CSV
with open("imtiaz_products.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["Product Name", "Price"])
    writer.writeheader()

    for product in products:
        writer.writerow({
            "Product Name": product.get("item_name") or product.get("name") or product.get("title") or "N/A",
            "Price": f"Rs. {product.get('price', '0')}"
        })

print(f" {len(products)} products saved to imtiaz_products.csv")
