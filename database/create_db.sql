CREATE DATABASE fruit_store_db;

USE fruit_store_db;

CREATE TABLE users
(
    id INT
    AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR
    (80) NOT NULL UNIQUE,
    password VARCHAR
    (120) NOT NULL
);

    CREATE TABLE products
    (
        id INT
        AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR
        (100) NOT NULL,
    price FLOAT NOT NULL,
    stock INT NOT NULL
);

        CREATE TABLE orders
        (
            id INT
            AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    quantity INT NOT NULL
);
