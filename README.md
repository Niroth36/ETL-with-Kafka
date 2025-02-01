# Extract Transform Load procedure

## Technologies
    - mysql
    - neo4j
    - kafka
    - mongodb
    - flask

## Databases
docker images for mysql and neo4j.
docker-compose up -d

## MySQL

docker exec -it mysql-db mysql -u cl_user -p

CREATE DATABASE IF NOT EXISTS cl_shop;
USE cl_shop;

CREATE TABLE clothes (
    clothID INT AUTO_INCREMENT PRIMARY KEY,
    style ENUM('athletic', 'casual', 'formal', 'business') NOT NULL,
    color ENUM('Red', 'Green', 'Blue', 'Black', 'White') NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    brand VARCHAR(255) NOT NULL
);

This schema ensures that the predefined attributes (style, color) only accept valid values while allowing flexibility for price and brand.

## Neo4j

docker exec -it neo4j-db cypher-shell -u neo4j -p password

- Create users
CREATE (:User {userID: 1, name: "Alice", email: "alice@example.com", purchasedClothes: [1, 2, 5]});
CREATE (:User {userID: 2, name: "Bob", email: "bob@example.com", purchasedClothes: [2, 3]});
CREATE (:User {userID: 3, name: "Charlie", email: "charlie@example.com", purchasedClothes: [1, 4, 5]});

- Create Relationships
MATCH (a:User {userID: 1}), (b:User {userID: 2})
CREATE (a)-[:FRIEND]->(b);

MATCH (a:User {userID: 2}), (c:User {userID: 3})
CREATE (a)-[:PARTNER]->(c);

- Make checks
MATCH (u:User) RETURN u;
MATCH (u:User) WHERE 8 IN u.purchasedClothes RETURN u;
