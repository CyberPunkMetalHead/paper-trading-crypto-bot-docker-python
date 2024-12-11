import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from data_access.DAL.coins_DAL import CoinsDAL
from services.coingecko_service import CoinGecko

DATABASE_URL = os.getenv("DATABASE_URL")


def initialize_coin_data():
    # Create engine and session using the database URL from environment
    engine = create_engine(DATABASE_URL, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    coins_dal = CoinsDAL(session)
    if len(coins_dal.get_all_coins()) > 0:
        print("DB already initalized, skipping...")
        return

    cg = CoinGecko()

    all_coins = cg.get_coin_list()

    # Add coins and their initial prices to the list
    for coin in all_coins:
        coins_dal.add_coin(coin.symbol, coin.coin_id)
        coins_dal.add_price_to_coin(
            coin.symbol, coin.prices[0].timestamp, coin.prices[0].value
        )
    session.close()
    print(f"Added {len(all_coins)} coins.")
    print(f"Added Prices to {len(all_coins)} coins.")
