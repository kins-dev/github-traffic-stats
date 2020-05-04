
SET SQL_MODE
= "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone
= "+00:00";

--
-- Database: `Stats_GitHub`
--

-- --------------------------------------------------------

--
-- Table structure for table `Data__Paths`
--

DROP TABLE IF EXISTS `Data__Paths`;
CREATE TABLE `Data__Paths`
(
  `Repo_ID` smallint
(6) UNSIGNED NOT NULL,
  `Date_ID` smallint
(6) UNSIGNED NOT NULL,
  `Path_ID` mediumint
(9) UNSIGNED NOT NULL,
  `Title_ID` mediumint
(9) UNSIGNED NOT NULL,
  `Views` int
(11) NOT NULL,
  `Unique Visitors` int
(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `Data__Referrals`
--

DROP TABLE IF EXISTS `Data__Referrals`;
CREATE TABLE `Data__Referrals`
(
  `Repo_ID` smallint
(6) UNSIGNED NOT NULL,
  `Date_ID` smallint
(6) UNSIGNED NOT NULL,
  `Referral_ID` mediumint
(6) UNSIGNED NOT NULL,
  `Views` int
(11) NOT NULL,
  `Unique Visitors` int
(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `Data__Traffic`
--

DROP TABLE IF EXISTS `Data__Traffic`;
CREATE TABLE `Data__Traffic`
(
  `Repo_ID` smallint
(5) UNSIGNED NOT NULL,
  `Date_ID` smallint
(5) UNSIGNED NOT NULL,
  `Clones` int
(11) NOT NULL,
  `Unique Cloners` int
(11) NOT NULL,
  `Views` int
(11) NOT NULL,
  `Unique Visitors` int
(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Stand-in structure for view `GitHub_Referral`
-- (See below for the actual view)
--
DROP VIEW IF EXISTS `GitHub_Referral`;
CREATE TABLE `GitHub_Referral`
(
`Repo` varchar
(255)
,`Date` timestamp
,`Referral` varchar
(255)
,`Views` int
(11)
,`Unique Visitors` int
(11)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `GitHub_Traffic`
-- (See below for the actual view)
--
DROP VIEW IF EXISTS `GitHub_Traffic`;
CREATE TABLE `GitHub_Traffic`
(
`Repo` varchar
(255)
,`Date` timestamp
,`Clones` int
(11)
,`Unique Cloners` int
(11)
,`Views` int
(11)
,`Unique Visitors` int
(11)
);

-- --------------------------------------------------------

--
-- Table structure for table `Index__Dates`
--

DROP TABLE IF EXISTS `Index__Dates`;
CREATE TABLE `Index__Dates`
(
  `Date_ID` smallint
(5) UNSIGNED NOT NULL,
  `Date` timestamp NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `Index__Paths`
--

DROP TABLE IF EXISTS `Index__Paths`;
CREATE TABLE `Index__Paths`
(
  `Path_ID` mediumint
(8) UNSIGNED NOT NULL,
  `Path` varchar
(768) CHARACTER
SET utf8mb4
COLLATE utf8mb4_0900_ai_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `Index__Referrals`
--

DROP TABLE IF EXISTS `Index__Referrals`;
CREATE TABLE `Index__Referrals`
(
  `Referral_ID` mediumint
(5) UNSIGNED NOT NULL,
  `Referral` varchar
(255) CHARACTER
SET utf8mb4
COLLATE utf8mb4_0900_ai_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `Index__Repos`
--

DROP TABLE IF EXISTS `Index__Repos`;
CREATE TABLE `Index__Repos`
(
  `Repo_ID` smallint
(5) UNSIGNED NOT NULL,
  `Repo` varchar
(255) CHARACTER
SET utf8mb4
COLLATE utf8mb4_0900_ai_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `Index__Titles`
--

DROP TABLE IF EXISTS `Index__Titles`;
CREATE TABLE `Index__Titles`
(
  `Title_ID` mediumint
(8) UNSIGNED NOT NULL,
  `Title` varchar
(768) CHARACTER
SET utf8mb4
COLLATE utf8mb4_0900_ai_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Structure for view `GitHub_Referral`
--
DROP TABLE IF EXISTS `GitHub_Referral`;

DROP VIEW IF EXISTS `GitHub_Referral`;
CREATE ALGORITHM=
MERGE DEFINER=`root`@`localhost` SQL SECURITY INVOKER VIEW `GitHub_Referral`  AS  select `Index__Repos`.`Repo` AS `Repo`,`Index__Dates`.`Date` AS `Date`,`Index__Referrals`.`Referral` AS `Referral`,`Data__Referrals`.`Views` AS `Views`,`Data__Referrals`.`Unique Visitors` AS `Unique Visitors` from (((`Data__Referrals` join `Index__Repos` on((`Index__Repos`.`Repo_ID` = `Data__Referrals`.`Repo_ID`))) join `Index__Dates` on((`Index__Dates`.`Date_ID` = `Data__Referrals`.`Date_ID`))) join `Index__Referrals` on((`Index__Referrals`.`Referral_ID` = `Data__Referrals`.`Referral_ID`))) ;

-- --------------------------------------------------------

--
-- Structure for view `GitHub_Traffic`
--
DROP TABLE IF EXISTS `GitHub_Traffic`;

DROP VIEW IF EXISTS `GitHub_Traffic`;
CREATE ALGORITHM=MERGE DEFINER=`root`@`localhost` SQL SECURITY INVOKER VIEW `GitHub_Traffic`  AS  select `Index__Repos`.`Repo` AS `Repo`,`Index__Dates`.`Date` AS `Date`,`Data__Traffic`.`Clones` AS `Clones`,`Data__Traffic`.`Unique Cloners` AS `Unique Cloners`,`Data__Traffic`.`Views` AS `Views`,`Data__Traffic`.`Unique Visitors` AS `Unique Visitors` from ((`Data__Traffic` join `Index__Repos` on((`Index__Repos`.`Repo_ID` = `Data__Traffic`.`Repo_ID`))) join `Index__Dates` on((`Index__Dates`.`Date_ID` = `Data__Traffic`.`Date_ID`))) ;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `Data__Paths`
--
ALTER TABLE `Data__Paths`
  ADD PRIMARY KEY (`Repo_ID`,`Date_ID`,`Path_ID`,`Title_ID`),
  ADD KEY `Date_ID` (`Date_ID`),
  ADD KEY `Path_ID` (`Path_ID`),
  ADD KEY `Title_ID` (`Title_ID`);

--
-- Indexes for table `Data__Referrals`
--
ALTER TABLE `Data__Referrals`
  ADD PRIMARY KEY (`Repo_ID`,`Date_ID`,`Referral_ID`),
  ADD KEY `Date_ID` (`Date_ID`),
  ADD KEY `Referral_ID` (`Referral_ID`);

--
-- Indexes for table `Data__Traffic`
--
ALTER TABLE `Data__Traffic`
  ADD PRIMARY KEY (`Repo_ID`,`Date_ID`),
  ADD KEY `Date_ID` (`Date_ID`);

--
-- Indexes for table `Index__Dates`
--
ALTER TABLE `Index__Dates`
  ADD PRIMARY KEY (`Date_ID`),
  ADD UNIQUE KEY `Date` (`Date`);

--
-- Indexes for table `Index__Paths`
--
ALTER TABLE `Index__Paths`
  ADD PRIMARY KEY (`Path_ID`),
  ADD UNIQUE KEY `Path` (`Path`);

--
-- Indexes for table `Index__Referrals`
--
ALTER TABLE `Index__Referrals`
  ADD PRIMARY KEY (`Referral_ID`),
  ADD UNIQUE KEY `Referral` (`Referral`) USING BTREE;

--
-- Indexes for table `Index__Repos`
--
ALTER TABLE `Index__Repos`
  ADD PRIMARY KEY (`Repo_ID`),
  ADD UNIQUE KEY `Repo` (`Repo`);

--
-- Indexes for table `Index__Titles`
--
ALTER TABLE `Index__Titles`
  ADD PRIMARY KEY (`Title_ID`),
  ADD UNIQUE KEY `Title` (`Title`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `Index__Dates`
--
ALTER TABLE `Index__Dates`
  MODIFY `Date_ID` smallint(5) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `Index__Paths`
--
ALTER TABLE `Index__Paths`
  MODIFY `Path_ID` mediumint(8) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `Index__Referrals`
--
ALTER TABLE `Index__Referrals`
  MODIFY `Referral_ID` mediumint(5) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `Index__Repos`
--
ALTER TABLE `Index__Repos`
  MODIFY `Repo_ID` smallint(5) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `Index__Titles`
--
ALTER TABLE `Index__Titles`
  MODIFY `Title_ID` mediumint(8) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `Data__Paths`
--
ALTER TABLE `Data__Paths`
  ADD CONSTRAINT `Data__Paths_ibfk_1` FOREIGN KEY (`Repo_ID`) REFERENCES `Index__Repos` (`Repo_ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `Data__Paths_ibfk_2` FOREIGN KEY (`Date_ID`) REFERENCES `Index__Dates` (`Date_ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `Data__Paths_ibfk_3` FOREIGN KEY (`Path_ID`) REFERENCES `Index__Paths` (`Path_ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `Data__Paths_ibfk_4` FOREIGN KEY (`Title_ID`) REFERENCES `Index__Titles` (`Title_ID`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `Data__Referrals`
--
ALTER TABLE `Data__Referrals`
  ADD CONSTRAINT `Data__Referrals_ibfk_1` FOREIGN KEY (`Repo_ID`) REFERENCES `Index__Repos` (`Repo_ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `Data__Referrals_ibfk_2` FOREIGN KEY (`Date_ID`) REFERENCES `Index__Dates` (`Date_ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `Data__Referrals_ibfk_3` FOREIGN KEY (`Referral_ID`) REFERENCES `Index__Referrals` (`Referral_ID`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `Data__Traffic`
--
ALTER TABLE `Data__Traffic`
  ADD CONSTRAINT `Data__Traffic_ibfk_1` FOREIGN KEY (`Date_ID`) REFERENCES `Index__Dates` (`Date_ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `Data__Traffic_ibfk_2` FOREIGN KEY (`Repo_ID`) REFERENCES `Index__Repos` (`Repo_ID`) ON
DELETE CASCADE ON
UPDATE CASCADE;
COMMIT;
