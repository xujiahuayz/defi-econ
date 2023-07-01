"""
Functions to help with asset pricing
"""

import warnings
from pathlib import Path

import pandas as pd
import scipy.stats as stats

from environ.constants import (
    DEPENDENT_VARIABLES,
    FIGURE_PATH,
    PROCESSED_DATA_PATH,
    STABLE_DICT,
)
from environ.utils.variable_constructer import lag_variable_columns

warnings.filterwarnings("ignore")

FONT_SIZE = 25


def _freq_col(
    df_panel: pd.DataFrame,
    freq: int,
    date_col: str = "Date",
) -> pd.DataFrame:
    """
    Function to reconstruct the frequency columns of a series
    """

    # convert the date to datetime
    df_panel["timestamp"] = df_panel[date_col].apply(lambda x: int(x.timestamp()))

    # create a freq column
    df_panel["freq"] = (
        (df_panel["timestamp"] - df_panel["timestamp"].min()) % (freq * 24 * 60 * 60)
    ) == 0

    return df_panel


def _freq_conversion(
    df_panel: pd.DataFrame,
) -> pd.DataFrame:
    """
    Function to convert the frequency of a series from daily to a given frequency
    """

    # keep the row with freq == True
    df_panel = df_panel[df_panel["freq"]]

    # check if the frequency is year or month
    df_panel.sort_values(by=["Token", "Date"], ascending=True, inplace=True)

    # calculate the return under the new frequency
    df_panel["ret"] = df_panel.groupby("Token")["dollar_exchange_rate"].pct_change()

    return df_panel


def _ret_winsorizing(
    df_panel: pd.DataFrame,
    threshold: float = 0.01,
    ret_col: str = "ret",
) -> pd.DataFrame:
    """
    Function to winsorize the DataFrame
    """

    # winsorize the return
    df_panel.loc[
        df_panel[ret_col] <= df_panel[ret_col].quantile(threshold), ret_col + "w"
    ] = df_panel[ret_col].quantile(threshold)
    df_panel.loc[
        df_panel[ret_col] >= df_panel[ret_col].quantile(1 - threshold), ret_col + "w"
    ] = df_panel[ret_col].quantile(1 - threshold)

    return df_panel


def _asset_pricing_preprocess(
    df_panel: pd.DataFrame,
    dominance_var: str,
    freq: int,
) -> pd.DataFrame:
    """
    Function to preprocess the dataframe
    """

    # reconstruct the frequency columns
    df_panel = _freq_col(df_panel, freq)

    # convert the frequency
    df_panel = _freq_conversion(df_panel)

    # winsorize the return
    df_panel = _ret_winsorizing(df_panel)

    # lag 1 unit for the dominance var and yield var to avoid information leakage
    df_panel = lag_variable_columns(
        data=df_panel,
        variable=[dominance_var],
        time_variable="Date",
        entity_variable="Token",
    )

    return df_panel


def _sorting(
    df_panel: pd.DataFrame,
    risk_factor: str,
    n_port: int = 3,
) -> pd.DataFrame:
    """
    Function to sort the tokens based on the dominance
    """

    # a list to store the top portfolio and bottom portfolio
    df_portfolio = []

    # sort the dataframe based on the Date
    df_panel = df_panel.sort_values(by=["Date"], ascending=True)

    # a list to store the date
    date_list = list(df_panel["Date"].unique())

    # remove the first date
    date_list.remove(df_panel["Date"].min())

    for period in date_list:
        # filter the dataframe
        df_panel_period = df_panel[df_panel["Date"] == period].copy()

        # sort the dataframe based on the risk factor
        df_panel_period = df_panel_period.sort_values(by=risk_factor, ascending=True)

        # rows per partition
        n_threasold = len(df_panel_period) // n_port

        for port in range(n_port - 1):
            # isolate the portfolio
            df_portfolio_period = df_panel_period.iloc[
                port * n_threasold : (port + 1) * n_threasold
            ].copy()

            # add the portfolio column
            df_portfolio_period["portfolio"] = f"P{port + 1}"

            # append the dataframe
            df_portfolio.append(df_portfolio_period)

        # isolate the portfolio
        df_portfolio_period = df_panel_period.iloc[(n_port - 1) * n_threasold :].copy()

        # add the portfolio column
        df_portfolio_period["portfolio"] = f"P{n_port}"

        # append the dataframe
        df_portfolio.append(df_portfolio_period)

    # concatenate the dataframe
    df_sample = pd.concat(df_portfolio)

    return df_sample


