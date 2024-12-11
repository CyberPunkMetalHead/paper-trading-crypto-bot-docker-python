import os
from typing import List
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from data_access.DAL.coins_DAL import CoinsDAL
from data_access.models.coin import Coin
from services.coingecko_service import CoinGecko
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL")


def update_coin_prices() -> List[Coin]:
    engine = create_engine(DATABASE_URL, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    coins_dal = CoinsDAL(session)
    cg = CoinGecko()
    db_coins = coins_dal.get_all_coins()
    db_coins_ids = [coin.coin_id for coin in db_coins]

    if len(db_coins) == 0:
        print("There are no coins in the database, cannot add prices")
        return

    coin_list = cg.get_coin_list()
    new_coins = 0
    for coin in coin_list:
        if coin.coin_id not in db_coins_ids:
            new_coins += 1
            coins_dal.add_coin(coin.symbol, coin.coin_id)

        coins_dal.add_price_to_coin(coin.symbol, datetime.now(), coin.prices[0].value)
    print(f"Price updated for {len(db_coins)} coins")
    print(
        f"Inserted {new_coins} coins to the coins table likely due movements in the top 250."
    )
    return coin_list
