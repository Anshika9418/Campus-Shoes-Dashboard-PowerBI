import time
import random
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

BASE_URL = "https://www.amazon.in/s?k=campus+shoes+for+men"
CSV_PATH = "C:/Users/anshi/OneDrive/Desktop/AMAZON_CAMPUS_MENS_SHOES_FINAL.csv"

all_products = []
scraped_urls = set()

options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

def extract_price(soup):
    off = soup.select_one("span.a-price > span.a-offscreen")
    if off and off.get_text(strip=True) != "":
        return off.get_text(strip=True)
    whole = soup.select_one("span.a-price-whole")
    fraction = soup.select_one("span.a-price-fraction")
    if whole and fraction:
        return f"₹{whole.get_text(strip=True)}.{fraction.get_text(strip=True)}"
    if whole:
        return f"₹{whole.get_text(strip=True)}"
    hidden = soup.select_one("span.a-offscreen")
    if hidden and hidden.get_text(strip=True) != "":
        return hidden.get_text(strip=True)
    return "N/A"

def clean_rating(soup):
    rating_tag = soup.select_one("span.a-icon-alt")
    if rating_tag:
        text = rating_tag.get_text(strip=True)
        if text[0].isdigit():
            return text.split()[0]
    return "No Rating"

def clean_reviews(soup):
    reviews_tag = soup.select_one("#acrCustomerReviewText")
    if reviews_tag:
        text = reviews_tag.get_text(strip=True).split()[0]
        if text.isdigit():
            return text
    return "No Reviews"

page_num = 1
max_pages = 17
while page_num <= max_pages:
    url = f"{BASE_URL}&page={page_num}"
    print(f"\n🔍 Scraping Page {page_num} → {url}")
    driver.get(url)

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.s-main-slot div[data-asin]"))
        )
    except:
        print("⚠ Timeout waiting for search results — skipping page")
        page_num += 1
        continue

    soup = BeautifulSoup(driver.page_source, "html.parser")
    products = soup.select("div.s-main-slot div[data-asin]")

    if not products:
        print("⚠ No products found — stopping.")
        break

    for product in products:
        try:
            asin = product.get("data-asin")
            if not asin:
                continue

            link_tag = product.select_one("a.a-link-normal.s-no-outline")
            if not link_tag:
                continue

            product_url = "https://www.amazon.in" + link_tag["href"]

            if product_url in scraped_urls:
                continue
            scraped_urls.add(product_url)

            driver.get(product_url)
            try:
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.ID, "productTitle"))
                )
            except:
                print("⚠ Timeout waiting for product page, parsing anyway")

            soup2 = BeautifulSoup(driver.page_source, "html.parser")

            name = soup2.select_one("#productTitle")
            name = name.get_text(strip=True) if name else "N/A"

            price = extract_price(soup2)
            mrp_tag = soup2.select_one("span.a-text-price span.a-offscreen")
            mrp = mrp_tag.get_text(strip=True) if mrp_tag else price

            discount_tag = soup2.select_one("span.savingsPercentage")
            discount_percent = discount_tag.get_text(strip=True) if discount_tag else "No Discount"

            image_tag = soup2.select_one("img#landingImage")
            image = image_tag["src"] if image_tag else "N/A"

            desc_tag = soup2.select_one("#feature-bullets ul")
            description = desc_tag.get_text(" ", strip=True) if desc_tag else "N/A"

            sizes_raw = soup2.select("#tp-inline-twister-dim-values-container li")
            sizes = [s.get_text(strip=True) for s in sizes_raw if s.get_text(strip=True).endswith("UK")]
            sizes_str = ", ".join(sizes) if sizes else "Not Available"

            # ---------------- COLORS ----------------
            try:
                color_buttons = driver.find_elements(By.CSS_SELECTOR, "div#variation_color_name ul li")
            except:
                color_buttons = []

            if color_buttons:
                for idx, color_button in enumerate(color_buttons):
                    try:
                        input_tag = color_button.find_element(By.TAG_NAME, "input")
                        driver.execute_script("arguments[0].click();", input_tag)
                        time.sleep(random.uniform(1.5, 2.5))  # wait for page update

                        soup_color = BeautifulSoup(driver.page_source, "html.parser")

                        current_color_tag = soup_color.select_one("span#inline-twister-expanded-dimension-text-color_name")
                        color_name_final = current_color_tag.get_text(strip=True) if current_color_tag else f"Color {idx+1}"

                        # ✅ Split combined colors into separate rows
                        colors_clean = [c.strip() for c in color_name_final.replace('/', ',').split(',')]

                        price = extract_price(soup_color)
                        mrp_tag = soup_color.select_one("span.a-text-price span.a-offscreen")
                        mrp = mrp_tag.get_text(strip=True) if mrp_tag else price
                        discount_tag = soup_color.select_one("span.savingsPercentage")
                        discount_percent = discount_tag.get_text(strip=True) if discount_tag else "No Discount"
                        rating = clean_rating(soup_color)
                        reviews = clean_reviews(soup_color)

                        for single_color in colors_clean:
                            all_products.append({
                                "ASIN": asin,
                                "URL": product_url,
                                "Name": name,
                                "Price": price,
                                "M.R.P": mrp,
                                "Discount": discount_percent,
                                "Image_URL": image,
                                "Description": description,
                                "Sizes": sizes_str,
                                "Colors": single_color,   # ✅ one color per row
                                "Rating": rating,
                                "Reviews": reviews
                            })

                            print(f"✔ {name} | Price {price} | MRP {mrp} | {discount_percent} | Color {single_color} | Sizes {sizes_str} | Rating {rating} | Reviews {reviews}")

                    except Exception as e:
                        print("⚠ Error with color:", e)
            else:
                soup_color = soup2
                current_color_tag = soup_color.select_one("span#inline-twister-expanded-dimension-text-color_name")
                color_name_final = current_color_tag.get_text(strip=True) if current_color_tag else "Not Available"

                colors_clean = [c.strip() for c in color_name_final.replace('/', ',').split(',')]

                for single_color in colors_clean:
                    all_products.append({
                        "ASIN": asin,
                        "URL": product_url,
                        "Name": name,
                        "Price": price,
                        "M.R.P": mrp,
                        "Discount": discount_percent,
                        "Image_URL": image,
                        "Description": description,
                        "Sizes": sizes_str,
                        "Colors": single_color,
                        "Rating": clean_rating(soup_color),
                        "Reviews": clean_reviews(soup_color)
                    })

                    print(f"✔ {name} | Price {price} | MRP {mrp} | {discount_percent} | Color {single_color} | Sizes {sizes_str} | Rating {clean_rating(soup_color)} | Reviews {clean_reviews(soup_color)}")

        except Exception as e:
            print("⚠ Error:", e)
            continue

    df = pd.DataFrame(all_products)
    df.to_csv(CSV_PATH, index=False, encoding="utf-8-sig")
    print(f"💾 SAVED — {len(all_products)} products so far")

    page_num += 1
    time.sleep(random.uniform(2, 4))

driver.quit()
print(f"\n🎉 DONE — TOTAL {len(all_products)} unique products saved successfully!")