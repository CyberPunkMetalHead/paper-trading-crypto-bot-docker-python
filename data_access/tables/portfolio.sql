DROP TABLE IF EXISTS pnl_entries;
DROP TABLE IF EXISTS portfolio_items;

-- Create the portfolio_item table
CREATE TABLE portfolio_items (
    id SERIAL PRIMARY KEY,
    cost_basis FLOAT NOT NULL,
    total_quantity FLOAT NOT NULL,
    symbol VARCHAR(50) NOT NULL
);

-- Create the pnl_entry table
CREATE TABLE pnl_entries (
    id SERIAL PRIMARY KEY,
    portfolio_item_id INTEGER NOT NULL, -- Foreign key referencing the portfolio_item table
    date TIMESTAMP NOT NULL,
    value FLOAT NOT NULL,
    CONSTRAINT fk_portfolio_item FOREIGN KEY (portfolio_item_id)
        REFERENCES portfolio_items (id) ON DELETE CASCADE
);
