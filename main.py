import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from data_access.DAL.orders_DAL import OrdersDAL
from data_access.DAL.portfolio_DAL import PortfolioDAL
from data_access.DAL.coins_DAL import CoinsDAL
from services.coingecko_service import CoinGecko
from services.trading_service import TradingService
from workers.initializer import initialize_coin_data
from workers.price_updater import update_coin_prices
from utils.load_env import *
from datetime import datetime
import time

logging.disable(logging.CRITICAL)

# Create engine and session using the database URL from environment
engine = create_engine(db_url, echo=True)
Session = sessionmaker(bind=engine)
session = Session()

# Initialize DALs and Services
coins_dal = CoinsDAL(session)
orders_dal = OrdersDAL(session)
portfolio_dal = PortfolioDAL(session)
cg = CoinGecko()

# Populate database with initial data
initialize_coin_data()


# Function to handle buy logic
def handle_buy(coin, current_price):
    if coin.price_change < price_change:
        return

    # Buy and add order to the table
    order = TradingService.buy(coin.symbol, current_price, qty)

    existing_portfolio = portfolio_dal.get_portfolio_item_by_symbol(order.symbol)

    if existing_portfolio is None:
        portfolio_dal.insert_portfolio_item(
            order.symbol, order.buy_price, order.quantity
        )
        print(
            f"Bought {order.symbol} and inserted new portfolio item for {order.symbol}"
        )
    else:
        cost_basis = TradingService.calculate_cost_basis(
            existing_portfolio.cost_basis,
            existing_portfolio.total_quantity,
            order.quantity,
            order.buy_price,
        )
        portfolio_dal.update_portfolio_item_by_symbol(
            order.symbol, cost_basis, order.quantity
        )
        print(
            f"Bought {order.symbol}. We already hold {order.symbol}, updating existing portfolio with new order data."
        )
    orders_dal.insert_order(
        order.timestamp, order.buy_price, order.quantity, order.symbol, order.direction
    )


# Function to handle sell logic
def handle_sell(coin, current_price):
    buy_orders = orders_dal.get_all_orders("BUY")

    # Filter buy orders for the current symbol
    filtered_buy_orders = [order for order in buy_orders if order.symbol == coin.symbol]

    if not filtered_buy_orders:
        return

    for order in filtered_buy_orders:
        stop_loss_price = order.buy_price * (1 - sl / 100)
        take_profit_price = order.buy_price * (1 + tp / 100)
        current_pnl = (current_price - order.buy_price) / order.buy_price * 100

        if current_price <= stop_loss_price:
            sell_order = TradingService.sell(
                order.symbol, current_price, order.quantity
            )
            print(
                f"Stop Loss Triggered: Sold {order.quantity} of {order.symbol} at ${current_price}"
            )

        elif current_price >= take_profit_price:
            sell_order = TradingService.sell(
                order.symbol, current_price, order.quantity
            )
            print(
                f"Take Profit Triggered: Sold {order.quantity} of {order.symbol} at ${current_price}"
            )
        else:
            continue
        orders_dal.insert_order(
            sell_order.timestamp,
            sell_order.buy_price,
            sell_order.quantity,
            sell_order.symbol,
            sell_order.direction,
        )
        coins_dal.update_coin_pnl(order.symbol, current_pnl)


# Main execution logic
def main():
    print("Starting up database...")
    time.sleep(5)
    while True:
        api_coins = update_coin_prices()
        for coin in api_coins:
            current_price = coin.prices[0].value
            handle_buy(coin, current_price)
            handle_sell(coin, current_price)
            portfolio_dal.add_pnl_entry_by_symbol(
                coin.symbol, datetime.now(), coin.prices[0].value
            )
        print("Engine cycle complete, sleeping for 1 hour.")
        time.sleep(3600)


if __name__ == "__main__":
    main()
