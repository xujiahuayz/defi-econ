"""
Plot (auto)correlation and (auto)covariance matrices
"""


import pandas as pd

from environ.constants import DATA_PATH, DEPENDENT_VARIABLES
from environ.tabulate.render_corr import render_corr_cov_figure, render_corr_cov_tab

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


# render the correlation table
corr_cov_table = render_corr_cov_tab(
    data=reg_panel,
    sum_column=corr_columns,
    fig_type="corr",
)

# render the correlation table figure
render_corr_cov_figure(
    corr_cov_tab=corr_cov_table,
    file_name="correlation_matrix",
)
