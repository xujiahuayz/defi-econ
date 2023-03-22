# -*- coding: utf-8 -*-
"""
Fetch the compound data by Compound official API
"""
from os import path
import pandas as pd

from environ.utils.config_parser import Config

# Initiating the config
config = Config()

# TODO: use the compound dictionary from constants.py
# set the constants
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
    "WBTC2": "0xccF4429DB6322D5C611ee964527D42E5d685DD6a",
}


def prepare_compound_data() -> None:
    """
    A function to calculate the boroow and supply rate for each asset
    """

    for ctoken_symbol in compound_assets.keys():

        # Set the path to load in the data
        file_name = path.join(
            config["dev"]["config"]["data"]["COMPOUND_DATA_PATH"],
            "compound_" + ctoken_symbol + ".csv",
        )

        # Load the data from the csv file

        def calculate_borrow_supply(file_name: str) -> pd.DataFrame:
            compound_info = pd.read_csv(file_name)

            # Calculate the borrow rata in USD
            compound_info["total_borrow_usd"] = (
                compound_info["total_borrows_history"] * compound_info["prices_usd"]
            )
            compound_info["total_supply_usd"] = (
                compound_info["total_supply_history"]
                * compound_info["exchange_rates"]
                * compound_info["prices_usd"]
            )
            # convert the timestamp to datetime
            compound_info["block_timestamp"] = pd.to_datetime(
                compound_info["block_timestamp"], unit="s"
            )
            return compound_info

        # Calculate the borrow and supply in USD
        compound_info = calculate_borrow_supply(file_name)

        if ctoken_symbol == "WBTC":
            file_name = path.join(
                config["dev"]["config"]["data"]["COMPOUND_DATA_PATH"],
                "compound_" + "WBTC2" + ".csv",
            )

            # Calculate the borrow and supply in USD
            compound_info2 = calculate_borrow_supply(file_name)

            compound_info = pd.concat(
                [compound_info, compound_info2], ignore_index=True
            )
            compound_info = (
                compound_info.groupby(["block_timestamp"])[
                    ["total_borrow_usd", "total_supply_usd"]
                ]
                .sum()
                .reset_index()
            )

        # skip the wbtc2 data
        if ctoken_symbol == "WBTC2":
            continue

        # sort the data by timestamp
        compound_info = compound_info.sort_values(by=["block_timestamp"])

        # set the new file name
        file_name = path.join(
            config["dev"]["config"]["data"]["COMPOUND_DATA_PATH"],
            "compound_" + ctoken_symbol + "_processed.csv",
        )

        # save the data to csv
        compound_info.to_csv(file_name, index=False)


if __name__ == "__main__":
    prepare_compound_data()
