"""
Script to fetch the historical price, market capitalization, and volume data from CoinGecko API.
"""

import pandas as pd
from pycoingecko import CoinGeckoAPI
from environ.utils.config_parser import Config

# Initialize config
config = Config()

# Initialize data path
GLOBAL_DATA_PATH = config["dev"]["config"]["data"]["GLOBAL_DATA_PATH"]

# Initialize CoinGecko API
cg = CoinGeckoAPI()


def fetch_market_data_coingecko() -> None:
    """
    Function to fetch the market data from CoinGecko API.
    """

    # coingecko api
    market_data = cg.get_coins_markets(vs_currency="usd")

    print(market_data)


if __name__ == "__main__":
    fetch_market_data_coingecko()
