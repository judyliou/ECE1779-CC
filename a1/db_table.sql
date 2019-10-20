CREATE DATABASE a1;
USE a1;

CREATE TABLE `users` (
  `userID` varchar(20) NOT NULL,
  `password` varchar(64) NOT NULL,
  `salt` varchar(12) NOT NULL,
  PRIMARY KEY (`userID`),
  UNIQUE KEY `userID_UNIQUE` (`userID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;


-- key0: filename for original photo
-- key1: filename for text-detected photo
-- key2: filename for text-detected thumbnail
CREATE TABLE `photos` (
  `userID` varchar(20) NOT NULL,
  `key0` varchar(100) NOT NULL,
  `key1` varchar(100) NOT NULL,
  `key2` varchar(100) NOT NULL,
  PRIMARY KEY (`key0`),
  UNIQUE KEY `key0_UNIQUE` (`key0`),
  UNIQUE KEY `key1_UNIQUE` (`key1`),
  UNIQUE KEY `key2_UNIQUE` (`key2`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;
