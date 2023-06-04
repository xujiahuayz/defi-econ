"""
Functions to help with asset pricing
"""

from typing import Literal, Optional

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from environ.constants import PROCESSED_DATA_PATH, STABLE_DICT
from environ.utils.variable_constructer import lag_variable_columns

YIELD_VAR_DICT = {
    "stablecoin": "supply_rates",
    "nonstablecoin": "dollar_exchange_rate",
}


def _freq_column(
    df_panel: pd.DataFrame,
) -> pd.DataFrame:
    """
    Function to reconstruct the frequency columns of a series
    """

    # convert the date to datetime
    df_panel["Date"] = pd.to_datetime(df_panel["Date"])

    # create a year column
    df_panel["year"] = df_panel["Date"].dt.year

    # create a year-month column
    df_panel["month"] = df_panel["Date"].dt.year * 100 + df_panel["Date"].dt.month

    return df_panel


def _freq_conversion(
    df_panel: pd.DataFrame,
    freq: Literal["year", "month"],
) -> pd.DataFrame:
    """
    Function to convert the frequency of a series from daily to monthly or yearly
    """

    # check if the frequency is year or month
    df_panel.sort_values(by=["Token", freq], ascending=True, inplace=True)

    # keep the last observation
    df_panel.drop_duplicates(subset=["Token", freq], keep="last", inplace=True)

    # calculate the return under the new frequency
    df_panel["ret"] = df_panel.groupby("Token")["dollar_exchange_rate"].pct_change()

    return df_panel


def _asset_pricing_preprocess(
    df_panel: pd.DataFrame,
    dominance_var: str,
    yield_var: Optional[dict[str, str]],
    freq: Literal["year", "month"],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Function to preprocess the dataframe
    """

    # reconstruct the frequency columns
    df_panel = _freq_column(df_panel)

    # convert the frequency
    df_panel = _freq_conversion(df_panel, freq)

    # lag 1 unit for the dominance var and yield var to avoid information leakage
    df_panel = lag_variable_columns(
        data=df_panel,
        variable=[dominance_var] + list(yield_var.values()),
        time_variable="Date",
        entity_variable="Token",
    )

    # plot the return of ethereum

    # split the series into stablecoin and nonstablecoin
    df_panel_stablecoin = df_panel[df_panel["Token"].isin(STABLE_DICT.keys())]
    df_panel_nonstablecoin = df_panel[~df_panel["Token"].isin(STABLE_DICT.keys())]

    return df_panel_stablecoin, df_panel_nonstablecoin


def _double_sorting(
    df_panel: pd.DataFrame,
    first_indicator: str,
    second_indicator: str,
    freq: Literal["year", "month"],
    threshold: float = 0.1,
) -> pd.DataFrame:
    """
    Function to sort the tokens based on the dominance
    """

    # a list to store the top portfolio and bottom portfolio
    df_portfolio = []

    for period in df_panel[freq].unique():
        # filter the dataframe
        df_panel_period = df_panel[df_panel[freq] == period].copy()

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
    freq: Literal["year", "month"],
    weight: Literal["equal", "mcap"],
) -> None:
    """
    Function to evaluate the portfolio
    """

    match weight:
        case "equal":
            # calculate the equal weight portfolio for top and bottom
            df_panel["retw"] = (
                df_panel.groupby(
                    [
                        freq,
                        "portfolio",
                    ]
                )["ret"]
                .transform(lambda x: x.mean())
                .copy()
            )
        case "mcap":
            # calculate the market cap weight portfolio for top and bottom
            df_panel["retw"] = (
                df_panel.groupby(
                    [
                        freq,
                        "portfolio",
                    ]
                )["ret"]
                .transform(
                    lambda x: (x * df_panel["mcap"]).sum() / df_panel["mcap"].sum()
                )
                .copy()
            )

    # drop the duplicates
    df_panel.drop_duplicates(subset=[freq, "portfolio"], inplace=True, keep="last")

    # print the dataframe
    print(df_panel)

    # plot the weighted return separately
    _, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(
        data=df_panel,
        x=freq,
        y="retw",
        hue="portfolio",
        ax=ax,
    )

    # show the plot
    plt.show()


def asset_pricing() -> None:
    """
    Aggregate function to create portfolios
    """

    # load the regression panel dataset
    reg_panel = pd.read_pickle(
        PROCESSED_DATA_PATH / "panel_main.pickle.zip", compression="zip"
    )

    # print(reg_panel.keys())
    df_panel_stablecoin, df_panel_nonstablecoin = _asset_pricing_preprocess(
        reg_panel, "volume_ultimate_share", YIELD_VAR_DICT, "year"
    )

    # sort the tokens based on the dominance
    df_sample = pd.concat(
        [
            _double_sorting(
                df_panel=df_panel_stablecoin,
                first_indicator="volume_ultimate_share",
                second_indicator="supply_rates",
                freq="year",
                threshold=0.1,
            ),
            _double_sorting(
                df_panel=df_panel_nonstablecoin,
                first_indicator="volume_ultimate_share",
                second_indicator="dollar_exchange_rate",
                freq="year",
                threshold=0.1,
            ),
        ]
    )

    # evaluate the portfolio
    _eval_port(df_sample, freq="year", weight="equal")


if __name__ == "__main__":
    asset_pricing()
