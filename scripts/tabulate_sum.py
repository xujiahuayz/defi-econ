"""
Tabulate the summary statistics of the data.
"""

from pathlib import Path

import pandas as pd

from environ.constants import TABLE_PATH
from environ.tabulate.render_summary import render_summary_table_latex

if __name__ == "__main__":
    # get the regressuib panel dataset from pickle file
    regression_panel = pd.read_pickle(Path(TABLE_PATH) / "reg_panel.pkl")

    # Specify the columns to be included in the summary table
    sum_column = [
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

    # generate the summary table
    render_summary_table_latex(
        file_name="test",
        data=regression_panel,
        sum_column=sum_column,
        all_columns=False,
    )
