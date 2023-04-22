"""
Plot (auto)correlation and (auto)covariance matrices
"""


import numpy as np
import pandas as pd

from environ.constants import (
    DEPENDENT_VARIABLES,
    PROCESSED_DATA_PATH,
)
from environ.tabulate.render_corr import render_corr_cov_figure, render_corr_cov_tab
from environ.utils.variable_constructer import lag_variable_columns


reg_panel = pd.read_pickle(
    PROCESSED_DATA_PATH / "panel_main.pickle.zip", compression="zip"
)

# columns to be included in the correlation table
corr_columns = DEPENDENT_VARIABLES[:5]
# + [
#     "mcap_share",
#     "TVL_share",
#     "Supply_share",
#     "stableshare",
#     # "std",
#     # "corr_gas",
#     # "corr_eth",
#     # "gas_price_usd",
#     # "gas_price_usd_log_return_vol_1_30",
# ]

reg_panel[corr_columns] = reg_panel[corr_columns].fillna(0)
LAG = 28
for subsample in ["boom", "bust", "full"]:
    reg_panel_sub = reg_panel[corr_columns + ["Date", "Token", "is_boom"]]
    # change all corr_columns value from corr_columns to np.na for is_boom != True
    # switch case for subsample
    if subsample == "boom":
        reg_panel_sub.loc[reg_panel_sub["is_boom"] == False, corr_columns] = np.nan
    elif subsample == "bust":
        reg_panel_sub.loc[reg_panel_sub["is_boom"], corr_columns] = np.nan

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

    # transpose the table but keep the same index and columns as the original
    corr_cov_table_t = corr_cov_table.T
    corr_cov_table_t.index = corr_cov_table.index
    corr_cov_table_t.columns = corr_cov_table.columns
    corr_cov_table_diff = corr_cov_table - corr_cov_table_t

    # render the correlation table figure
    render_corr_cov_figure(
        corr_cov_tab=corr_cov_table,
        file_name=f"auto_corr_{subsample}",
    )

    render_corr_cov_figure(
        corr_cov_tab=corr_cov_table_diff,
        file_name=f"auto_corr_{subsample}_diff",
    )
