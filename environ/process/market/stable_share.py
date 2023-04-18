"""
Script to get the stable share of a given dataset.
"""

import pandas as pd

from environ.constants import GLOBAL_DATA_PATH

# read the stablecoin share data
stable_share_df = pd.read_csv(
    GLOBAL_DATA_PATH / "stablecoin" / "stablecoin_share.csv",
)

# convert the date to datetime
stable_share_df["Date"] = pd.to_datetime(stable_share_df["Date"])
