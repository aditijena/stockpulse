CREATE USER 'stockuser'@'localhost' IDENTIFIED BY 'stockpass123'; 
GRANT ALL PRIVILEGES ON stockpulse_db.* TO 'stockuser'@'localhost'; 
FLUSH PRIVILEGES; 
CREATE DATABASE stockpulse_db; 
USE stockpulse_db;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin','viewer') DEFAULT 'admin'
);

INSERT INTO users (username, password)
VALUES ('admin', 'admin123');

CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    cost_price DECIMAL(10,2),
    selling_price DECIMAL(10,2),
    initial_stock INT,
    current_stock INT,
    added_date DATE DEFAULT (CURRENT_DATE)
) ENGINE=InnoDB;

INSERT INTO products
(product_name, category, cost_price, selling_price, initial_stock, current_stock)
VALUES
('Mobile Phone', 'Electronics', 12000, 18000, 40, 40),
('Headphones', 'Electronics', 1500, 3000, 70, 70),
('T-Shirt', 'Fashion', 400, 900, 120, 120),
('Cooking Oil', 'Grocery', 1100, 1350, 25, 25),
('Notebook', 'Stationery', 40, 80, 200, 200);

CREATE TABLE sales (
    sale_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT,
    quantity_sold INT,
    sale_date DATE,
    FOREIGN KEY (product_id)
        REFERENCES products(product_id)
        ON DELETE CASCADE
);

INSERT INTO sales (product_id, quantity_sold, sale_date)
VALUES
(1, 5, DATE_SUB(CURDATE(), INTERVAL 40 DAY)),
(2, 3, DATE_SUB(CURDATE(), INTERVAL 10 DAY)),
(3, 8, DATE_SUB(CURDATE(), INTERVAL 10 DAY)),
(4, 9, DATE_SUB(CURDATE(), INTERVAL 50 DAY)),
(5, 10, DATE_SUB(CURDATE(), INTERVAL 90 DAY));



CREATE TABLE risk_analysis (
    analysis_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT UNIQUE,
    days_unsold INT,
    risk_level ENUM('Low','Medium','High'),
    risk_score INT,
    suggested_action VARCHAR(100),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id)
        REFERENCES products(product_id)
        ON DELETE CASCADE
);

TRUNCATE TABLE risk_analysis;

INSERT INTO risk_analysis
(product_id, days_unsold, risk_level, risk_score, suggested_action)
SELECT
    p.product_id,
    COALESCE(DATEDIFF(CURDATE(), MAX(s.sale_date)), 0) AS days_unsold,
    CASE
        WHEN COALESCE(DATEDIFF(CURDATE(), MAX(s.sale_date)), 0) > 45 THEN 'High'
        WHEN COALESCE(DATEDIFF(CURDATE(), MAX(s.sale_date)), 0) > 20 THEN 'Medium'
        ELSE 'Low'
    END AS risk_level,
    CASE
        WHEN COALESCE(DATEDIFF(CURDATE(), MAX(s.sale_date)), 0) > 45 THEN 80
        WHEN COALESCE(DATEDIFF(CURDATE(), MAX(s.sale_date)), 0) > 20 THEN 50
        ELSE 10
    END AS risk_score,
    CASE
        WHEN COALESCE(DATEDIFF(CURDATE(), MAX(s.sale_date)), 0) > 45 THEN 'Clear stock'
        WHEN COALESCE(DATEDIFF(CURDATE(), MAX(s.sale_date)), 0) > 20 THEN 'Discount'
        ELSE 'Normal sales'
    END AS suggested_action
FROM products p
LEFT JOIN sales s ON p.product_id = s.product_id
GROUP BY p.product_id;

DROP TABLE IF EXISTS risk_analysis;
DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS products;
SET SQL_SAFE_UPDATES = 0;

UPDATE risk_analysis
SET
    risk_score = LEAST(100, days_unsold * 2),
    risk_level = CASE
        WHEN days_unsold * 2 >= 71 THEN 'High'
        WHEN days_unsold * 2 >= 31 THEN 'Medium'
        ELSE 'Low'
    END,
    suggested_action = CASE
        WHEN days_unsold * 2 >= 71 THEN 'Clear stock'
        WHEN days_unsold * 2 >= 31 THEN 'Discount'
        ELSE 'Normal sales'
    END;
    
SELECT 
    p.product_id,
    p.product_name AS `Product Name`,
    p.category AS `Category`,
    p.current_stock AS `Stock Quantity`,
    DATEDIFF(
        CURDATE(),
        COALESCE(MAX(s.sale_date), p.added_date)
    ) AS `Days Unsold`
FROM products p
LEFT JOIN sales s ON p.product_id = s.product_id
GROUP BY p.product_id;

select * from sales














































































