use shoes_data;
select * from products;
select count(*)from products group by platform;


WITH ranked_products AS (
    SELECT
        id,
        ROW_NUMBER() OVER (
            PARTITION BY Platform, URL
            ORDER BY scraped_at DESC
        ) AS rn
    FROM products
)
DELETE FROM products
WHERE id IN (
    SELECT id
    FROM ranked_products
    WHERE rn > 1
);


SET SQL_SAFE_UPDATES = 0;
-- CLEAN PRICE (SAFE-MODE FRIENDLY)
UPDATE products
SET Price = CAST(
    NULLIF(
        REPLACE(REPLACE(Price, '₹', ''), ',', ''),
        ''
    ) AS DECIMAL(10,2)
)
WHERE id IS NOT NULL;

-- CLEAN MRP
UPDATE products
SET MRP = CAST(
    NULLIF(
        REPLACE(REPLACE(MRP, '₹', ''), ',', ''),
        ''
    ) AS DECIMAL(10,2)
)
WHERE id IS NOT NULL;


-- CLEAN DISCOUNT
UPDATE products
SET Discount = NULL
WHERE id IS NOT NULL
  AND Discount IN ('No Discount', '', 'N/A');
  
  
  -- CLEAN RATING
UPDATE products
SET Rating = NULL
WHERE id IS NOT NULL
  AND (Rating <= 0 OR Rating > 5);
  
 -- CLEAN REVIEWS
UPDATE products
SET Reviews = NULL
WHERE id IS NOT NULL
  AND Reviews < 0;
  
-- CLEAN SIZES
UPDATE products
SET Sizes = NULL
WHERE id IS NOT NULL
  AND Sizes IN ('Not Available', '', 'N/A');


-- cLEAN COLORS
UPDATE products
SET Colors = NULL
WHERE id IS NOT NULL
  AND Colors IN ('Not Available', '', 'N/A');
  
  -- REMOVE DUPLICATES (SAFE MODE FRIENDLY)
DELETE FROM products
WHERE id IN (
    SELECT id FROM (
        SELECT
            id,
            ROW_NUMBER() OVER (
                PARTITION BY Platform, URL
                ORDER BY scraped_at DESC
            ) AS rn
        FROM products
    ) t
    WHERE rn > 1
);

-- VERIFY EVERYTHING
SELECT
    Platform,
    COUNT(*) AS total_rows,
    COUNT(Price) AS price_count
FROM products
GROUP BY Platform;

-- Create a clean view:

CREATE OR REPLACE VIEW vw_products_clean AS
SELECT
    id,
    Platform,
    URL,
    Name,
    Price,
    MRP,
    (MRP - Price) AS Discount_Amount,
    ROUND(((MRP - Price) / MRP) * 100, 2) AS Discount_Percent,
    Rating,
    Reviews,
    Sizes,
    Colors,
    scraped_at
FROM products
WHERE Price IS NOT NULL;

SELECT
    COUNT(*) AS total_rows,
    SUM(ASIN IS NULL) AS asin_nulls,
    SUM(PID IS NULL)  AS pid_nulls
FROM products;

CREATE OR REPLACE VIEW vw_products_clean AS
SELECT
    Platform,
    URL,
    Name,
    Price,
    MRP,
    Rating,
    Reviews,
    Sizes,
    Colors,
    scraped_at
FROM products;

