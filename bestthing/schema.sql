SET SESSION storage_engine = "InnoDB";
SET SESSION time_zone = "+0:00";

DROP DATABASE IF EXISTS bestthing;
CREATE DATABASE bestthing;
USE bestthing;
ALTER DATABASE CHARACTER SET "utf8";

DROP TABLE IF EXISTS concept;
CREATE TABLE concept (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        value varchar(1000),
        parent BIGINT DEFAULT -1,
        score INT DEFAULT 0,
        INDEX index_value USING BTREE (value),
        INDEX index_score USING BTREE (score),
        INDEX index_parent USING BTREE (parent)
        );
