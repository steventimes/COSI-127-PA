-- This file aim to create the tables according to the ER diagram
CREATE TABLE IF NOT EXISTS MotionPicture (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    rating FLOAT,
    production VARCHAR(255),
    budget BIGINT,
    CONSTRAINT rating_check CHECK (
        rating > 0
        AND rating <= 10
    ),
    CONSTRAINT budget_check CHECK (budget >= 0)
);
CREATE TABLE IF NOT EXISTS Genre (
    mpid INT,
    genre_name VARCHAR(255),
    PRIMARY KEY (mpid, genre_name),
    FOREIGN KEY (mpid) REFERENCES MotionPicture(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS Movie(
    mpid INT PRIMARY KEY,
    boxoffice_collection FLOAT,
    FOREIGN KEY (mpid) REFERENCES MotionPicture(id) ON DELETE CASCADE,
    CONSTRAINT boxoffice_collection_check CHECK (boxoffice_collection >= 0)
);
CREATE TABLE IF NOT EXISTS Series(
    mpid INT PRIMARY KEY,
    season_count TINYINT,
    FOREIGN KEY (mpid) REFERENCES MotionPicture(id) ON DELETE CASCADE,
    CONSTRAINT season_count_check CHECK (season_count >= 1)
);
CREATE TABLE IF NOT EXISTS Users(
    email VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255),
    age TINYINT
);
CREATE TABLE IF NOT EXISTS Likes(
    uemail VARCHAR(255),
    mpid INT,
    PRIMARY KEY (uemail, mpid),
    FOREIGN KEY (uemail) REFERENCES Users(email) ON DELETE CASCADE,
    FOREIGN KEY (mpid) REFERENCES MotionPicture(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS People(
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    nationality VARCHAR(56),
    dob DATE,
    gender CHAR(1),
    CONSTRAINT gender_check CHECK (gender IN ('M', 'F', 'O'))
);
CREATE TABLE IF NOT EXISTS Role(
    mpid INT,
    pid INT,
    role_name VARCHAR(255),
    PRIMARY KEY (mpid, pid, role_name),
    FOREIGN KEY (mpid) REFERENCES MotionPicture(id) ON DELETE CASCADE,
    FOREIGN KEY (pid) REFERENCES People(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS Award(
    mpid INT,
    pid INT,
    award_name VARCHAR(255),
    award_year YEAR,
    PRIMARY KEY (mpid, pid, award_name, award_year),
    FOREIGN KEY (mpid) REFERENCES MotionPicture(id) ON DELETE CASCADE,
    FOREIGN KEY (pid) REFERENCES People(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS Location(
    mpid INT,
    zip INT,
    city VARCHAR(255),
    country VARCHAR(255),
    PRIMARY KEY (mpid, zip),
    FOREIGN KEY (mpid) REFERENCES MotionPicture(id) ON DELETE CASCADE
);