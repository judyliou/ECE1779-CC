CREATE DATABASE a2;
USE a2;

CREATE TABLE `auto_config` (
  `ratio_high` int(11) NOT NULL,
  `ratio_low` int(11) NOT NULL,
  `threshold_high` int(11) NOT NULL,
  `threshold_low` int(11) NOT NULL,
  PRIMARY KEY (`ratio_high`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

INSERT INTO auto_config values (2, 2, 60, 20);