def _eval_port(
    df_panel: pd.DataFrame,
    freq: int,
    save_path: Path | str,
) -> None:
    """
    Function to evaluate the portfolio
    """

    # sort the dataframe by the frequency and portfolio
    df_panel.sort_values(by=["Date", "portfolio"], ascending=True, inplace=True)

    # check how many portfolio
    n_port = len(df_panel["portfolio"].unique())

    # dict to store the freq and portfolio return
    ret_dict = {f"P{port}": [] for port in range(1, n_port + 1)}
    ret_dict["freq"] = []

    # iterate through the frequency
    for period in df_panel["Date"].unique():
        # filter the dataframe
        df_panel_period = df_panel[df_panel["Date"] == period].copy()

        # calculate the equal weight portfolio for top and bottom
        ret_dict["freq"].append(period)

        for portfolio in [f"P{port}" for port in range(1, n_port + 1)]:
            # isolate the top and bottom portfolio
            df_portfolio = df_panel_period[
                df_panel_period["portfolio"] == portfolio
            ].copy()

            # calculate the market cap weight
            df_portfolio["weight"] = df_portfolio["mcap"] / df_portfolio["mcap"].sum()

            # calculate the return
            ret_dict[portfolio].append(
                (df_portfolio["weight"] * df_portfolio["ret"]).sum()
            )

    # convert the dict to dataframe
    df_ret = pd.DataFrame(ret_dict)

    # sort the dataframe by the frequency
    df_ret.sort_values(by="freq", ascending=True, inplace=True)

    # convert the freq to string
    df_ret["freq"] = pd.to_datetime(df_ret["freq"])

    # calculate the bottom minus top
    df_ret[f"P{n_port} - P1"] = df_ret[f"P{n_port}"] - df_ret["P1"]

    # a new dataframe to store the averag return for each portfolio
    df_ret_avg = pd.DataFrame(
        {
            "portfolio": [f"P{port}" for port in range(1, n_port + 1)]
            + [f"P{n_port} - P1"],
            "avg_return": df_ret[[f"P{port}" for port in range(1, n_port + 1)]]
            .mean()
            .to_list()
            + [df_ret[f"P{n_port} - P1"].mean()],
            "t-stat": df_ret[[f"P{port}" for port in range(1, n_port + 1)]]
            .apply(lambda x: stats.ttest_1samp(x, 0)[0])
            .to_list()
            + [stats.ttest_1samp(df_ret[f"P{n_port} - P1"], 0)[0]],
        }
    )

    # annualize the return
    df_ret_avg["avg_return"] = (1 + df_ret_avg["avg_return"]) ** (365 / freq) - 1

    print(df_ret_avg)


def asset_pricing(
    reg_panel: pd.DataFrame,
    save_path: Path | str,
    dom_var: str = "volume_ultimate_share",
    n_port: int = 3,
    freq: int = 14,
) -> None:
    """
    Aggregate function to create portfolios
    """

    # preprocess the dataframe
    df_panel = _asset_pricing_preprocess(reg_panel, dom_var, freq)

    # sort the tokens based on the dominance
    df_sample = _sorting(
        df_panel=df_panel,
        risk_factor=dom_var,
        n_port=3,
    )

    # evaluate the performance of the portfolio
    _eval_port(df_sample, freq, save_path)


if __name__ == "__main__":
    # load the regression panel dataset
    reg_panel = pd.read_pickle(
        PROCESSED_DATA_PATH / "panel_main.pickle.zip", compression="zip"
    )
    # stable non-stable info dict
    stable_nonstable_info = {
        "stablecoin": reg_panel[reg_panel["Token"].isin(STABLE_DICT.keys())],
        "nonstablecoin": reg_panel[~reg_panel["Token"].isin(STABLE_DICT.keys())],
    }

    # iterate through the dominance
    for panel_info, df_panel in stable_nonstable_info.items():
        for dominance in DEPENDENT_VARIABLES:
            for frequency in [14, 30]:
                print(f"Processing {panel_info} {dominance} {frequency}")
                asset_pricing(
                    df_panel,
                    FIGURE_PATH / f"{panel_info}_{dominance}_{frequency}.pdf",
                    dominance,
                    3,
                    frequency,
                )
