-- DROP SCHEMA IF EXISTS flask;
CREATE SCHEMA IF NOT EXISTS csc336_project;
USE csc336_project;

CREATE TABLE IF NOT EXISTS user (
    id INT UNSIGNED AUTO_INCREMENT,
    name VARCHAR(45) NOT NULL,
    email VARCHAR(45) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS artist (
    id INT UNSIGNED AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    spotify_artist_id VARCHAR(50) NOT NULL,
    spotify_artist_uri VARCHAR(50) NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS album (
    id INT UNSIGNED AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    total_tracks INT NOT NULL,
    duration TIME NOT NULL,
    release_date DATE NOT NULL,
    label VARCHAR(100) NOT NULL,
    img_src VARCHAR(100) NOT NULL,
    spotify_album_id VARCHAR(50) NOT NULL,
	spotify_album_uri VARCHAR(50) NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS album_tracks (
    id INT UNSIGNED AUTO_INCREMENT,
    track_number INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    explicit BOOLEAN NOT NULL,
    duration TIME NOT NULL,
    spotify_track_id VARCHAR(50) NOT NULL,
    spotify_track_uri VARCHAR(50) NOT NULL,
    album_id INT UNSIGNED NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (album_id) REFERENCES album (id)
);

CREATE TABLE IF NOT EXISTS album_artist (
    id INT UNSIGNED AUTO_INCREMENT,
    artist_id INT UNSIGNED NOT NULL,
    album_id INT UNSIGNED NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (album_id) REFERENCES album (id),
    FOREIGN KEY (artist_id) REFERENCES artist (id)
);

CREATE TABLE IF NOT EXISTS user_album (
    id INT UNSIGNED AUTO_INCREMENT,
    user_id INT UNSIGNED NOT NULL,
    album_id INT UNSIGNED NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES user (id),
    FOREIGN KEY (album_id) REFERENCES album (id)
);