DROP TABLE IF EXISTS `companies`; 
CREATE TABLE `companies`(
    `symbol` VARCHAR(255) NOT NULL,
    `company_name` VARCHAR(255) NOT NULL,
    `industry` VARCHAR(255) NOT NULL,
    `sector` VARCHAR(255) NOT NULL,
    `mktCap` BIGINT NOT NULL,
    `CEO` VARCHAR(255) NULL,
    `country` VARCHAR(255) NOT NULL,
    `fullTimeEmployees` BIGINT NOT NULL,
    `ipoDate` DATE NOT NULL,
    PRIMARY KEY(`symbol`)
);

DROP TABLE IF EXISTS `mergers_acquisitions`; 
CREATE TABLE `mergers_acquisitions`(
    `acquisition_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `acquisition_date` DATE NOT NULL,
    `acquisition_type` VARCHAR(255) NOT NULL,
    `acquired_company` VARCHAR(255) NOT NULL,
    `acquired_company_domain` VARCHAR(255) NOT NULL,
    `acquirer` VARCHAR(255) NOT NULL,
    `acquisition_price_usd` FLOAT(53) NOT NULL,
    `is_key_acquisition` BOOLEAN NOT NULL,
    `founded_year` BIGINT NOT NULL,
    `company_details_overview` VARCHAR(255) NOT NULL,
    `disclosed` BIGINT NOT NULL,
    `industry` VARCHAR(255) NOT NULL,
    `acquisition_year` BIGINT NOT NULL,
    `matured` BIGINT NOT NULL,
	`city` VARCHAR(255) NOT NULL,
    `state_province_region` VARCHAR(255) NOT NULL,
    `country` VARCHAR(255) NOT NULL

);
DROP TABLE IF EXISTS `income_statements`; 
CREATE TABLE `income_statements`(
    `statement_date_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `symbol` VARCHAR(255) NOT NULL,
    `statement_date` DATE NOT NULL,
    `revenue` BIGINT NOT NULL,
    `grossProfit` BIGINT NOT NULL,
    `operatingIncome` BIGINT NOT NULL,
    `netIncome` BIGINT NOT NULL,
    `eps` FLOAT(53) NOT NULL
);
DROP TABLE IF EXISTS `stock_prices`; 
CREATE TABLE `stock_prices`(
    `stock_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `symbol` VARCHAR(255) NOT NULL,
    `companyName` VARCHAR(255) NOT NULL,
    `price` FLOAT(53) NOT NULL,
    `changesPercentage` FLOAT(53) NOT NULL,
    `marketCap` BIGINT NOT NULL,
    `priceAvg50` FLOAT(53) NOT NULL,
    `priceAvg200` FLOAT(53) NOT NULL,
    `volume` BIGINT NOT NULL,
    `eps` FLOAT(53) NOT NULL,
    `pe` FLOAT(53) NOT NULL,
    `stock_timestamp` DATETIME NOT NULL
);
ALTER TABLE
    `income_statements` ADD CONSTRAINT `income_statements_symbol_foreign` FOREIGN KEY(`symbol`) REFERENCES `companies`(`symbol`);
ALTER TABLE
    `stock_prices` ADD CONSTRAINT `stock_prices_symbol_foreign` FOREIGN KEY(`symbol`) REFERENCES `companies`(`symbol`); 
-- Add an index to acquirer in mergers_acquisitions
ALTER TABLE `mergers_acquisitions` ADD INDEX (`acquirer`);

-- Fix the foreign key reference
ALTER TABLE 
	`mergers_acquisitions` ADD CONSTRAINT `mergers_acquisitions_acquirer_foreign` FOREIGN KEY(`acquirer`) REFERENCES `companies`(`symbol`);