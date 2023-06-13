"""
Functions to help with asset pricing
"""

import warnings

from typing import Literal
import matplotlib.pyplot as plt
import pandas as pd

from environ.constants import PROCESSED_DATA_PATH, STABLE_DICT
from environ.process.market.boom_bust import BOOM_BUST
from environ.utils.variable_constructer import lag_variable_columns
from environ.plot.plot_ma import plot_boom_bust

YIELD_VAR_DICT = {
    "stablecoin": "supply_rates",
    "nonstablecoin": "dollar_exchange_rate_log_return_1",
}

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
    yield_var: None | dict[str, str],
    freq: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
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
        variable=[dominance_var] + list(yield_var.values()),
        time_variable="Date",
        entity_variable="Token",
    )

    # split the series into stablecoin and nonstablecoin
    df_panel["is_stable"] = df_panel["Token"].isin(STABLE_DICT.keys())

    return df_panel[df_panel["is_stable"]], df_panel[~df_panel["is_stable"]]


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
    weight: Literal["equal", "mcap"],
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
        "True_top": [],
        "True_bottom": [],
        "False_top": [],
        "False_bottom": [],
    }

    # iterate through the frequency
    for period in df_panel["Date"].unique():
        # filter the dataframe
        df_panel_period = df_panel[df_panel["Date"] == period].copy()

        # calculate the equal weight portfolio for top and bottom
        ret_dict["freq"].append(period)

        match weight:
            case "equal":
                for portfolio in ["top", "bottom"]:
                    ret_dict[portfolio].append(
                        df_panel_period[df_panel_period["portfolio"] == portfolio][
                            "ret"
                        ].mean()
                    )
                    for is_stable in [True, False]:
                        ret_dict[f"{is_stable}_{portfolio}"].append(
                            df_panel_period[
                                (df_panel_period["portfolio"] == portfolio)
                                & (df_panel_period["is_stable"] == is_stable)
                            ]["ret"].mean()
                        )

            case "mcap":
                for portfolio in ["top", "bottom"]:
                    # isolate the top and bottom portfolio
                    df_portfolio = df_panel_period[
                        df_panel_period["portfolio"] == portfolio
                    ].copy()

                    # calculate the market cap weight
                    df_portfolio["weight"] = (
                        df_portfolio["mcap"] / df_portfolio["mcap"].sum()
                    )

                    # calculate the return
                    ret_dict[portfolio].append(
                        (df_portfolio["weight"] * df_portfolio["ret"]).sum()
                    )
                    for is_stable in [True, False]:
                        df_portfolio_stable = df_portfolio[
                            df_portfolio["is_stable"] == is_stable
                        ].copy()

                        # recalculate the weight
                        df_portfolio_stable["weight"] = (
                            df_portfolio_stable["mcap"]
                            / df_portfolio_stable["mcap"].sum()
                        )

                        # calculate the return
                        ret_dict[f"{is_stable}_{portfolio}"].append(
                            (
                                df_portfolio_stable["weight"]
                                * df_portfolio_stable["ret"]
                            ).sum()
                        )

    # convert the dict to dataframe
    df_ret = pd.DataFrame(ret_dict)

    # sort the dataframe by the frequency
    df_ret.sort_values(by="freq", ascending=True, inplace=True)

    # convert the freq to string
    df_ret["freq"] = pd.to_datetime(df_ret["freq"])

    # calculate the bottom minus top
    df_ret["bottom_minus_top"] = df_ret["bottom"] - df_ret["top"]

    plot_dict = {
        "regular": [
            "top",
            "bottom",
            "bottom_minus_top",
        ],
        "stable": [
            "True_top",
            "True_bottom",
        ],
        "nonstable": [
            "False_top",
            "False_bottom",
        ],
    }

    # calculate the cumulative return
    for _, lst in plot_dict.items():
        for col_ret in lst:
            df_ret[col_ret + "_cum"] = (df_ret[col_ret] + 1).cumprod()

    # three subplots for cum ret sharing x axis
    _, (ax_ret, ax_ret_stable, ax_ret_nonstable) = plt.subplots(
        nrows=3, ncols=1, sharex=True, figsize=(12, 7)
    )

    for col in plot_dict["regular"]:
        ax_ret.plot(df_ret["freq"], df_ret[col + "_cum"], label=col)

    for col in plot_dict["stable"]:
        ax_ret_stable.plot(df_ret["freq"], df_ret[col + "_cum"], label=col)

    for col in plot_dict["nonstable"]:
        ax_ret_nonstable.plot(df_ret["freq"], df_ret[col + "_cum"], label=col)

    for plt_subplot in [ax_ret, ax_ret_stable, ax_ret_nonstable]:
        # plot boom bust cycles
        plot_boom_bust(plt_subplot, boom_bust=BOOM_BUST)
        plt_subplot.set_xlim(df_panel["Date"].min(), df_panel["Date"].max())

    # legend
    ax_ret.legend()
    ax_ret_stable.legend()
    ax_ret_nonstable.legend()

    # tight layout
    plt.tight_layout()

    # show the plot
    plt.show()


def asset_pricing(
    dom: str = "volume_ultimate_share",
    freq: int = 14,
    weight: Literal["mcap", "equal"] = "mcap",
) -> None:
    """
    Aggregate function to create portfolios
    """

    # load the regression panel dataset
    reg_panel = pd.read_pickle(
        PROCESSED_DATA_PATH / "panel_main.pickle.zip", compression="zip"
    )

    df_panel_stablecoin, df_panel_nonstablecoin = _asset_pricing_preprocess(
        reg_panel, dom, YIELD_VAR_DICT, freq
    )

    # sort the tokens based on the dominance
    df_sample = pd.concat(
        [
            _double_sorting(
                df_panel=df_panel_stablecoin,
                first_indicator=dom,
                second_indicator=YIELD_VAR_DICT["stablecoin"],
                threshold=0.1,
            ),
            _double_sorting(
                df_panel=df_panel_nonstablecoin,
                first_indicator=dom,
                second_indicator=YIELD_VAR_DICT["nonstablecoin"],
                threshold=0.1,
            ),
        ]
    )

    # evaluate the portfolio
    _eval_port(df_sample, weight=weight)


if __name__ == "__main__":
    asset_pricing("volume_ultimate_share", 14, "mcap")
