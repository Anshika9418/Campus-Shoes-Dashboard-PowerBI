# Campus-Shoes-Dashboard-PowerBI

## Project Overview
This project analyzes and visualizes data of men’s Campus shoes collected from 
Amazon, Flipkart, and the Campus website.
The goal is to provide insights on sales trends, pricing, ratings,
and inventory through an interactive Power BI dashboard.

---

## Project Workflow

### 1. Data Collection
- Web scraped data from Amazon, Flipkart, and the Campus official website.
- Focused on **men’s Campus shoes**.
- Collected key attributes like:
  - Product Name
  - Price
  - Ratings
  - Number of Reviews
  - Availability/Stock

### 2. Data Cleaning & Processing (Python)
- Removed duplicates and missing values.
- Standardized price formats, ratings, and product categories.
- Processed the data using Python libraries:
  - `pandas` for data manipulation
  - `numpy` for numerical operations
  - `BeautifulSoup` / `requests` for web scraping
- Saved the cleaned dataset as a CSV for Power BI visualization.

### 3. Dashboard Creation (Power BI)
- Built an **interactive dashboard** to analyze:
  - Total sales across platforms
  - Price distribution
  - Product ratings and reviews
  - Inventory status
  - Comparison of products across Amazon, Flipkart, and Campus website
- Used **Power BI features** such as slicers, filters, and charts for user-friendly navigation.

### 4. Insights & Analysis
- Identified trends in pricing and top-rated products.
- Compared sales and popularity across different platforms.
- Highlighted products with high demand or high ratings.

---

## Tech Stack
- **Python:** Data cleaning, processing, and web scraping  
- **Power BI:** Dashboard creation and visualization  
- **Libraries Used:** `pandas`, `numpy`, `BeautifulSoup`, `requests`  
- **Data Sources:** Amazon, Flipkart, Campus website  

---

## How to Use
1. Download the **PBIX file** to open in Power BI Desktop.
2. Explore the dashboard interactively with slicers and filters.
3. Refer to the cleaned CSV file for data analysis in Python or other tools.

---

## Key Learnings
- Hands-on experience with **web scraping** and **data cleaning** in Python.  
- Learned to create **interactive dashboards** in Power BI.  
- Improved skills in **data visualization**, storytelling, and extracting actionable insights from datasets.  

---

## Future Improvements
- Automate data scraping to update the dashboard regularly.  
- Integrate additional platforms or product categories.  
- Implement predictive analytics to forecast sales trends.  
