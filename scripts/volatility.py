# -*- coding: utf-8 -*-
"""
Calculate the volatility by the prices of tokens
"""

from os import path
import pandas as pd
import numpy as np
from defi_econ.constants import GLOBAL_DATA_PATH


def calculate_volatility(df_token_price, window) -> pd.DataFrame:
    """
    Calculate the volatility by the columns of the dataframe
    """
    # Dataframe for the volatility
    df_volatility = df_token_price[["Date", "USDC"]].copy()

    # Iterate columns for the token symbol
    for col in df_token_price.columns:
        if col == "Date":
            continue

        # Initialize temp dataframe
        data = pd.DataFrame()

        # Data processing
        data["price"] = df_token_price[col].copy()
        data["log returns"] = np.log(data["price"] / data["price"].shift())
        data["std"] = data["log returns"].rolling(window, min_periods=1).std()
        data["annualized volatility"] = data["std"] * np.sqrt(365)
        # data["annualized volatility"] = data["log returns"].std() * 365**0.5

        # Store to the volatility dataframe
        df_volatility[col] = data["annualized volatility"].copy().values

    return df_volatility


if __name__ == "__main__":
    # Load the price dataset
    price_file = path.join(GLOBAL_DATA_PATH, "token_market/primary_token_price.csv")
    df_token_price = pd.read_csv(price_file, index_col=0)

    # Calculate
    df_vol = calculate_volatility(df_token_price, 30)

    # Write to file
    vol_file = path.join(GLOBAL_DATA_PATH, "token_market/primary_token_volatility.csv")
    df_vol.to_csv(vol_file)
