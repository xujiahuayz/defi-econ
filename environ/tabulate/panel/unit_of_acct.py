"""
Function to construct the unit-of-account proxy.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
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

    # merge the mcap into reg_panel
    reg_panel = pd.merge(reg_panel, mcap, how="outer", on=["Date", "Token"])

    return reg_panel


def _merge_mcap_share(reg_panel: pd.DataFrame) -> pd.DataFrame:
    """
    Function to merge the market capitalization share.
    """

    # group the reg_panel by date
    group = reg_panel.groupby("Date")

    # calculate the sum of mcap
    sum_mcap = group["mcap"].sum().reset_index()

    # rename the column "mcap" to "sum_mcap"
    sum_mcap = sum_mcap.rename(columns={"mcap": "sum_mcap"})

    # merge the sum_mcap into reg_panel
    reg_panel = pd.merge(reg_panel, sum_mcap, how="left", on="Date")

    # calculate the market capitalization share
    reg_panel["mcap_share"] = reg_panel["mcap"] / reg_panel["sum_mcap"]

    # drop the column "sum_mcap"
    reg_panel = reg_panel.drop(columns=["sum_mcap"])

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
    x = 1 / max(0.0001, price) if price < 1 else price
    return 2 / x**5 - 1


def depegging_degree(price: float) -> float:
    """
    Function to calculate the depegging degree.
    """
    if price < 0:
        raise ValueError("Price cannot be negative.")
    return np.log(1 / max(0.0001, price) if price < 1 else price)


def _merge_pegging(reg_panel: pd.DataFrame) -> pd.DataFrame:
    """
    Function to merge the pegging degree.
    """

    reg_panel["pegging_degree"] = reg_panel["Stable"] * (
        reg_panel["dollar_exchange_rate"]
    ).apply(pegging_degree)

    reg_panel["depegging_degree"] = reg_panel["Stable"] * (
        reg_panel["dollar_exchange_rate"]
    ).apply(depegging_degree)

    reg_panel["pegging_degree_uppeg"] = reg_panel["pegging_degree"] * (
        reg_panel["dollar_exchange_rate"] > 1
    )
    reg_panel["pegging_degree_downpeg"] = reg_panel["pegging_degree"] * (
        reg_panel["dollar_exchange_rate"] < 1
    )

    reg_panel["depegging_degree_uppeg"] = reg_panel["depegging_degree"] * (
        reg_panel["dollar_exchange_rate"] > 1
    )
    reg_panel["depegging_degree_downpeg"] = reg_panel["depegging_degree"] * (
        reg_panel["dollar_exchange_rate"] < 1
    )
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

    # merge the market capitalization share
    reg_panel = _merge_mcap_share(reg_panel)

    # merge the dollar exchange rate
    reg_panel = _dollar_exchange_rate(reg_panel)

    # merge the stablecoin deviation
    # reg_panel = _merge_stable_deviation(reg_panel)

    # merge the pegging degree
    reg_panel = _merge_pegging(reg_panel)

    return reg_panel.loc[
        (reg_panel["Date"] >= "2020-06-01") & (reg_panel["Date"] < "2023-02-01")
    ]


if __name__ == "__main__":
    # plot pegging degree when price is 0.1 to 10
    from typing import Callable
    from matplotlib import pyplot as plt

    x = np.linspace(0.1, 10, 100)

    def plot_peg(func: Callable, label: str):
        y = [func(i) for i in x]
        plt.plot(x, y)
        # plot a vertical line at 1
        plt.axvline(x=1, color="r")
        # add horizontal line at 0
        plt.axhline(y=0, color="k")
        # label the axes
        plt.xlabel("Price")
        plt.ylabel(label)
        plt.show()
        plt.close()

    plot_peg(pegging_degree, "Pegging Degree")
    plot_peg(depegging_degree, "Depegging Degree")
