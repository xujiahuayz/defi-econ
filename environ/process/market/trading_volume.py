"""
Script to preprocess the market volume data
"""

import pandas as pd
from environ.constants import GLOBAL_DATA_PATH

# load the dataframe with the market volume
df_volume = pd.read_csv(
    rf"{GLOBAL_DATA_PATH}/token_market/total_market_trading_volume.csv",
)

df_volume["Date"] = pd.to_datetime(df_volume["Date"], format="%Y-%m-%d")
