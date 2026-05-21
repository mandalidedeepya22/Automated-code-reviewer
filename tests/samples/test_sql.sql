-- Sample SQL code for testing the AI Code Reviewer.
-- This file contains intentional issues for testing purposes.

-- SELECT * instead of specific columns
SELECT * FROM users;

-- Missing WHERE clause in UPDATE
UPDATE users SET status = 'active';

-- SQL injection vulnerability (string concatenation)
SELECT * FROM users WHERE username = '' + user_input + '';

-- Missing index on frequently queried column
SELECT * FROM orders WHERE customer_id = 123;

-- N+1 query pattern (simulated)
-- This would typically be in application code, but shown here for reference
SELECT id FROM customers;
-- Then for each customer:
SELECT * FROM orders WHERE customer_id = 1;
SELECT * FROM orders WHERE customer_id = 2;
SELECT * FROM orders WHERE customer_id = 3;

-- Using deprecated syntax
SELECT * FROM users WHERE status LIKE '%active%';

-- Missing transaction handling for multiple operations
INSERT INTO audit_log (action, timestamp) VALUES ('LOGIN', NOW());
UPDATE users SET last_login = NOW() WHERE id = 1;
DELETE FROM sessions WHERE user_id = 1;

-- Hardcoded values instead of parameters
SELECT * FROM products WHERE category = 'electronics' AND price < 1000;

-- No LIMIT on potentially large result set
SELECT * FROM logs ORDER BY created_at DESC;

-- Using SELECT without specifying columns on joined tables
SELECT * FROM users u
JOIN orders o ON u.id = o.user_id
JOIN products p ON o.product_id = p.id;

-- Missing proper JOIN condition
SELECT * FROM users, orders WHERE users.id = orders.user_id;

-- Potential SQL injection in dynamic query
-- This pattern is dangerous when user_input is not sanitized
SET @query = CONCAT('SELECT * FROM users WHERE name = ''', user_input, '''');
PREPARE stmt FROM @query;
EXECUTE stmt;

-- Using OR in WHERE clause that prevents index usage
SELECT * FROM products WHERE name = 'widget' OR description LIKE '%widget%';

-- Storing passwords in plain text (should be hashed)
INSERT INTO users (username, password, email) 
VALUES ('admin', 'password123', 'admin@example.com');

-- Missing foreign key constraints
CREATE TABLE order_items (
    id INT PRIMARY KEY,
    order_id INT,  -- Should have FOREIGN KEY constraint
    product_id INT,  -- Should have FOREIGN KEY constraint
    quantity INT
);

-- Using FLOAT for monetary values (precision issues)
CREATE TABLE transactions (
    id INT PRIMARY KEY,
    amount FLOAT,  -- Should use DECIMAL
    total FLOAT    -- Should use DECIMAL
);

-- Missing NOT NULL constraints where appropriate
CREATE TABLE users_backup (
    id INT,
    username VARCHAR(50),  -- Should be NOT NULL
    email VARCHAR(100),    -- Should be NOT NULL
    created_at TIMESTAMP
);

-- Wildcard in LIKE at the beginning (prevents index usage)
SELECT * FROM products WHERE name LIKE '%phone%';

-- UNION without proper column matching
SELECT id, name, email FROM users
UNION
SELECT order_id, product_name, NULL FROM orders;

-- Subquery that could be a JOIN
SELECT * FROM products 
WHERE category_id IN (SELECT id FROM categories WHERE active = 1);

-- Missing GROUP BY with aggregate
SELECT customer_id, COUNT(*) FROM orders;

-- Using HAVING without GROUP BY
SELECT * FROM products HAVING price > 100;