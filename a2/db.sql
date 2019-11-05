CREATE DATABASE a2;
USE a2;

CREATE TABLE `auto_config` (
  `ratio` int(11) NOT NULL,
  `threshold_high` int(11) NOT NULL,
  `threshold_low` int(11) NOT NULL,
  PRIMARY KEY (`ratio`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;
