Campus Men’s Shoes Data Analysis & Power BI Dashboard
📌 Project Overview

This project focuses on analyzing men’s footwear products across multiple e-commerce platforms to understand pricing patterns, customer engagement, and platform performance.
The end goal was to convert raw, unstructured data into actionable business insights using SQL and Power BI.

🔍 Data Collection (Web Scraping)

Product data was scraped from multiple e-commerce platforms (Campus, Amazon, Flipkart)

Collected attributes include:

Product name

Price & MRP

Discount

Customer reviews

Ratings

Product URL

Platform name

Data was stored in a MySQL database for further processing

🗄️ Data Storage (SQL)

Designed structured tables in MySQL

Inserted scraped data into relational tables

Ensured consistent schema for multi-platform comparison

🧹 Data Cleaning & Transformation (SQL)

Performed extensive data cleaning using SQL:

Removed duplicates

Handled missing and null values

Standardized price and discount formats

Converted text-based numeric columns into usable numeric fields

Created calculated columns such as:

Price buckets

Discount flags

Engagement-related metrics

📊 Data Modeling & Analysis

Connected MySQL database to Power BI

Built relationships between tables

Created calculated measures using DAX, including:

Average Selling Price

Customer Engagement

Reviews per Product (Efficiency)

Segmented products by price range for deeper analysis

📈 Dashboard Features (Power BI)

The interactive dashboard provides:

KPI cards for:

Total Products

Average Selling Price

Average Rating

Total Reviews

Platform-wise performance comparison

Price vs Reviews relationship analysis

Customer engagement analysis by price segment

Top 5 products by customer engagement

Most common shoe categories

Dynamic filters for platform, price, and rating

Advanced tooltips with product-level details

Dynamic product link button that opens the selected product’s URL reminder

💡 Key Insights

Campus dominates in both product volume and customer engagement

Mid-priced shoes (₹1000–₹1500) receive the highest customer engagement

Higher-priced products tend to receive fewer reviews

Certain products consistently outperform others across platforms

