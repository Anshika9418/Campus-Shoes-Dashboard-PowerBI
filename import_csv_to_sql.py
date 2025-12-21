# import_csv_to_sql.py — FINAL SAFE VERSION (HANDLES 'nan' COLUMNS + NO DUPLICATES)
import pandas as pd
import mysql.connector
import glob
import os
import getpass

def clean_price(val):
    if pd.isna(val) or val in (None, "", "N/A", "Not Available"):
        return None
    try:
        return float(str(val).replace("₹", "").replace(",", "").strip())
    except:
        return None

def clean_float(val):
    if pd.isna(val) or val in (None, "", "N/A", "Not Available"):
        return None
    try:
        return float(str(val).split()[0])
    except:
        return None

def clean_int(val):
    if pd.isna(val) or val in (None, "", "N/A", "Not Available"):
        return None
    try:
        return int(str(val).replace(",", "").split()[0])
    except:
        return None

csv_folder = "C:/Users/anshi/OneDrive/Desktop/Just"
csv_files = glob.glob(os.path.join(csv_folder, "*.csv"))

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password=("enter your password"),
    database="shoes_data",
    port=3306
)
cursor = conn.cursor()

new = 0
skipped = 0

for file in csv_files:
    print(f"\nProcessing: {os.path.basename(file)}")
    try:
        df = pd.read_csv(file)
    except Exception as e:
        print(f"Cannot read CSV: {e}")
        continue

    # === FIX 'nan' COLUMNS ===
    df = df.loc[:, df.columns.notna()]  # remove NaN column names
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]  # remove Unnamed: 0 etc.
    df.columns = [str(col).strip() for col in df.columns]  # clean column names

    # Detect platform
    filename = os.path.basename(file).upper()
    if "AMAZON" in filename:
        platform = "AMAZON"
    elif "FLIPKART" in filename:
        platform = "FLIPKART"
    elif "CAMPUS" in filename:
        platform = "CAMPUS"
    else:
        platform = "UNKNOWN"

    df["Platform"] = platform

    for _, row in df.iterrows():
        url = str(row.get("URL", "")).strip()
        if not url or url in ("nan", "None"):
            continue

        unique_id = url

        try:
            sql = """
            INSERT IGNORE INTO products 
            (URL, Name, Price, MRP, Discount, Image_URL, Description, Sizes, Colors, Rating, Reviews, Platform, unique_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                url,
                str(row.get("Name", "Not Available")),
                clean_price(row.get("Price")),
                clean_price(row.get("M.R.P") or row.get("MRP")),
                str(row.get("Discount", "No Discount")),
                str(row.get("Image_URL", "Not Available")),
                str(row.get("Description", "Not Available")),
                str(row.get("Sizes", "Not Available")),
                str(row.get("Colors", "Not Available")),
                clean_float(row.get("Rating")),
                clean_int(row.get("Reviews")),
                platform,
                unique_id
            )
            cursor.execute(sql, values)
            if cursor.rowcount == 1:
                new += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"Row error: {e}")

conn.commit()
cursor.close()
conn.close()

print(f"\nDONE!")
print(f"New products added: {new}")
print(f"Duplicates skipped: {skipped}")
print("Amazon data should now be in your table!")