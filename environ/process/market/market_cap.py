"""
Script to get the market cap of a given dataset.
"""
import numpy as np
import pandas as pd

from environ.constants import GLOBAL_DATA_PATH

# read in the csv file
mcap = pd.read_csv(
    rf"{GLOBAL_DATA_PATH}/token_market/primary_token_marketcap_2.csv",
    index_col=None,
    header=0,
)

# convert date in "YYYY-MM-DD" to datetime
mcap["Date"] = pd.to_datetime(mcap["Date"], format="%Y-%m-%d")

# drop the column "Unnamed: 0"
mcap = mcap.drop(columns=["Unnamed: 0"])

# sort the time series
mcap = mcap.sort_values(by="Date", ascending=True)

# drop the WETH column
mcap = mcap.drop(columns=["WETH"])

# load in the ethereum.csv from data/data_global/coingecko/token_data
ethereum = pd.read_csv(rf"{GLOBAL_DATA_PATH}/coingecko/token_data/ethereum.csv")

# only keep the time and market_caps columns
ethereum = ethereum[["time", "market_caps"]]

# rename the columns
ethereum.columns = ["Date", "WETH"]

# convert date in "YYYY-MM-DD" to datetime
ethereum["Date"] = pd.to_datetime(ethereum["Date"], format="%Y-%m-%d")

# only keep the rows with Date >= 2019-01-01 <= 2023-02-01
ethereum = ethereum[
    (ethereum["Date"] >= "2019-01-01") & (ethereum["Date"] <= "2023-02-01")
]

# merge the ethereum dataframe with the mcap dataframe
mcap = pd.merge(mcap, ethereum, on="Date", how="left")

# set the index to be the Date column
mcap = mcap.set_index("Date")

# convert the dataframe to panel
mcap = mcap.stack().reset_index()

# rename the column "level_1" to "Token"
mcap = mcap.rename(columns={"level_1": "Token"})

# rename the column "0" to "mcap"
mcap = mcap.rename(columns={0: "mcap"})

# # take the log of mcap
# mcap["log_mcap"] = mcap["mcap"].apply(lambda x: np.log(x))

# remove inf and -inf
mcap = mcap.replace([np.inf, -np.inf], np.nan)

# drop the rows with NaN
mcap = mcap.dropna()
