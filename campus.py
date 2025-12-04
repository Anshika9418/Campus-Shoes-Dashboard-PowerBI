import time
import random
import pandas as pd
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

BASE_URL = "https://www.campusshoes.com/collections/mens-footwear"

# 📌 Change ONLY this file name when you want a new CSV
CSV_PATH = "C:/Users/anshi/OneDrive/Desktop/CAMPUS_MENS_SHOES_FINAL.csv"

all_products = []
scraped_urls = set()

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/122 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/14 Safari/605.1.15",
]

options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

def get_product_data(driver, product_url, handle):
    """Fetches all data for a single product from its URL and .js endpoint."""
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    api_url = f"https://www.campusshoes.com/products/{handle}.js"
    raw = requests.get(api_url, headers=headers, timeout=20).json()

    name = raw["title"]
    price = raw["price"] / 100
    mrp = raw["compare_at_price"] / 100 if raw.get("compare_at_price") else price
    discount_percent = f"{round((mrp - price) / mrp * 100)}% OFF" if mrp > price else "No Discount"

    image = raw.get("images", [None])[0] or "N/A"
    description = BeautifulSoup(raw.get("description", ""), "html.parser").get_text(strip=True)

    sizes = sorted({v.get("option2") for v in raw.get("variants", []) if v.get("option2")})
    colors = sorted({v.get("option1") for v in raw.get("variants", []) if v.get("option1")})

    # ⭐ Rating + Reviews (requires Selenium)
    driver.get(product_url)
    try:
        rating_element = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".jdgm-prev-badge"))
        )
        soup2 = BeautifulSoup(driver.page_source, "html.parser")
        rating = soup2.select_one(".jdgm-prev-badge__stars")["data-score"]
        reviews = soup2.select_one(".jdgm-prev-badge__text").get_text(strip=True)
    except Exception:
        rating = "No Rating"
        reviews = "No Reviews"

    return {
        "URL": product_url,
        "Name": name,
        "Price": f"₹{price:.2f}",
        "M.R.P": f"₹{mrp:.2f}",
        "Discount": discount_percent,
        "Image_URL": image,
        "Description": description,
        "Sizes": ", ".join(sizes) if sizes else "Not Available",
        "Colors": ", ".join(colors) if colors else "Not Available",
        "Rating": rating,
        "Reviews": reviews,
    }

page_num = 1
max_pages = 36

while page_num <= max_pages:
    url = f"{BASE_URL}?page={page_num}"
    print(f"\n🔍 Scraping Page {page_num} → {url}")
    driver.get(url)

    WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[data-product-id]"))
    )

    soup = BeautifulSoup(driver.page_source, "html.parser")
    products = soup.select("div[data-product-id]")

    if not products:
        print("⚠ No products found — stopping.")
        break

    for product in products:
        try:
            link = product.select_one('a[href*="/products/"]')["href"]
            handle = link.split("/")[-1].strip()
            product_url = f"https://www.campusshoes.com/products/{handle}"

            if product_url in scraped_urls:
                continue
            scraped_urls.add(product_url)

            headers = {"User-Agent": random.choice(USER_AGENTS)}
            api_url = f"https://www.campusshoes.com/products/{handle}.js"
            raw = requests.get(api_url, headers=headers, timeout=20).json()
            product_details = get_product_data(driver, product_url, handle)
            all_products.append(product_details)

            name = raw["title"]
            price = raw["price"] / 100
            mrp = raw["compare_at_price"] / 100 if raw["compare_at_price"] else price
            discount_percent = f"{round((mrp - price) / mrp * 100)}% OFF" if mrp > price else "No Discount"
            # Print statement now uses the dictionary for consistency
            print(f"✔ {product_details['Name']} | Price {product_details['Price']} | Colors {product_details['Colors']} | Rating {product_details['Rating']}")

            image = raw["images"][0] if raw.get("images") else "N/A"
            description = BeautifulSoup(raw.get("description", ""), "html.parser").get_text(strip=True)

            sizes = sorted({v.get("option2") for v in raw["variants"] if v.get("option2")})
            colors = sorted({v.get("option1") for v in raw["variants"] if v.get("option1")})

            sizes_str = ", ".join(sizes) if sizes else "Not Available"
            colors_str = ", ".join(colors) if colors else "Not Available"

            # ⭐ Rating + Reviews
            driver.get(product_url)
            try:
                rating_element = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".jdgm-prev-badge"))
                )
                soup2 = BeautifulSoup(driver.page_source, "html.parser")
                rating = soup2.select_one(".jdgm-prev-badge__stars")["data-score"]
                reviews = soup2.select_one(".jdgm-prev-badge__text").get_text(strip=True)
            except:
                rating = "No Rating"
                reviews = "No Reviews"

            all_products.append({
                "URL": product_url,
                "Name": name,
                "Price": f"₹{price:.2f}",
                "M.R.P": f"₹{mrp:.2f}",
                "Discount": discount_percent,
                "Image_URL": image,
                "Description": description,
                "Sizes": sizes_str,
                "Colors": colors_str,
                "Rating": rating,
                "Reviews": reviews
            })

            print(f"✔ {name} | Price ₹{price:.2f} | MRP ₹{mrp:.2f} | {discount_percent} | Colors {colors_str} | Sizes {sizes_str} | Rating {rating} | {reviews}")

            time.sleep(random.uniform(0.7, 1.3))

        except Exception as e:
            print("⚠ Error:", e)
            continue

    # 💾 SAVE CSV AFTER EVERY PAGE (so data won't be lost)
    df = pd.DataFrame(all_products)
    df.to_csv(CSV_PATH, index=False, encoding="utf-8-sig")
    print(f"💾 SAVED — {len(all_products)} products so far")

    page_num += 1
    time.sleep(random.uniform(2, 4))

driver.quit()
print(f"\n🎉 DONE — TOTAL {len(all_products)} unique products saved successfully!")
