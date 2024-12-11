DROP TABLE IF EXISTS coins;
DROP TABLE IF EXISTS coins_prices;

-- Create the coin table
CREATE TABLE coins (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(50) NOT NULL UNIQUE,  
    coin_id TEXT NOT NULL,    
    realized_pnl FLOAT
);

-- Create the coin_price table
CREATE TABLE coins_prices (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(50) NOT NULL, -- Foreign key referencing the coin table
    timestamp TIMESTAMP NOT NULL,
    value FLOAT NOT NULL,
    CONSTRAINT fk_coin FOREIGN KEY (symbol)
        REFERENCES coins (symbol) ON DELETE CASCADE
);
