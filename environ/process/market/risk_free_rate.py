"""
Script to fetch the risk-free rate from the Fama French library
"""

import pandas as pd
from environ.constants import (
    GLOBAL_DATA_PATH,
)

# load the risk free rate
df_rf = pd.read_csv(
    GLOBAL_DATA_PATH / "risk_free_rate/risk_free_rate.csv",
    parse_dates=["Date"],
)

# divide the risk free rate by 100
df_rf["RF"] = df_rf["RF"] / 100

# convert the date to datetime
df_rf["Date"] = pd.to_datetime(df_rf["Date"], format="%Y%m%d")
