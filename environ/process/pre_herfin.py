"""
Functions to prepare the herfin date series.
"""

import pandas as pd

from environ.constants import HERFIN_VAR_INFO, SAMPLE_PERIOD


def construct_herfin(
    main_panel: pd.DataFrame,
    herfin_col: list[str],
) -> pd.DataFrame:
    """
    Function to construct the herfin date series.
    """

    main_panel.set_index(["Date", "Token"], inplace=True)
    herfin_panel = main_panel[herfin_col].copy()
    herfin_panel = herfin_panel.groupby("Date").apply(lambda x: (x**2).sum())
    herfin_panel.rename(
        columns=HERFIN_VAR_INFO,
        inplace=True,
    )
    herfin_panel.sort_index(inplace=True)
    herfin_panel.index = pd.to_datetime(herfin_panel.index, format="%Y%m%d")

    return herfin_panel.loc[SAMPLE_PERIOD[0] : SAMPLE_PERIOD[1]]


if __name__ == "__main__":
    df_herfin = pd.read_csv("test/panel_main.csv")

    print(
        construct_herfin(
            main_panel=df_herfin,
            herfin_col=list(HERFIN_VAR_INFO.keys()),
        )
    )
