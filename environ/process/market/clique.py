"""
Script to calculate the clique of a market.
"""

import pandas as pd

from environ.constants import GLOBAL_DATA_PATH

# Read in the data
df_clique = pd.read_csv(GLOBAL_DATA_PATH / "token_market" / "clique.csv")

# convert the date column to datetime
df_clique["Date"] = pd.to_datetime(df_clique["Date"])
