DROP TABLE IF EXISTS place_amenity;
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS places;
DROP TABLE IF EXISTS amenities;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id CHAR(36) PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE
);

CREATE TABLE places (
    id CHAR(36) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    latitude FLOAT,
    longitude FLOAT,
    owner_id CHAR(36) NOT NULL,
    FOREIGN KEY (owner_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

CREATE TABLE reviews (
    id CHAR(36) PRIMARY KEY,
    text TEXT,
    rating INT CHECK(rating >= 1 AND rating <= 5) NOT NULL,
    user_id CHAR(36),
    place_id CHAR(36),

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (place_id) REFERENCES places(id) ON DELETE CASCADE,

    UNIQUE (user_id, place_id)
);

CREATE TABLE amenities (
    id CHAR(36) PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE place_amenity (
    place_id CHAR(36) NOT NULL,
    amenity_id CHAR(36) NOT NULL,
    PRIMARY KEY (place_id, amenity_id),
    FOREIGN KEY (place_id) REFERENCES places(id) ON DELETE CASCADE,
    FOREIGN KEY (amenity_id) REFERENCES amenities(id) ON DELETE CASCADE
);

INSERT INTO users(
    id,
    first_name,
    last_name,
    email,
    password,
    is_admin
)
VALUES (
    '36c9050e-ddd3-4c3b-9731-9f487208bbc1',
    'Admin',
    'HBnB',
    'admin@hbnb.io',
    '$2a$12$PWa.AB4JRzmwjaV5Sy/mpen3KbD361ANgdZCNJ558dc9OfwnPmh52',
    TRUE
);


INSERT INTO amenities (id, name)
VALUES
('b263c15a-4b50-4209-92cc-4ce8fabc528d', 'WIFI'),
('2ff598e5-182b-4133-b596-0dc539c16b92', 'Swimming Pool'),
('503443f3-1377-4572-8ae9-26966ea37142', 'Air Conditioning');

SHOW TABLES;
SELECT * FROM users;
SELECT * FROM amenities;
