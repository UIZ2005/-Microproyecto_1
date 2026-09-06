CREATE TABLE products (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(500),
    price DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL DEFAULT 0
);

INSERT INTO products (name, description, price, stock)
VALUES
    ('Laptop Lenovo', 'Laptop para trabajo y estudio', 2500000.00, 10),
    ('Mouse Logitech', 'Mouse inalambrico', 85000.00, 25),
    ('Teclado Mecánico', 'Teclado mecanico RGB', 180000.00, 15);
