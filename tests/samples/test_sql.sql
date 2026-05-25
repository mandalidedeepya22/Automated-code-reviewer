-- Sample SQL code with intentional issues for testing the code reviewer.
-- This file contains various security vulnerabilities, performance issues, and style issues.

-- SQL Injection vulnerable pattern (if concatenated with user input)
-- This is a demonstration of what NOT to do
SELECT * FROM users WHERE id = 1 OR 1=1;

-- SELECT * instead of specific columns (PERFORMANCE ISSUE)
SELECT * FROM users;
SELECT * FROM products;
SELECT * FROM orders;

-- Missing WHERE clause in UPDATE (CRITICAL ISSUE)
UPDATE users SET status = 'active';
UPDATE products SET price = 0;

-- Missing WHERE clause in DELETE (CRITICAL ISSUE)
DELETE FROM temp_logs;
DELETE FROM session_data;

-- N+1 Query pattern (PERFORMANCE ISSUE)
-- This would be executed in a loop:
SELECT * FROM orders WHERE user_id = 1;
SELECT * FROM orders WHERE user_id = 2;
SELECT * FROM orders WHERE user_id = 3;

-- Missing index on frequently queried column
SELECT * FROM users WHERE email = 'test@example.com';
SELECT * FROM products WHERE sku = 'ABC123';

-- Using LIKE with leading wildcard (PERFORMANCE ISSUE)
SELECT * FROM users WHERE name LIKE '%john%';
SELECT * FROM products WHERE description LIKE '%search%';

-- UNION injection pattern (SECURITY ISSUE)
-- SELECT name, price FROM products WHERE id = 1 UNION SELECT username, password FROM users;

-- Hardcoded credentials in comments (SECURITY ISSUE)
-- Username: admin, Password: admin123
-- API Key: sk_live_1234567890

-- Missing transaction handling for multi-step operation
INSERT INTO orders (user_id, total) VALUES (1, 100.00);
INSERT INTO order_items (order_id, product_id, quantity) VALUES (1, 1, 2);
-- If second insert fails, first insert remains

-- Using deprecated syntax
SELECT * FROM users, orders WHERE users.id = orders.user_id;

-- Implicit type conversion (PERFORMANCE ISSUE)
SELECT * FROM users WHERE phone = 1234567890;
SELECT * FROM products WHERE created_at = '2024-01-01';

-- Missing ORDER BY with LIMIT (INCONSISTENT RESULTS)
SELECT * FROM products LIMIT 10;

-- Using SELECT DISTINCT on large dataset without need
SELECT DISTINCT category FROM products;

-- Subquery that could be a JOIN (PERFORMANCE ISSUE)
SELECT * FROM users 
WHERE id IN (SELECT user_id FROM orders WHERE total > 100);

-- Cartesian product (PERFORMANCE ISSUE)
SELECT * FROM users, products, orders;

-- Using FLOAT for monetary values (PRECISION ISSUE)
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY,
    amount FLOAT,
    description VARCHAR(255)
);

-- Missing NOT NULL constraints
CREATE TABLE bad_table (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    created_at TIMESTAMP
);

-- Using TEXT for short strings (STORAGE ISSUE)
CREATE TABLE inefficient_table (
    id INTEGER PRIMARY KEY,
    status TEXT,
    type TEXT,
    code TEXT
);

-- Duplicate indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_email2 ON users(email);

-- Missing foreign key constraints
CREATE TABLE orders_no_fk (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    product_id INTEGER
);

-- Using reserved keywords as identifiers
CREATE TABLE select (
    id INTEGER PRIMARY KEY,
    from VARCHAR(100),
    where INTEGER
);

-- Inconsistent naming conventions
CREATE TABLE Users (
    UserID INTEGER PRIMARY KEY,
    user_name VARCHAR(100),
    UserEmail VARCHAR(100)
);

-- Overly wide VARCHAR
CREATE TABLE wide_table (
    id INTEGER PRIMARY KEY,
    description VARCHAR(65535),
    notes VARCHAR(65535)
);

-- Missing primary key
CREATE TABLE no_pk (
    name VARCHAR(100),
    value INTEGER
);

-- Using SELECT INTO instead of INSERT SELECT
SELECT * INTO backup_users FROM users;

-- Cursor usage when set-based operation would be better
-- DECLARE user_cursor CURSOR FOR SELECT id FROM users;
-- FETCH NEXT FROM user_cursor;

-- Multiple row count operations
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM orders;
SELECT COUNT(*) FROM products;

-- Redundant ORDER BY on indexed column
SELECT * FROM users ORDER BY id;

-- Using HAVING without GROUP BY
SELECT COUNT(*) FROM users HAVING COUNT(*) > 10;