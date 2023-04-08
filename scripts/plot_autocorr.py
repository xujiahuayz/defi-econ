"""
Plot (auto)correlation and (auto)covariance matrices
"""


import numpy as np
import pandas as pd

from environ.constants import DATA_PATH, DEPENDENT_VARIABLES
from environ.tabulate.render_corr import render_corr_cov_figure, render_corr_cov_tab
from environ.utils.variable_constructer import lag_variable_columns


reg_panel = pd.read_pickle(DATA_PATH / "processed" / "reg_panel_merged.pkl")


# columns to be included in the correlation table
corr_columns = DEPENDENT_VARIABLES + [
    "mcap_share",
    "TVL_share",
    "Supply_share",
    "stableshare",
    "std",
    "corr_gas",
    "corr_eth",
    # "gas_price_usd",
    # "gas_price_usd_log_return_vol_1_30",
]

reg_panel[corr_columns] = reg_panel[corr_columns].fillna(0)
LAG = 28
for subsample in ["bust", "boom"]:
    reg_panel_sub = reg_panel[corr_columns + ["Date", "Token", "is_boom"]]
    # change all corr_columns value from corr_columns to np.na for is_boom != True
    reg_panel_sub.loc[
        reg_panel_sub["is_boom"] == (subsample == "bust"), corr_columns
    ] = np.nan
    reg_panel_sub = lag_variable_columns(
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
