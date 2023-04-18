"""
Script to get the average clustering coefficient
"""

import pandas as pd

from environ.constants import GLOBAL_DATA_PATH

# load the dataframe with the average clustering coefficient
avg_cluster_df = pd.read_csv(
    str(GLOBAL_DATA_PATH / "token_market" / "cluster_coef.csv")
)

# convert the date to datetime
avg_cluster_df["Date"] = pd.to_datetime(avg_cluster_df["Date"])
