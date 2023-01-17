# -*- coding: utf-8 -*-
"""
Scripts to execute statistical tests
"""

from os import path
import pandas as pd
import numpy as np
from chow_test import chow_test
from defi_econ.constants import BETWEENNESS_DATA_PATH


def stat_chow_test(
    y: pd.Series, breakpoint_index: str, significance=0.05
) -> tuple[float, float]:
    """
    Execute Chow Test for the structural break / regime switch on the given date.
    """

    x_series_num_seq = pd.Series(
        np.arange(len(y))
    )  # generate X series by serial integer index

    # Chow test
    # Note: last index for the linear model 1, first index for the linear model 2, then compare coefficients
    chow_test_result = chow_test(
        y_series=y,
        X_series=x_series_num_seq,
        last_index=len(y[:breakpoint_index]) - 1,
        first_index=len(y[:breakpoint_index]),
        significance=significance,
    )

    return chow_test_result


if __name__ == "__main__":
    # Example
    data_v2v3 = pd.read_csv(
        path.join(BETWEENNESS_DATA_PATH, "betweenness_centrality_merge.csv")
    )
    usdc_value_v2v3 = data_v2v3.loc[data_v2v3["node"] == "USDC"].set_index(["date"])

    # input the date (index) of the test point
    # Note: you may need to adapt "breakpoint_index" variable to fit the index and date format in your pd.Series data
    stat_chow_test(
        y=usdc_value_v2v3["betweenness_centrality_volume"], breakpoint_index="2022/5/10"
    )
