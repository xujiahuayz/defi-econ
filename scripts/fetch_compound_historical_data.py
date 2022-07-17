# -*- coding: utf-8 -*-


import requests
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import calendar
from defi_econ.constants import DATA_PATH
from os import path


def fetch_asset_historical_data(asset_address, min_timestamp, max_timestamp, horizon):
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


if __name__ == "__main__":
    # Define the asset (symbol of underlying asset + ctoken address)
    compound_assets = {
        "ETH": "0x4ddc2d193948926d02f9b1fe9e1daa0718270ed5",
        "USDC": "0x39aa39c021dfbae8fac545936693ac917d5e7563",
        "USDT": "0xf650c3d88d12db855b8bf7d11be6c55a4e07dcc9",
        "WBTC": "0xc11b1268c1a384e55c48c2391d8d480264a3a7f4",
        "DAI": "0x5d3a536e4d6dbd6114cc1ead35777bab948e3643",
        "UNI": "0x35a18000230da775cac24873d00ff85bccded550",
    }

    df_compound_assets = pd.DataFrame(
        list(compound_assets.items()), columns=["underlying_symbol", "ctoken_address"]
    )

    # Define the horizon of fecting historical data
    start_date = datetime(2021, 1, 1, 0, 0)
    end_date = datetime(2022, 6, 1, 0, 0)

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
    for index, row in df_compound_assets.iterrows():
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
                "date": date_list,
                "total_supply": total_supply_usd,
                "total_borrow": total_borrow_usd,
            }
        )
        # Add to the whole dataset frame
        df_compound = pd.concat(
            [df_compound, df_asset_history], ignore_index=True, axis=0
        )

        # Separate file
        file_name = path.join(DATA_PATH, "compound_" + ctoken_symbol + ".csv")
        df_asset_history.to_csv(file_name)

        time.sleep(1)
