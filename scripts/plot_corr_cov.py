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

    corr_columns = [
        "Volume_share",
        "volume_in_share",
        "volume_out_share",
        "borrow_rate",
        "supply_rates",
        "TVL_share",
        "Inflow_centrality",
        "Outflow_centrality",
        "betweenness_centrality_count",
        "betweenness_centrality_volume",
        "log_return",
        "corr_gas",
        "corr_eth",
        "corr_sp",
        "std",
        "gas_price_usd",
        "Nonstable",
        "IsWETH",
        # "exceedance",
        # "Gas_fee_volatility",
        "beta",
        "corr_sentiment",
        "average_return",
        # "mcap_share",
        "dollar_exchange_rate",
    ]

    # set the lag number
    LAG_NUM = 28

    # whether to plot the auto lagged correlation table or normal correlation table
    AUTO_LAG = False

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
    corr_table, cov_table = render_corr_cov_tab(
        data=regression_panel, sum_column=corr_columns, auto_lag=AUTO_LAG, lag=LAG_NUM
    )

    # render the correlation table figure
    render_corr_cov_figure(
        corr_tab=corr_table,
        cov_tab=cov_table,
        file_name=FILE_NAME,
        auto_lag=AUTO_LAG,
        lag=LAG_NUM,
    )
