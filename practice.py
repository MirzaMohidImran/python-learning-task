import requests
from bs4 import BeautifulSoup

url = "https://www.rahimstore.com/index"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    )
}

response = requests.get(url, headers=headers)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")
print(soup.prettify()[:10000000000])

product_found = False
for item in soup.select("div.item"):
    name_tag = item.select_one("p > a[href^='https://www.rahimstore.com/product/']")
    name = name_tag.get_text(strip=True) if name_tag else None

    button_tag = item.select_one("button[data]")
    if button_tag:
        data_string = button_tag.get("data")
        parts = data_string.split("~")
        if len(parts) >= 3:
            price = parts[2]

            if name and price:
                print(f"{name} — Rs. {price}")
                product_found = True

if product_found:
    print(" Scraping completed successfully.")
else:
    print(" No products found. Check selectors or structure.")
