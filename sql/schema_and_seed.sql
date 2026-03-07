-- Database setup
DROP DATABASE IF EXISTS team2_firmhub;
CREATE DATABASE IF NOT EXISTS team2_firmhub 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

USE team2_firmhub;

-- MySQL configuration
/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

-- ================================================================
-- DIMENSION TABLES
-- ================================================================

-- ----------------------------------------------------------------
-- Table: dim_data_source
-- Description: Data sources for panel database
-- ----------------------------------------------------------------
DROP TABLE IF EXISTS `dim_data_source`;
CREATE TABLE `dim_data_source` (
  `source_id` smallint NOT NULL AUTO_INCREMENT,
  `source_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `source_type` enum('market','financial_statement','ownership','text_report','manual') COLLATE utf8mb4_unicode_ci NOT NULL,
  `provider` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `note` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`source_id`),
  UNIQUE KEY `source_name` (`source_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Master list of data sources';

-- Seed data for dim_data_source
INSERT INTO `dim_data_source` VALUES 
(1, 'FiinPro', 'ownership', 'FiinGroup', 'Ownership ratios (end-of-year snapshot)'),
(2, 'BCTC_Audited', 'financial_statement', 'Company/Exchange', 'Audited financial statements'),
(3, 'Vietstock', 'market', 'Vietstock', 'Market fields (price, shares, dividend, EPS)'),
(4, 'AnnualReport', 'text_report', 'Company', 'Annual report / disclosures for innovation & headcount');

-- ----------------------------------------------------------------
-- Table: dim_exchange
-- Description: Stock exchanges in Vietnam
-- ----------------------------------------------------------------
DROP TABLE IF EXISTS `dim_exchange`;
CREATE TABLE `dim_exchange` (
  `exchange_id` tinyint NOT NULL AUTO_INCREMENT,
  `exchange_code` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `exchange_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`exchange_id`),
  UNIQUE KEY `exchange_code` (`exchange_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Vietnamese stock exchanges';

-- Seed data for dim_exchange
INSERT INTO `dim_exchange` VALUES 
(1, 'HOSE', 'Ho Chi Minh Stock Exchange'),
(2, 'HNX', 'Hanoi Stock Exchange');

-- ----------------------------------------------------------------
-- Table: dim_industry_l2
-- Description: Industry classification (Level 2)
-- ----------------------------------------------------------------
DROP TABLE IF EXISTS `dim_industry_l2`;
CREATE TABLE `dim_industry_l2` (
  `industry_l2_id` smallint NOT NULL AUTO_INCREMENT,
  `industry_l2_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`industry_l2_id`),
  UNIQUE KEY `industry_l2_name` (`industry_l2_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Industry classification level 2';

-- No seed data - industry_l2 will be imported from Excel

-- ----------------------------------------------------------------
-- Table: dim_firm
-- Description: Firm master data (empty - to be populated by import script)
-- ----------------------------------------------------------------
DROP TABLE IF EXISTS `dim_firm`;
CREATE TABLE `dim_firm` (
  `firm_id` bigint NOT NULL AUTO_INCREMENT,
  `ticker` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `company_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `exchange_id` tinyint NOT NULL,
  `industry_l2_id` smallint DEFAULT NULL,
  `founded_year` smallint DEFAULT NULL,
  `listed_year` smallint DEFAULT NULL,
  `status` enum('active','delisted','inactive') COLLATE utf8mb4_unicode_ci DEFAULT 'active',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`firm_id`),
  UNIQUE KEY `ticker` (`ticker`),
  KEY `fk_firm_exchange` (`exchange_id`),
  KEY `fk_firm_industry` (`industry_l2_id`),
  CONSTRAINT `fk_firm_exchange` FOREIGN KEY (`exchange_id`) REFERENCES `dim_exchange` (`exchange_id`),
  CONSTRAINT `fk_firm_industry` FOREIGN KEY (`industry_l2_id`) REFERENCES `dim_industry_l2` (`industry_l2_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Firm master data - populated by import script';

-- No seed data - firms will be imported from Excel

-- ================================================================
-- FACT TABLES
-- ================================================================

-- ----------------------------------------------------------------
-- Table: fact_data_snapshot
-- Description: Snapshot metadata for versioning
-- ----------------------------------------------------------------
DROP TABLE IF EXISTS `fact_data_snapshot`;
CREATE TABLE `fact_data_snapshot` (
  `snapshot_id` bigint NOT NULL AUTO_INCREMENT,
  `snapshot_date` date NOT NULL,
  `period_from` date DEFAULT NULL,
  `period_to` date DEFAULT NULL,
  `fiscal_year` smallint NOT NULL,
  `source_id` smallint NOT NULL,
  `version_tag` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  `created_by` varchar(80) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`snapshot_id`),
  UNIQUE KEY `uq_snapshot` (`snapshot_date`,`fiscal_year`,`source_id`,`version_tag`),
  KEY `fk_snapshot_source` (`source_id`),
  CONSTRAINT `fk_snapshot_source` FOREIGN KEY (`source_id`) REFERENCES `dim_data_source` (`source_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Data snapshot versioning';

-- NOTE: SNAPSHOTS WILL BE CREATED BY SEPARATE SCRIPT

-- ----------------------------------------------------------------
-- Table: fact_financial_year
-- Description: Annual financial statement data
-- ----------------------------------------------------------------
DROP TABLE IF EXISTS `fact_financial_year`;
CREATE TABLE `fact_financial_year` (
  `firm_id` bigint NOT NULL,
  `fiscal_year` smallint NOT NULL,
  `snapshot_id` bigint NOT NULL,
  `unit_scale` bigint NOT NULL DEFAULT '1000000000' COMMENT 'Default: 1 billion VND',
  `currency_code` char(3) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'VND',
  `net_sales` decimal(20,2) DEFAULT NULL COMMENT 'Net sales revenue (billion VND)',
  `total_assets` decimal(20,2) DEFAULT NULL COMMENT 'Total assets (billion VND)',
  `selling_expenses` decimal(20,2) DEFAULT NULL,
  `general_admin_expenses` decimal(20,2) DEFAULT NULL,
  `intangible_assets_net` decimal(20,2) DEFAULT NULL,
  `manufacturing_overhead` decimal(20,2) DEFAULT NULL,
  `net_operating_income` decimal(20,2) DEFAULT NULL,
  `raw_material_consumption` decimal(20,2) DEFAULT NULL,
  `merchandise_purchase_year` decimal(20,2) DEFAULT NULL,
  `wip_goods_purchase` decimal(20,2) DEFAULT NULL,
  `outside_manufacturing_expenses` decimal(20,2) DEFAULT NULL,
  `production_cost` decimal(20,2) DEFAULT NULL,
  `rnd_expenses` decimal(20,2) DEFAULT NULL COMMENT 'R&D expenditure',
  `net_income` decimal(20,2) DEFAULT NULL,
  `total_equity` decimal(20,2) DEFAULT NULL,
  `total_liabilities` decimal(20,2) DEFAULT NULL,
  `cash_and_equivalents` decimal(20,2) DEFAULT NULL,
  `long_term_debt` decimal(20,2) DEFAULT NULL,
  `current_assets` decimal(20,2) DEFAULT NULL,
  `current_liabilities` decimal(20,2) DEFAULT NULL,
  `growth_ratio` decimal(10,6) DEFAULT NULL COMMENT 'Year-over-year sales growth',
  `inventory` decimal(20,2) DEFAULT NULL,
  `net_ppe` decimal(20,2) DEFAULT NULL COMMENT 'Net property, plant & equipment',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`firm_id`,`fiscal_year`,`snapshot_id`),
  KEY `fk_fin_snapshot` (`snapshot_id`),
  CONSTRAINT `fk_fin_firm` FOREIGN KEY (`firm_id`) REFERENCES `dim_firm` (`firm_id`),
  CONSTRAINT `fk_fin_snapshot` FOREIGN KEY (`snapshot_id`) REFERENCES `fact_data_snapshot` (`snapshot_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Annual financial statement data';

-- No seed data - will be imported from Excel

-- ----------------------------------------------------------------
-- Table: fact_cashflow_year
-- Description: Annual cash flow statement data
-- ----------------------------------------------------------------
DROP TABLE IF EXISTS `fact_cashflow_year`;
CREATE TABLE `fact_cashflow_year` (
  `firm_id` bigint NOT NULL,
  `fiscal_year` smallint NOT NULL,
  `snapshot_id` bigint NOT NULL,
  `unit_scale` bigint NOT NULL DEFAULT '1000000000' COMMENT 'Default: 1 billion VND',
  `currency_code` char(3) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'VND',
  `net_cfo` decimal(20,2) DEFAULT NULL COMMENT 'Net cash from operating activities',
  `capex` decimal(20,2) DEFAULT NULL COMMENT 'Capital expenditure',
  `net_cfi` decimal(20,2) DEFAULT NULL COMMENT 'Net cash from investing activities',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`firm_id`,`fiscal_year`,`snapshot_id`),
  KEY `fk_cf_snapshot` (`snapshot_id`),
  CONSTRAINT `fk_cf_firm` FOREIGN KEY (`firm_id`) REFERENCES `dim_firm` (`firm_id`),
  CONSTRAINT `fk_cf_snapshot` FOREIGN KEY (`snapshot_id`) REFERENCES `fact_data_snapshot` (`snapshot_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Annual cash flow data';

-- No seed data - will be imported from Excel

-- ----------------------------------------------------------------
-- Table: fact_market_year
-- Description: Annual market data (stock price, market cap, etc.)
-- ----------------------------------------------------------------
DROP TABLE IF EXISTS `fact_market_year`;
CREATE TABLE `fact_market_year` (
  `firm_id` bigint NOT NULL,
  `fiscal_year` smallint NOT NULL,
  `snapshot_id` bigint NOT NULL,
  `shares_outstanding` bigint DEFAULT NULL COMMENT 'Number of shares outstanding',
  `price_reference` enum('close_year_end','avg_year','close_fiscal_end') COLLATE utf8mb4_unicode_ci DEFAULT 'close_year_end',
  `share_price` decimal(20,4) DEFAULT NULL COMMENT 'Share price in VND',
  `market_value_equity` decimal(20,2) DEFAULT NULL COMMENT 'Market capitalization (VND)',
  `dividend_cash_paid` decimal(20,2) DEFAULT NULL COMMENT 'Cash dividend paid (VND)',
  `eps_basic` decimal(20,6) DEFAULT NULL COMMENT 'Basic earnings per share (VND)',
  `currency_code` char(3) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'VND',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`firm_id`,`fiscal_year`,`snapshot_id`),
  KEY `fk_mkt_snapshot` (`snapshot_id`),
  CONSTRAINT `fk_mkt_firm` FOREIGN KEY (`firm_id`) REFERENCES `dim_firm` (`firm_id`),
  CONSTRAINT `fk_mkt_snapshot` FOREIGN KEY (`snapshot_id`) REFERENCES `fact_data_snapshot` (`snapshot_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Annual market data';

-- No seed data - will be imported from Excel

-- ----------------------------------------------------------------
-- Table: fact_ownership_year
-- Description: Annual ownership structure data
-- ----------------------------------------------------------------
DROP TABLE IF EXISTS `fact_ownership_year`;
CREATE TABLE `fact_ownership_year` (
  `firm_id` bigint NOT NULL,
  `fiscal_year` smallint NOT NULL,
  `snapshot_id` bigint NOT NULL,
  `managerial_inside_own` decimal(10,6) DEFAULT NULL COMMENT 'Managerial/inside ownership ratio (0-1)',
  `state_own` decimal(10,6) DEFAULT NULL COMMENT 'State ownership ratio (0-1)',
  `institutional_own` decimal(10,6) DEFAULT NULL COMMENT 'Institutional ownership ratio (0-1)',
  `foreign_own` decimal(10,6) DEFAULT NULL COMMENT 'Foreign ownership ratio (0-1)',
  `note` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`firm_id`,`fiscal_year`,`snapshot_id`),
  KEY `fk_own_snapshot` (`snapshot_id`),
  CONSTRAINT `fk_own_firm` FOREIGN KEY (`firm_id`) REFERENCES `dim_firm` (`firm_id`),
  CONSTRAINT `fk_own_snapshot` FOREIGN KEY (`snapshot_id`) REFERENCES `fact_data_snapshot` (`snapshot_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Annual ownership structure';

-- No seed data - will be imported from Excel

-- ----------------------------------------------------------------
-- Table: fact_innovation_year
-- Description: Annual innovation indicators
-- ----------------------------------------------------------------
DROP TABLE IF EXISTS `fact_innovation_year`;
CREATE TABLE `fact_innovation_year` (
  `firm_id` bigint NOT NULL,
  `fiscal_year` smallint NOT NULL,
  `snapshot_id` bigint NOT NULL,
  `product_innovation` tinyint DEFAULT NULL COMMENT 'Product innovation dummy (0/1)',
  `process_innovation` tinyint DEFAULT NULL COMMENT 'Process innovation dummy (0/1)',
  `evidence_source_id` smallint DEFAULT NULL COMMENT 'Source of innovation evidence',
  `evidence_note` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`firm_id`,`fiscal_year`,`snapshot_id`),
  KEY `fk_innov_snapshot` (`snapshot_id`),
  KEY `fk_innov_source` (`evidence_source_id`),
  CONSTRAINT `fk_innov_firm` FOREIGN KEY (`firm_id`) REFERENCES `dim_firm` (`firm_id`),
  CONSTRAINT `fk_innov_snapshot` FOREIGN KEY (`snapshot_id`) REFERENCES `fact_data_snapshot` (`snapshot_id`),
  CONSTRAINT `fk_innov_source` FOREIGN KEY (`evidence_source_id`) REFERENCES `dim_data_source` (`source_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Annual innovation indicators';

-- No seed data - will be imported from Excel

-- ----------------------------------------------------------------
-- Table: fact_firm_year_meta
-- Description: Annual firm metadata (employees, age, etc.)
-- ----------------------------------------------------------------
DROP TABLE IF EXISTS `fact_firm_year_meta`;
CREATE TABLE `fact_firm_year_meta` (
  `firm_id` bigint NOT NULL,
  `fiscal_year` smallint NOT NULL,
  `snapshot_id` bigint NOT NULL,
  `employees_count` int DEFAULT NULL COMMENT 'Number of employees',
  `firm_age` smallint DEFAULT NULL COMMENT 'Firm age in years',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`firm_id`,`fiscal_year`,`snapshot_id`),
  KEY `fk_meta_snapshot` (`snapshot_id`),
  CONSTRAINT `fk_meta_firm` FOREIGN KEY (`firm_id`) REFERENCES `dim_firm` (`firm_id`),
  CONSTRAINT `fk_meta_snapshot` FOREIGN KEY (`snapshot_id`) REFERENCES `fact_data_snapshot` (`snapshot_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Annual firm metadata';

-- No seed data - will be imported from Excel

-- ----------------------------------------------------------------
-- Table: fact_value_override_log
-- Description: Audit log for manual data corrections
-- ----------------------------------------------------------------
DROP TABLE IF EXISTS `fact_value_override_log`;
CREATE TABLE `fact_value_override_log` (
  `override_id` bigint NOT NULL AUTO_INCREMENT,
  `firm_id` bigint NOT NULL,
  `fiscal_year` smallint NOT NULL,
  `table_name` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL,
  `column_name` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL,
  `old_value` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `new_value` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `reason` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `changed_by` varchar(80) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `changed_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`override_id`),
  KEY `fk_override_firm` (`firm_id`),
  CONSTRAINT `fk_override_firm` FOREIGN KEY (`firm_id`) REFERENCES `dim_firm` (`firm_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Audit log for data corrections';

-- No seed data - for future use

-- ================================================================
-- RESTORE MYSQL SETTINGS
-- ================================================================

/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;