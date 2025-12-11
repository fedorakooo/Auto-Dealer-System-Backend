-- Get paginated users with customer data
SELECT u.*, c.date_of_birth
FROM users u
LEFT JOIN customers c ON c.user_id = u.id
OFFSET 20 LIMIT 20;


-- Count total users
SELECT COUNT(*) FROM users;


-- Get user by UUID with customer data
SELECT u.* , c.date_of_birth
FROM users u
LEFT JOIN customers c ON c.user_id = u.id
WHERE u.id = 'aedaf184-df84-4243-b79d-839befafe020';


-- Get all customers with user data
SELECT
    c.id AS customer_id,
    c.date_of_birth,
    u.*
FROM customers c
LEFT JOIN users u ON u.id = c.user_id;


-- Create customer procedure
CREATE OR REPLACE PROCEDURE add_customer(
    p_user_id UUID,
    p_customer_id UUID,
    p_first_name VARCHAR(100),
    p_second_name VARCHAR(100),
    p_phone_number VARCHAR(20),
    p_email VARCHAR(255),
    p_hashed_password VARCHAR(255),
    p_role user_roles,
    p_date_of_birth DATE
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO users (id, first_name, second_name, phone_number, email, hashed_password, role)
    VALUES (p_user_id, p_first_name, p_second_name, p_phone_number, p_email, p_hashed_password, p_role);

    INSERT INTO customers (id, user_id, date_of_birth)
    VALUES (p_customer_id, p_user_id, p_date_of_birth);
END;
$$;


-- Update user phone number
UPDATE users
SET phone_number = '+375299998877'
WHERE id = 'aedaf184-df84-4243-b79d-839befafe020';


-- Delete user by UUID
DELETE FROM users
WHERE id = 'aedaf184-df84-4243-b79d-839befafe020';
