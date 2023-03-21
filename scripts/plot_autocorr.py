"""
Plot (auto)correlation and (auto)covariance matrices
"""


import numpy as np
import pandas as pd

from environ.constants import TABLE_PATH
from environ.tabulate.render_corr import render_corr_cov_figure, render_corr_cov_tab
from environ.utils.variable_constructer import lag_variable

regression_panel = pd.read_pickle(TABLE_PATH / "reg_panel.pkl")

# columns to be included in the correlation table
corr_columns = [
    "Volume_share",
    "TVL_share",
    "avg_eigenvector_centrality",
    "betweenness_centrality_count",
    "betweenness_centrality_volume",
    "stableshare",
]

regression_panel[corr_columns] = regression_panel[corr_columns].fillna(0)
LAG = 28
for subsample in ["bust", "boom"]:
    reg_panel_sub = regression_panel[corr_columns + ["Date", "Token", "is_boom"]]
    # change all corr_columns value from corr_columns to np.na for is_boom != True
    reg_panel_sub.loc[
        reg_panel_sub["is_boom"] == (subsample == "bust"), corr_columns
    ] = np.nan
    reg_panel_sub = lag_variable(
        data=reg_panel_sub,
        variable=corr_columns,
        time_variable="Date",
        entity_variable="Token",
        lag=LAG,
    )
    # remove all rows with where reg_panel_sub["is_boom"] == (subsample == "bust")
    reg_panel_sub = reg_panel_sub[reg_panel_sub["is_boom"] == (subsample == "boom")]

    # render the correlation table
    corr_cov_table = render_corr_cov_tab(
        data=reg_panel_sub,
        sum_column=corr_columns,
        fig_type="corr",
        lag=LAG,
    )

    # render the correlation table figure
    render_corr_cov_figure(
        corr_cov_tab=corr_cov_table,
        file_name=f"auto_corr_{subsample}",
    )
