CREATE TABLE users (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    username VARCHAR(255) UNIQUE,
    password VARCHAR(255)
);

INSERT INTO users (name, email, username, password)
VALUES
    ('juan', 'juan@gmail.com', 'juan', '123'),
    ('maria', 'maria@gmail.com', 'maria', '456');
