"""
Plot (auto)correlation and (auto)covariance matrices
"""

from pathlib import Path

import pandas as pd

from environ.constants import TABLE_PATH
from environ.tabulate.render_corr import render_corr_cov_figure, render_corr_cov_tab
from environ.utils.variable_constructer import lag_variable

if __name__ == "__main__":
    # get the regressuib panel dataset from pickle file
    regression_panel = pd.read_pickle(Path(TABLE_PATH) / "reg_panel.pkl")

    # columns to be included in the correlation table
    corr_columns = [
        "Volume_share",
        "avg_eigenvector_centrality",
        "TVL_share",
        "betweenness_centrality_count",
        "betweenness_centrality_volume",
        "stableshare",
    ]

    # set the lag number
    LAG_NUM = 28

    # figure type
    FIGURE_TYPE = "corr"

    # file name
    FILE_NAME = "test"

    # lag the variables
    regression_panel = lag_variable(
        data=regression_panel,
        variable=corr_columns,
        lag=LAG_NUM,
        time_variable="Date",
        entity_variable="Token",
    )

    # render the correlation table
    corr_cov_table = render_corr_cov_tab(
        data=regression_panel,
        sum_column=corr_columns,
        lag=LAG_NUM,
        fig_type=FIGURE_TYPE,
    )

    # render the correlation table figure
    render_corr_cov_figure(
        corr_cov_tab=corr_cov_table,
        file_name=FILE_NAME,
        lag=LAG_NUM,
        fig_type=FIGURE_TYPE,
    )
