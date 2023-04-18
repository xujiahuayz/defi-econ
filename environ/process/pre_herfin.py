"""
Functions to prepare the herfin date series.
"""

import pandas as pd

from environ.constants import HERFIN_VAR_INFO, SAMPLE_PERIOD
from environ.process.market.prepare_market_data import market_data
from environ.process.market.cluster_coef import avg_cluster_df
from environ.tabulate.panel.panel_generator import _merge_boom_bust
from environ.process.market.trading_volume import df_volume


def construct_herfin(
    main_panel: pd.DataFrame,
) -> pd.DataFrame:
    """
    Function to construct the herfin date series.
    """

    # calculate the herfin date series
    main_panel.set_index(["Date", "Token"], inplace=True)
    herfin_panel = main_panel[list(HERFIN_VAR_INFO.keys())].copy()
    herfin_panel = herfin_panel.groupby("Date").apply(lambda x: (x**2).sum())
    herfin_panel.rename(
        columns=HERFIN_VAR_INFO,
        inplace=True,
    )
    herfin_panel.sort_index(inplace=True)
    herfin_panel.index = pd.to_datetime(herfin_panel.index)
    herfin_panel = herfin_panel.reset_index().rename(columns={"index": "Date"})

    # merge boom bust cycles
    herfin_panel = _merge_boom_bust(herfin_panel)

    # merge other time series
    for market_df in [market_data, df_volume, avg_cluster_df]:
        herfin_panel = herfin_panel.merge(
            market_df,
            how="left",
            on=["Date"],
        )

    return herfin_panel.loc[
        (herfin_panel["Date"] >= SAMPLE_PERIOD[0])
        & (herfin_panel["Date"] <= SAMPLE_PERIOD[1])
    ]


if __name__ == "__main__":
    df_herfin = pd.read_csv("test/panel_main.csv")

    print(
        construct_herfin(
            main_panel=df_herfin,
        )
    )
