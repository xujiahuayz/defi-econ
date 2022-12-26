# -*- coding: utf-8 -*-
"""
Calculate the volatility by the prices of tokens
"""

from os import path
import pandas as pd
import numpy as np
from defi_econ.constants import GLOBAL_DATA_PATH


def calculate_volatility(price_series, window) -> np.ndarray:
    """
    Calculate the volatility by the input price series
    """
    # Initialize temp dataframe
    data = pd.DataFrame()

    # Data processing
    data["price"] = price_series.copy()
    data["log returns"] = np.log(data["price"] / data["price"].shift())
    data["std"] = data["log returns"].rolling(window, min_periods=1).std()
    data["annualized volatility"] = data["std"] * np.sqrt(365)

    return data["annualized volatility"].copy().values


def process_token_price_vol(vol_window) -> None:
    """
    Load the token price dataset and output the price volatility dataset
    """
    # Load the price dataset
    price_file = path.join(GLOBAL_DATA_PATH, "token_market/primary_token_price_2.csv")
    df_token_price = pd.read_csv(price_file, index_col=0)

    # Dataframe for the volatility
    df_price_volatility = df_token_price[["Date", "USDC"]].copy()

    # Iterate columns for the token symbol
    for col in df_token_price.columns:
        # Skip the data column for the token price dataset
        if col == "Date":
            continue

        # Calculate and Store to the volatility dataframe
        df_price_volatility[col] = calculate_volatility(df_token_price[col], vol_window)

    # Write to file
    vol_file = path.join(
        GLOBAL_DATA_PATH, "token_market/primary_token_volatility_2.csv"
    )
    df_price_volatility.to_csv(vol_file)


def process_gas_vol(vol_window) -> None:
    """
    Load the gas fee dataset and output the gas fee volatility dataset
    """
    # Load the price dataset
    price_file = path.join(GLOBAL_DATA_PATH, "gas_fee/avg_gas_fee.csv")
    df_gas = pd.read_csv(price_file, index_col=1)

    # Dataframe for the volatility
    df_gas_volatility = df_gas[["Date(UTC)", "Gas Fee USD"]].copy()

    # Calculate and Store to the volatility dataframe
    df_gas_volatility["volatility"] = calculate_volatility(
        df_gas["Gas Fee USD"], vol_window
    )

    # Write to file
    gas_vol_file = path.join(GLOBAL_DATA_PATH, "gas_fee/gas_volatility.csv")
    df_gas_volatility.to_csv(gas_vol_file)


if __name__ == "__main__":
    # Define the rolling window for calculating volatility
    rolling_window = 30

    # Token price volatility
    process_token_price_vol(rolling_window)

    # Gas fee volatility
    process_gas_vol(rolling_window)
