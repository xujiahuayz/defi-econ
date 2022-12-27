# -*- coding: utf-8 -*-
"""
Fetch the compound data by Compound official API
"""
from os import path
import time
from tqdm import tqdm
from datetime import datetime, timedelta
import calendar
import requests
import pandas as pd
import numpy as np
from environ.utils.config_parser import Config


def fetch_asset_historical_data(
    asset_address: str, min_timestamp: int, max_timestamp: int, horizon: int
) -> tuple[dict, dict, dict, dict, dict]:
    """
    get the snapshot of the asset historical data during the given horizon
    """
    market_history_url = "https://api.compound.finance/api/v2/market_history/graph"
    ctoken_params = {
        "asset": asset_address,
        "min_block_timestamp": min_timestamp,
        "max_block_timestamp": max_timestamp,
        "num_buckets": horizon,
        "network": "mainnet",
    }

    token_history_result = requests.get(url=market_history_url, params=ctoken_params)
    token_history_result = token_history_result.json()

    total_supply_dict = token_history_result["total_supply_history"]
    total_borrow_dict = token_history_result["total_borrows_history"]
    price_dict = token_history_result["prices_usd"]
    exchange_rate_dict = token_history_result["exchange_rates"]

    return total_supply_dict, total_borrow_dict, price_dict, exchange_rate_dict


def fetch_comp_historical_data(start_date: datetime, end_date: datetime) -> None:

    """
    Fetch compound historical data.
    """

    # Initialize configuration
    config = Config()

    # Define the asset (symbol of underlying asset + ctoken address)
    compound_assets = {
        "ETH": "0x4ddc2d193948926d02f9b1fe9e1daa0718270ed5",
        "USDC": "0x39aa39c021dfbae8fac545936693ac917d5e7563",
        "USDT": "0xf650c3d88d12db855b8bf7d11be6c55a4e07dcc9",
        "WBTC": "0xc11b1268c1a384e55c48c2391d8d480264a3a7f4",
        "DAI": "0x5d3a536e4d6dbd6114cc1ead35777bab948e3643",
        "UNI": "0x35a18000230da775cac24873d00ff85bccded550",
        "SAI": "0xf5dce57282a584d2746faf1593d3121fcac444dc",
        "REP": "0x158079ee67fce2f58472a96584a73c7ab9ac95c1",
        "MKR": "0x95b4ef2869ebd94beb4eee400a99824bf5dc325b",
        "YFI": "0x80a2ae356fc9ef4305676f7a3e2ed04e12c33946",
        "USDP": "0x041171993284df560249b57358f931d9eb7b925d",
        "ZRX": "0xb3319f5d18bc0d84dd1b4825dcde5d5f7266d407",
        "SUSHI": "0x4b0181102a0112a2ef11abee5563bb4a3176c9d7",
        "FEI": "0x7713dd9ca933848f6819f38b8352d9a15ea73f67",
        "BAT": "0x6c8c6b02e7b2be14d4fa6022dfd6d75921d90e4e",
        "COMP": "0x70e36f6bf80a52b3b46b3af8e106cc0ed743e8e4",
        "TUSD": "0x12392f67bdf24fae0af363c24ac620a2f67dad86",
        "AAVE": "0xe65cdb6479bac1e22340e4e755fae7e509ecd06c",
        "LINK": "0xface851a4921ce59e912d19329929ce6da6eb0c7",
    }

    df_compound_assets = pd.DataFrame(
        list(compound_assets.items()), columns=["underlying_symbol", "ctoken_address"]
    )

    # Convert the date (UTC) to unix timestamp
    start_timestamp = int(calendar.timegm(start_date.timetuple()))
    end_timestamp = int(calendar.timegm(end_date.timetuple()))

    # Calculate the horizon
    horizon = int((end_date - start_date).days)

    # Date list
    date_list = []
    for date_count in range(horizon):
        date = start_date + timedelta(days=date_count)
        date_list.append(date)

    # Initialize a dataframe to store the whole result
    df_compound = pd.DataFrame()

    # Do iteration for each ctoken
    for _, row in tqdm(
        df_compound_assets.iterrows(), total=df_compound_assets.shape[0]
    ):
        # ctoken address, not underlying asset address
        ctoken_symbol = row["underlying_symbol"]
        ctoken_address = row["ctoken_address"]

        # get the total supply and borrow (json)
        (
            supply_result,
            borrow_result,
            price_result,
            exchange_rate_result,
        ) = fetch_asset_historical_data(
            ctoken_address, start_timestamp, end_timestamp, horizon
        )

        # list of timestamps
        timestamp_values = []
        for i in supply_result:
            utc_dt = datetime.utcfromtimestamp(int(i["block_timestamp"]))
            timestamp_values.append(utc_dt)

        # list of supply values
        supply_values = []
        for i in supply_result:
            supply_values.append(float(i["total"]["value"]))

        # list of borrow values
        borrow_values = []
        for i in borrow_result:
            borrow_values.append(float(i["total"]["value"]))

        # list of prices
        price_values = []
        for i in price_result:
            price_values.append(float(i["price"]["value"]))

        # list of exchange rates
        exchange_rate_values = []
        for i in exchange_rate_result:
            exchange_rate_values.append(float(i["rate"]))

        # derived values
        total_supply_underlying = np.multiply(supply_values, exchange_rate_values)
        total_supply_usd = np.multiply(total_supply_underlying, price_values)
        total_borrow_usd = np.multiply(borrow_values, price_values)

        # create a dataframe for this asset
        df_asset_history = pd.DataFrame(
            {
                "ctoken_symbol": ctoken_symbol,
                "date": timestamp_values,
                "total_supply": total_supply_usd,
                "total_borrow": total_borrow_usd,
            }
        )

        # Add to the whole dataset frame
        df_compound = pd.concat(
            [df_compound, df_asset_history], ignore_index=True, axis=0
        )

        # Separate file
        file_name = path.join(
            config["dev"]["config"]["data"]["COMPOUND_DATA_PATH"],
            "compound_" + ctoken_symbol + ".csv",
        )
        df_asset_history.to_csv(file_name)
        time.sleep(1)