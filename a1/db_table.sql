CREATE TABLE `users` (
  `userID` varchar(20) NOT NULL,
  `password` varchar(32) NOT NULL,
  PRIMARY KEY (`userID`),
  UNIQUE KEY `userID_UNIQUE` (`userID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `photos` (
  `userID` varchar(20) NOT NULL,
  `key0` varchar(100) DEFAULT NULL,
  `key1` varchar(100) DEFAULT NULL,
  `key2` varchar(100) NOT NULL,
  PRIMARY KEY (`key2`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

