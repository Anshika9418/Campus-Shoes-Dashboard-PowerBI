DROP DATABASE IF EXISTS ecommerce_data;
CREATE DATABASE ecommerce_data;
USE ecommerce_data;

DROP TABLE IF EXISTS campus;
CREATE TABLE campus (
    Name VARCHAR(500),
    Colors VARCHAR(500),
    URL TEXT,
    Price DECIMAL(10,2),
    `M.R.P` DECIMAL(10,2),
    Discount VARCHAR(100),
    Image_URL TEXT,
    Sizes VARCHAR(500),
    Rating DECIMAL(3,2),
    Reviews INT
);

DROP TABLE IF EXISTS flipkart;
CREATE TABLE flipkart (
    URL TEXT,
    Name VARCHAR(500),
    Price DECIMAL(10,2),
    `M.R.P` DECIMAL(10,2),
    Discount VARCHAR(100),
    Image_URL TEXT,
    Sizes VARCHAR(500),
    Colors VARCHAR(500),
    Rating DECIMAL(3,2),
    Reviews INT
);

DROP TABLE IF EXISTS amazon;
CREATE TABLE amazon (
    ASIN VARCHAR(100),
    Name VARCHAR(500),
    URL TEXT,
    Price DECIMAL(10,2),
    `M.R.P` DECIMAL(10,2),
    Discount VARCHAR(100),
    Image_URL TEXT,
    Description TEXT,
    Rating DECIMAL(3,2),
    Reviews INT,
    Sizes VARCHAR(500),
    Colors VARCHAR(500)
);

