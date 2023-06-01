"""
Functions to help with asset pricing
"""

import pandas as pd
import matplotlib.pyplot as plt
from environ.constants import PROCESSED_DATA_PATH, STABLE_DICT
from environ.utils.variable_constructer import lag_variable_columns, name_lag_variable
from typing import Optional


def freq_column(
    df_series: pd.DataFrame,
) -> pd.DataFrame:
    """
    Function to get the frequency columns of a series
    """

    # convert the date to datetime
    df_series["Date"] = pd.to_datetime(df_series["Date"])

    # create a year column
    df_series["year"] = df_series["Date"].dt.year

    # create a year-month column
    df_series["year_month"] = (
        df_series["Date"].dt.year * 100 + df_series["Date"].dt.month
    )

    return df_series


def freq_conversion(
    df_series: pd.DataFrame,
    freq: str = "year",
) -> pd.DataFrame:
    """
    Function to convert the frequency of a series
    """

    # keep the last observation
    return df_series.sort_values(by=["Token", freq], ascending=True).drop_duplicates(
        subset=["Token", freq], keep="last"
    )


def sorting(
    df_series: pd.DataFrame,
    dominance_var: str,
    yield_var: dict[str, str] = {
        "stablecoin": "supply_rates",
        "nonstablecoin": "dollar_exchange_rate",
    },
    threshold: float = 0.1,
    freq: str = "year",
) -> pd.DataFrame:
    """
    Function to sort the series
    """

    def _sorting_util(
        df_series: pd.DataFrame,
        sorting_var: str,
    ) -> pd.DataFrame:
        """
        Function to sort the series
        """

        # rank the series
        df_series[f"{sorting_var}_rank"] = df_series.groupby(freq)[sorting_var].rank(
            pct=True
        )

        # create a high column
        df_series[f"{sorting_var}_high"] = (
            df_series[f"{sorting_var}_rank"] >= 1 - threshold
        )

        # create a low column
        df_series[f"{sorting_var}_low"] = df_series[f"{sorting_var}_rank"] <= threshold

        return df_series

    # lag the dominance var and yield var
    df_series = lag_variable_columns(
        data=df_series,
        variable=[dominance_var] + list(yield_var.values()),
        time_variable="Date",
        entity_variable="Token",
    )

    # split the series into stablecoin and nonstablecoin
    df_series_stablecoin = df_series[df_series["Token"].isin(STABLE_DICT.keys())]
    df_series_nonstablecoin = df_series[~df_series["Token"].isin(STABLE_DICT.keys())]

    # for stablecoin sort by supply rates and dominance
    df_series_stablecoin = _sorting_util(
        df_series=df_series_stablecoin,
        sorting_var=name_lag_variable(dominance_var),
    )
    df_series_stablecoin = _sorting_util(
        df_series=df_series_stablecoin,
        sorting_var=name_lag_variable(yield_var["stablecoin"]),
    )

    # for nonstablecoin sort by dollar exchange rate and dominance
    df_series_nonstablecoin = _sorting_util(
        df_series=df_series_nonstablecoin,
        sorting_var=name_lag_variable(dominance_var),
    )
    df_series_nonstablecoin = _sorting_util(
        df_series=df_series_nonstablecoin,
        sorting_var=name_lag_variable(yield_var["nonstablecoin"]),
    )

    # calculate the number of sample we need
    sample_num_dict = {
        "stablecoin": df_series_stablecoin.shape[0] * threshold,
        "nonstablecoin": df_series_nonstablecoin.shape[0] * threshold,
    }

    # for stablecoin group by frequency, and

    return df_series


if __name__ == "__main__":
    # load the regression panel dataset
    reg_panel = pd.read_pickle(
        PROCESSED_DATA_PATH / "panel_main.pickle.zip", compression="zip"
    )

    print(reg_panel.keys())
