"""
Plot (auto)correlation and (auto)covariance matrices
"""


import pandas as pd

from environ.constants import TABLE_PATH
from environ.tabulate.render_corr import render_corr_cov_figure, render_corr_cov_tab

regression_panel = pd.read_pickle(TABLE_PATH / "reg_panel.pkl")

# columns to be included in the correlation table
corr_columns = [
    "Volume_share",
    "TVL_share",
    "avg_eigenvector_centrality",
    "betweenness_centrality_count",
    "betweenness_centrality_volume",
    "stableshare",
    "mcap_share",
    "Supply_share",
    "std",
    "corr_gas",
    "corr_eth",
    "gas_price_usd",
    "gas_price_usd_log_return_vol_1_30",
]


# render the correlation table
corr_cov_table = render_corr_cov_tab(
    data=regression_panel,
    sum_column=corr_columns,
    fig_type="corr",
)

# render the correlation table figure
render_corr_cov_figure(
    corr_cov_tab=corr_cov_table,
    file_name="correlation_matrix",
)
