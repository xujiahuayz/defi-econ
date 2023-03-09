"""
Function to construct the unit-of-account proxy.
"""

import pandas as pd
import numpy as np
from environ.utils.config_parser import Config

# Initialize config
config = Config()

# Initialize data path
GLOBAL_DATA_PATH = config["dev"]["config"]["data"]["GLOBAL_DATA_PATH"]


def _market_cap(reg_panel: pd.DataFrame) -> pd.DataFrame:
    """
    Function to merge the market capitalization.
    """

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

    # take the log of mcap
    mcap["mcap"] = mcap["mcap"].apply(lambda x: np.log(x))

    # remove inf and -inf
    mcap = mcap.replace([np.inf, -np.inf], np.nan)

    # drop the rows with NaN
    mcap = mcap.dropna()

    # merge the mcap into reg_panel
    reg_panel = pd.merge(reg_panel, mcap, how="outer", on=["Date", "Token"])

    return reg_panel


def _dollar_exchange_rate(reg_panel: pd.DataFrame) -> pd.DataFrame:
    """
    Function to merge the dollar exchange rate.
    """

    # read in the csv file
    dollar = pd.read_csv(
        rf"{GLOBAL_DATA_PATH}/token_market/primary_token_price_2.csv",
        index_col=None,
        header=0,
    )

    # convert date in "YYYY-MM-DD" to datetime
    dollar["Date"] = pd.to_datetime(dollar["Date"], format="%Y-%m-%d")

    # shift the date by one day
    dollar["Date"] = dollar["Date"] + pd.DateOffset(days=-1)

    # drop the column "Unnamed: 0"
    dollar = dollar.drop(columns=["Unnamed: 0"])

    # sort the time series
    dollar = dollar.sort_values(by="Date", ascending=True)

    # set the index to be the Date column
    dollar = dollar.set_index("Date")

    # convert the dataframe to panel
    dollar = dollar.stack().reset_index()

    # rename the column "level_1" to "Token"
    dollar = dollar.rename(columns={"level_1": "Token"})

    # rename the column "0" to "dollar"
    dollar = dollar.rename(columns={0: "dollar_exchange_rate"})

    # # take the log of dollar
    # dollar["dollar_exchange_rate"] = dollar["dollar_exchange_rate"].apply(
    #     lambda x: np.log(x)
    # )

    # remove inf and -inf
    dollar = dollar.replace([np.inf, -np.inf], np.nan)

    # drop the rows with nan
    dollar = dollar.dropna()

    # merge the dollar into reg_panel
    reg_panel = pd.merge(reg_panel, dollar, how="outer", on=["Date", "Token"])

    return reg_panel


def pegging_degree(price: float) -> float:
    """
    Function to calculate the pegging degree.
    """
    if price < 0:
        raise ValueError("Price cannot be negative.")
    x = 1 / max(0.01, price) if price < 1 else price
    return 2 / x - 1


def _merge_pegging(reg_panel: pd.DataFrame) -> pd.DataFrame:
    """
    Function to merge the pegging degree.
    """

    reg_panel["pegging_degree"] = reg_panel["Stable"] * (
        reg_panel["dollar_exchange_rate"]
    ).apply(pegging_degree)

    return reg_panel


def _merge_stable_deviation(reg_panel: pd.DataFrame) -> pd.DataFrame:
    """
    Function to merge the stablecoin deviation.
    """

    reg_panel["stablecoin_deviation"] = (
        reg_panel["Stable"] * (reg_panel["dollar_exchange_rate"] - 1) ** 2
    )

    return reg_panel


def unit_of_acct(reg_panel: pd.DataFrame) -> pd.DataFrame:
    """
    Function to construct the unit-of-account proxy.
    """
    # merge the market capitalization
    reg_panel = _market_cap(reg_panel)

    # merge the dollar exchange rate
    reg_panel = _dollar_exchange_rate(reg_panel)

    # merge the stablecoin deviation
    # reg_panel = _merge_stable_deviation(reg_panel)

    # merge the pegging degree
    reg_panel = _merge_pegging(reg_panel)

    return reg_panel.loc[
        (reg_panel["Date"] >= "2020-06-01") & (reg_panel["Date"] < "2023-02-01")
    ]
