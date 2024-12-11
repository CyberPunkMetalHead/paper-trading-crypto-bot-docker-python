DROP TABLE IF EXISTS paper_orders;

-- Create the paper_order table
CREATE TABLE paper_orders (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    buy_price FLOAT NOT NULL,
    quantity FLOAT NOT NULL,
    symbol VARCHAR(50) NOT NULL,
    direction VARCHAR(50) NOT NULL 
);
