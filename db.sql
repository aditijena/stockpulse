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
);
CREATE TABLE risk_analysis (
    analysis_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT,
    days_unsold INT,
    risk_level ENUM('Low','Medium','High'),
    risk_score DECIMAL(5,2),
    suggested_action VARCHAR(100),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);
CREATE TABLE sales (
    sale_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT,
    quantity_sold INT,
    sale_date DATE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);
SHOW tables;
DESCRIBE products;
DESCRIBE risk_analysis;

INSERT INTO products 
(product_name, category, cost_price, selling_price, initial_stock, current_stock, seasonal_flag, added_date)
VALUES
('Laptop', 'Electronics', 40000, 52000, 50, 50, 0, CURDATE()),
('Shoes', 'Fashion', 800, 1500, 100, 60, 1, CURDATE()),
('Rice Bag', 'Grocery', 1200, 1500, 30, 5, 0, CURDATE());
SELECT * FROM products;
INSERT INTO sales (product_id, quantity_sold, sale_date)
VALUES
(1, 5, DATE_SUB(CURDATE(), INTERVAL 40 DAY)),
(2, 10, DATE_SUB(CURDATE(), INTERVAL 5 DAY)),
(3, 25, DATE_SUB(CURDATE(), INTERVAL 60 DAY));

INSERT INTO risk_analysis
(product_id, days_unsold, risk_level, risk_score, suggested_action)
SELECT
    p.product_id,
    DATEDIFF(CURDATE(), MAX(s.sale_date)) AS days_unsold,
    CASE
        WHEN DATEDIFF(CURDATE(), MAX(s.sale_date)) > 45 THEN 'High'
        WHEN DATEDIFF(CURDATE(), MAX(s.sale_date)) > 20 THEN 'Medium'
        ELSE 'Low'
    END AS risk_level,
    CASE
        WHEN DATEDIFF(CURDATE(), MAX(s.sale_date)) > 45 THEN 80
        WHEN DATEDIFF(CURDATE(), MAX(s.sale_date)) > 20 THEN 50
        ELSE 10
    END AS risk_score,
    CASE
        WHEN DATEDIFF(CURDATE(), MAX(s.sale_date)) > 45 THEN 'Clear stock'
        WHEN DATEDIFF(CURDATE(), MAX(s.sale_date)) > 20 THEN 'Discount'
        ELSE 'Normal sales'
    END AS suggested_action
FROM products p
LEFT JOIN sales s ON p.product_id = s.product_id
GROUP BY p.product_id;
TRUNCATE TABLE risk_analysis;
SELECT * FROM risk_analysis;
ALTER TABLE products
ADD COLUMN risk_level ENUM('LOW', 'MEDIUM', 'HIGH') DEFAULT 'LOW';
SELECT COUNT(*) FROM products;
SHOW TABLE STATUS WHERE Name = 'products';
ALTER TABLE products ENGINE=InnoDB;







