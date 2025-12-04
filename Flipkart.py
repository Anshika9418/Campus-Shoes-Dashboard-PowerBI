import time
import json
import pandas as pd
from bs4 import BeautifulSoup
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth

BASE_URL = "https://www.flipkart.com/search?q=campus+shoes+for+men"
CSV_PATH = "C:/Users/anshi/OneDrive/Desktop/FLIPKART_CAMPUS_FINAL.csv"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36"
}

options = uc.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
driver = uc.Chrome(options=options)

stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL",
        fix_hairline=True)

wait = WebDriverWait(driver, 5)
all_products = []
seen_pids = set()  # track product IDs to avoid duplicates


def extract_sizes_and_colors(driver):
    # --- SIZE extraction (your original working logic) ---
    sizes = []
    try:
        size_section = driver.find_element(
            By.XPATH,
            "//div[.//div[contains(normalize-space(text()),'Size')]]"
        )
        size_opts = size_section.find_elements(
            By.XPATH,
            ".//*[contains(@class,'HduqIE') and contains(@class,'WLkY3m')]"
        )
        sizes = [o.text.strip() for o in size_opts if o.text.strip()]
    except:
        sizes = []

    sizes = [f"{s} UK" for s in sizes]
    sizes = list(dict.fromkeys(sizes))
    sizes_str = ", ".join(sizes) if sizes else "Not Available"

    # --- COLOR extraction (fixed: strictly scoped to Color section) ---
    colors = []
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # 1) Find the "Color" header and scope to its nearest container
    color_header = soup.find(["div", "span"], string=lambda s: isinstance(s, str) and "Color" in s)
    if color_header:
        # Prefer the smallest meaningful parent to avoid whole-page text
        parent = color_header.find_parent()
        if parent:
            # a) Swatch images: <div class="_2C41yO"><img alt="Black" ... /></div>
            for img in parent.select("div._2C41yO img"):
                v = img.get("alt") or img.get("title")
                if v and v.strip():
                    colors.append(v.strip())

            # b) Attribute-based fallback inside the same color section
            if not colors:
                for el in parent.select("[data-color], [aria-label], [title], img[alt], img[title]"):
                    v = el.get("data-color") or el.get("aria-label") or el.get("title") or el.get("alt")
                    if v and v.strip():
                        colors.append(v.strip())

            # c) Minimal text fallback for short labels within swatches
            if not colors:
                for el in parent.select("button, a, div"):
                    txt = el.get_text(strip=True)
                    if txt and len(txt) <= 25 and "size" not in txt.lower() and "chart" not in txt.lower():
                        colors.append(txt)

    # 2) If header not found, attempt global swatch class (kept tight to swatches)
    if not colors:
        for img in soup.select("div._2C41yO img"):
            v = img.get("alt") or img.get("title")
            if v and v.strip():
                colors.append(v.strip())

    # Cleanup: remove noise and duplicates
    colors = [c for c in colors if c]
    colors = [c for c in colors
              if len(c) <= 25
              and "add to cart" not in c.lower()
              and "buy now" not in c.lower()
              and "offer" not in c.lower()
              and "explore" not in c.lower()
              and "flipkart" not in c.lower()]
    colors = list(dict.fromkeys(colors))
    colors_str = ", ".join(colors) if colors else "Not Available"

    return sizes_str, colors_str


def extract_discount(driver, price, mrp):
    try:
        elem = driver.find_elements(By.XPATH, "//span[contains(text(),'% off')]")
        if elem:
            return elem[0].text.strip()
        if price != mrp and price not in ("Not Available", None) and mrp not in ("Not Available", None):
            return f"-{round((float(mrp) - float(price)) / float(mrp) * 100)}%"
    except:
        pass
    return "-"


def extract_from_json(product_url):
    res = requests.get(product_url, headers=headers, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")
    block = soup.find("script", {"type": "application/ld+json"})
    if not block:
        return None

    data = json.loads(block.text)
    pdata = None

    if isinstance(data, dict):
        pdata = data
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and item.get("name"):
                pdata = item
                break

    if pdata is None:
        return None

    return (
        pdata.get("name", "Not Available"),
        pdata.get("offers", {}).get("price", "Not Available"),
        pdata.get("offers", {}).get("price", "Not Available"),
        pdata.get("image", "Not Available"),
        pdata.get("description", "Not Available"),
        pdata.get("aggregateRating", {}).get("ratingValue", "Not Available"),
        pdata.get("aggregateRating", {}).get("reviewCount", "Not Available")
    )


# detect total pages
driver.get(BASE_URL)
time.sleep(2)
soup = BeautifulSoup(driver.page_source, "html.parser")
page_numbers = [int(p.get_text()) for p in soup.select("nav a") if p.get_text().isdigit()]
max_pages = max(page_numbers) if page_numbers else 1
print(f"📄 Detected {max_pages} pages to scrape")

for page in range(1, max_pages + 1):
    full_url = BASE_URL + f"&page={page}"
    print(f"\n🔍 Scraping Page {page} → {full_url}")
    driver.get(full_url)
    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    products = soup.select("a[href*='/p/']")
    if not products:
        print("⚠ No more products found — scraping finished.")
        break

    for p in products:
        href = p.get("href", "")
        # extract PID and deduplicate
        pid = None
        if "pid=" in href:
            try:
                pid = href.split("pid=")[1].split("&")[0]
            except:
                pid = None
        if pid and pid in seen_pids:
            continue
        if pid:
            seen_pids.add(pid)

        # Build canonical product URL (strip trailing params after pid)
        base = href.split("&pid=")[0]
        url = "https://www.flipkart.com" + base

        driver.get(url)

        try:
            wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(@class,'_2c7YLP') or contains(@class,'_1AtVbE')]")))
        except:
            pass

        json_data = extract_from_json(url)
        if not json_data:
            continue

        name, price, mrp, image, desc, rating, reviews = json_data
        sizes, colors = extract_sizes_and_colors(driver)
        discount = extract_discount(driver, price, mrp)

        product = {
            "URL": url,
            "Name": name,
            "Price": price,
            "M.R.P": mrp,
            "Discount": discount,
            "Image_URL": image,
            "Description": desc,
            "Sizes": sizes,
            "Colors": colors,
            "Rating": rating,
            "Reviews": reviews,
        }
        all_products.append(product)

        print(
            f"✔ {name} | Price ₹{price} | MRP ₹{mrp} | {discount} | "
            f"Color {colors} | Sizes {sizes} | Rating {rating} | Reviews {reviews}"
        )

    pd.DataFrame(all_products).to_csv(CSV_PATH, index=False, encoding="utf-8-sig")
    print(f"💾 Saved {len(all_products)} products so far")

driver.quit()
print(f"\n🎉 DONE — TOTAL {len(all_products)} Flipkart products scraped successfully!")