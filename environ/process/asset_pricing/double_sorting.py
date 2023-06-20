"""
Functions to help with asset pricing
"""

import warnings

import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

from environ.constants import (
    DEPENDENT_VARIABLES,
    FIGURE_PATH,
    PROCESSED_DATA_PATH,
    STABLE_DICT,
)
from environ.plot.plot_ma import plot_boom_bust
from environ.process.market.boom_bust import BOOM_BUST
from environ.utils.variable_constructer import lag_variable_columns

warnings.filterwarnings("ignore")


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
    yield_var: str = "supply_rates",
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
        variable=[dominance_var, yield_var],
        time_variable="Date",
        entity_variable="Token",
    )

    return df_panel


def _double_sorting(
    df_panel: pd.DataFrame,
    first_indicator: str,
    second_indicator: str,
    threshold: float = 0.1,
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

        # calculate the threshold
        n_threasold = int(df_panel_period.shape[0] * threshold)

        # sort the dataframe based on the first and second indicator
        df_panel_period = df_panel_period.sort_values(
            by=[first_indicator, second_indicator], ascending=False
        )

        # create the top portfolio
        df_top_portfolio = df_panel_period.head(n_threasold).copy()
        df_top_portfolio["portfolio"] = "top"

        # create the bottom portfolio
        df_bottom_portfolio = df_panel_period.tail(n_threasold).copy()
        df_bottom_portfolio["portfolio"] = "bottom"

        # append the portfolio
        df_portfolio.append(df_top_portfolio)
        df_portfolio.append(df_bottom_portfolio)

    # concatenate the dataframe
    df_sample = pd.concat(df_portfolio)

    return df_sample


def _eval_port(
    df_panel: pd.DataFrame,
    save_path: Path | str,
) -> None:
    """
    Function to evaluate the portfolio
    """

    # sort the dataframe by the frequency and portfolio
    df_panel.sort_values(by=["Date", "portfolio"], ascending=True, inplace=True)

    # dict to store the portfolio return
    ret_dict = {
        "freq": [],
        "top": [],
        "bottom": [],
    }

    # iterate through the frequency
    for period in df_panel["Date"].unique():
        # filter the dataframe
        df_panel_period = df_panel[df_panel["Date"] == period].copy()

        # calculate the equal weight portfolio for top and bottom
        ret_dict["freq"].append(period)

        for portfolio in ["top", "bottom"]:
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
    df_ret["top_minus_bottom"] = df_ret["top"] - df_ret["bottom"]

    plot_lst = ["top", "bottom", "top_minus_bottom"]

    # calculate the cumulative return
    for col_ret in plot_lst:
        df_ret[col_ret + "_cum"] = (df_ret[col_ret] + 1).cumprod()

    # three subplots for cum ret sharing x axis
    (
        _,
        ax_ret,
    ) = plt.subplots(figsize=(12, 7))

    for col in plot_lst:
        ax_ret.plot(df_ret["freq"], df_ret[col + "_cum"], label=col)

    # plot boom bust cycles
    plot_boom_bust(ax_ret, boom_bust=BOOM_BUST)
    ax_ret.set_xlim(df_panel["Date"].min(), df_panel["Date"].max())

    # legend
    ax_ret.legend()

    # tight layout
    plt.tight_layout()

    # save the plot to the save path
    plt.savefig(save_path, dpi=300)

    plt.show()

    # close the plot
    plt.close()


def asset_pricing(
    reg_panel: pd.DataFrame,
    save_path: Path | str,
    dom_var: str = "volume_ultimate_share",
    yield_var: str = "supply_rates",
    threshold: float = 0.1,
    freq: int = 14,
) -> None:
    """
    Aggregate function to create portfolios
    """

    # preprocess the dataframe
    df_panel = _asset_pricing_preprocess(reg_panel, dom_var, freq, yield_var)

    # sort the tokens based on the dominance
    df_sample = _double_sorting(
        df_panel=df_panel,
        first_indicator=dom_var,
        second_indicator=yield_var,
        threshold=threshold,
    )

    # evaluate the performance of the portfolio
    _eval_port(df_sample, save_path)


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
                asset_pricing(
                    df_panel,
                    FIGURE_PATH / f"{panel_info}_{dominance}_{frequency}.pdf",
                    dominance,
                    "supply_rates",
                    0.1,
                    frequency,
                )
