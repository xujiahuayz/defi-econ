# -*- coding: utf-8 -*-
"""
Fetch the historical price and market cap for tokens from coingecko
Note: the data for market cap of WETH is not available so that it is calculated by FULLY DILUTED MARKET CAP
Key: Infura key is needed
"""

import time
import calendar
from datetime import datetime, timedelta
from os import path
import requests
import pandas as pd
import numpy as np
from web3 import Web3

# Unofficial API python package for CoinGeckoAPI
# * Attribution required: https://www.coingecko.com/en/api
from pycoingecko import CoinGeckoAPI
from defi_econ.constants import GLOBAL_DATA_PATH


# Get the total supply by calling the totalSupply() function from archive node
def get_total_supply(
    contract_address: str, contract_abi: str, block_number: int
) -> str:
    """
    get the total supply of given token via Infura archive node
    """
    # Config Infura
    Infura_HTTP = "YOUR_INFURA_HTTP_KEY"
    w3 = Web3(Web3.HTTPProvider(Infura_HTTP))

    # Get the contract
    contract = w3.eth.contract(contract_address, abi=contract_abi)

    # Get the total supply
    total_supply = contract.functions.totalSupply().call(block_identifier=block_number)

    # Convert Wei to ETH
    total_supply_eth = w3.fromWei(total_supply, "ether")

    return total_supply_eth


def get_block_number_by_timestamp(timestamp: int) -> str:
    """
    get the closest block number by the given timestamp
    """
    # convert timestamp to str
    timestamp = str(timestamp)

    # Define the api address
    etherscan_api = "https://api.etherscan.io/api"
    get_blockno_by_time_params = {
        "module": "block",
        "action": "getblocknobytime",
        "timestamp": timestamp,
        "closest": "before",
        "apikey": "YOUR_ETHERSCAN_API_KEY",
    }
    query_block_number = requests.get(
        url=etherscan_api, params=get_blockno_by_time_params
    )
    block_number = query_block_number.json()

    # Return type: str
    return block_number["result"]


if __name__ == "__main__":
    # Define the horizon of fecting historical data
    start_date = datetime(2020, 1, 1, 0, 0)
    end_date = datetime(2022, 7, 1, 0, 0)

    # Define the currency of unit
    target_currency = "usd"

    # Refer to CoinGecko API Token List
    # https://docs.google.com/spreadsheets/d/1wTTuxXt8n9q7C4NDXqQpI3wpKu1_5bGVmP9Xz0XGSyU/edit#gid=0
    # token symbol is not unique variable, so that manually check from the doc to get id is recommended
    primary_token_dict = {
        "USDC": "usd-coin",
        "WETH": "weth",
        "DAI": "dai",
        "WBTC": "wrapped-bitcoin",
        "USDT": "tether",
        "FRAX": "frax",
        "PAX": "paxos-standard",
        "agEUR": "ageur",
        "APE": "apecoin",
        "1INCH": "1inch",
        "BUSD": "binance-usd",
        "FEI": "fei-usd",
        "HEX": "hex",
        "RAI": "rai",
        "LOOKS": "looksrare",
        "renBTC": "renbtc",
        "MKR": "maker",
        "LINK": "chainlink",
        "ETH2x-FLI": "eth-2x-flexible-leverage-index",
        "MATIC": "matic-network",
        "TUSD": "true-usd",
        "EURS": "stasis-eurs",
        "CRV": "curve-dao-token",
        "NEXO": "nexo",
        "FUN": "funfair",
        "ENS": "ethereum-name-service",
        "LUNA": "terra-luna-2",
        "MIM": "magic-internet-money",
        "LUSD": "liquity-usd",
    }

    # Convert the date (UTC) to unix timestamp
    start_timestamp = int(calendar.timegm(start_date.timetuple()))
    end_timestamp = int(calendar.timegm(end_date.timetuple()))

    # List of candidate dates
    candidate_date = []
    candidate_timestamp = []
    for date_count in range((end_date - start_date).days + 1):
        aggregate_date = start_date + timedelta(days=date_count)
        candidate_date.append(aggregate_date)
        candidate_timestamp.append(int(calendar.timegm(aggregate_date.timetuple())))

    # Initialize the dataframe for the historical data
    df_price = pd.DataFrame({"Date": candidate_date}, index=candidate_timestamp)
    df_marketcap = pd.DataFrame({"Date": candidate_date}, index=candidate_timestamp)

    # Initialize the CoinGeckoAPI instance
    cg = CoinGeckoAPI()

    # Iterate for fetching the historical data
    for symbol, coin_id in primary_token_dict.items():
        # Fetch the data
        print(coin_id)
        token_historical_data = cg.get_coin_market_chart_range_by_id(
            id=coin_id,
            vs_currency=target_currency,
            from_timestamp=start_timestamp,
            to_timestamp=end_timestamp,
        )

        # keep speed limitation
        time.sleep(3)

        # Initialize the column for token
        df_price[symbol] = np.nan
        df_marketcap[symbol] = np.nan

        # Store the value
        for price_pair in token_historical_data["prices"]:
            df_price.loc[price_pair[0] / 1000, symbol] = price_pair[1]

        # Store the value
        for mktcap_pair in token_historical_data["market_caps"]:
            df_marketcap.loc[mktcap_pair[0] / 1000, symbol] = mktcap_pair[1]

    # Calculate the market cap for WETH
    # Define the constant variable of WETH
    weth_contract = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    weth_abi = [
        {
            "inputs": [],
            "name": "totalSupply",
            "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function",
        }
    ]

    # Do iteration for each day
    for timestamp in df_price.index:
        # timestamp of 23:59:59 for each day like the "close price"
        close_timestamp = timestamp + 86400 - 1

        # Get the block number by the timestamp
        block_number = int(get_block_number_by_timestamp(close_timestamp))
        # Limit the API access speed
        time.sleep(0.03)

        # Get the total supply of token
        weth_total_supply = float(
            get_total_supply(weth_contract, weth_abi, block_number)
        )

        # Get the historical WETH price
        weth_price = float(df_price.loc[timestamp, "WETH"])

        # Calculate the market cap
        weth_market_cap = weth_total_supply * weth_price

        # Store value to the dataframe
        df_marketcap.loc[timestamp, "WETH"] = weth_market_cap

    # Write data to csv
    price_file_name = path.join(
        GLOBAL_DATA_PATH, "token_market/primary_token_price.csv"
    )
    marketcap_file_name = path.join(
        GLOBAL_DATA_PATH, "/token_market/primary_token_marketcap.csv"
    )
    df_price.to_csv(price_file_name)
    df_marketcap.to_csv(marketcap_file_name)
