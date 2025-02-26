
-- Create Partners table
CREATE TABLE IF NOT EXISTS Partners (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(20) NOT NULL,
    city VARCHAR(100),
    street VARCHAR(100),
    building VARCHAR(20),
    director_lastname VARCHAR(50),
    director_firstname VARCHAR(50),
    director_middlename VARCHAR(50),
    phone VARCHAR(20),
    email VARCHAR(100),
    inn VARCHAR(20) UNIQUE NOT NULL,
    rating INT
);

-- Create Partner_products table
CREATE TABLE IF NOT EXISTS Partner_products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    partner_id INT NOT NULL,
    product_name VARCHAR(100) NOT NULL,
    product_code VARCHAR(50) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (partner_id) REFERENCES Partners(id) ON DELETE CASCADE
);

-- Sample INSERT statements for Partners (to be replaced with actual data from Excel)
-- INSERT INTO Partners (name, type, city, street, building, director_lastname, director_firstname, director_middlename, phone, email, inn, rating)
-- VALUES ('ООО Пример', 'ООО', 'Москва', 'Ленина', '10', 'Иванов', 'Иван', 'Иванович', '+7(999)123-45-67', 'example@mail.ru', '1234567890', 5);

-- Sample INSERT statements for Partner_products (to be replaced with actual data from Excel)
-- INSERT INTO Partner_products (partner_id, product_name, product_code, price)
-- VALUES (1, 'Продукт 1', 'P001', 1500.00);
