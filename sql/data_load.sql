SET GLOBAL local_infile = 'ON';
SHOW GLOBAL VARIABLES LIKE 'local_infile';
SHOW VARIABLES LIKE 'secure_file_priv';

-- Companies Table (change path to yours)
LOAD DATA LOCAL INFILE '/Users/ricardogolding/Documents/Ironhack/Bootcamp/Week8/Final_Project/sql/data/clean_profiles.csv'
INTO TABLE companies
FIELDS TERMINATED BY ';' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

select * from companies;

-- Income Statements Table (change path to yours)
LOAD DATA LOCAL INFILE '/Users/ricardogolding/Documents/Ironhack/Bootcamp/Week8/Final_Project/sql/data/clean_income_statements.csv'
INTO TABLE income_statements
FIELDS TERMINATED BY ';' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(symbol, statement_date, revenue, grossProfit, operatingIncome, netIncome, eps);

SELECT * FROM income_statements;

-- Stocks Table (change path to yours)
LOAD DATA LOCAL INFILE '/Users/ricardogolding/Documents/Ironhack/Bootcamp/Week8/Final_Project/sql/data/clean_stock_prices.csv'
INTO TABLE stock_prices
FIELDS TERMINATED BY ';'
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(symbol, companyName, price, changesPercentage, marketCap, priceAvg50, priceAvg200, volume, eps, pe, @stock_timestamp)
SET stock_timestamp = STR_TO_DATE(@stock_timestamp, '%Y-%m-%d %H:%i:%s');

select * from stock_prices;

-- Mergers & Acquisition Table (change path to yours)
LOAD DATA LOCAL INFILE '/Users/ricardogolding/Documents/Ironhack/Bootcamp/Week8/Final_Project/sql/data/clean_mergers_acquisitions.csv'
INTO TABLE mergers_acquisitions
FIELDS TERMINATED BY ';' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(acquisition_date, acquisition_type, acquired_company, acquired_company_domain, acquirer, acquisition_price_usd, @is_key_acquisition, founded_year, location, company_details_overview, disclosed, industry, acquisition_year, @matured)
SET
  is_key_acquisition = IF(@is_key_acquisition='True',1,0),
  matured = IF(@matured='True',1,0);

select * from mergers_acquisitions;
