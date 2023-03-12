# get the regression panel dataset from pickled file
from pathlib import Path

import pandas as pd

from environ.constants import TABLE_PATH
from environ.utils.lags import lag_variable
from environ.tabulate.render_regression import (
    construct_regress_vars,
    render_regress_table,
)

dependent_variables = [
    "avg_eigenvector_centrality",
    "betweenness_centrality_volume",
    "betweenness_centrality_count",
    "Volume_share",
]

iv_chunk_list_unlagged = [
    [["std", "corr_gas", "mcap_share", "Supply_share"]],
    [
        # ["Stable", "depegging_degree"],
        # ["pegging_degree"],
        # ["depeg_pers"],
        ["stableshare"],
    ],
    [["corr_eth"], ["corr_sp"]],
]

reg_combi = construct_regress_vars(
    dependent_variables=dependent_variables,
    iv_chunk_list=iv_chunk_list_unlagged,
    lag_iv=True,
    with_lag_dv=True,
    without_lag_dv=False,
)

# Get the regression panel dataset from pickled file
reg_panel = pd.read_pickle(Path(TABLE_PATH) / "reg_panel.pkl")

# Lag all variable except the Date and Token
for variable in reg_panel.columns:
    if variable not in ["Date", "Token", "is_boom", "Stable"]:
        reg_panel = lag_variable(reg_panel, variable, "Date", "Token")


LAG_DV_NAME = "$\it Dominance_{t-1}$"
result_full = render_regress_table(
    reg_panel=reg_panel, file_name="full", reg_combi=reg_combi, lag_dv=LAG_DV_NAME
)
result_bust = render_regress_table(
    reg_panel=reg_panel.query("is_boom != True"),
    file_name="bust",
    reg_combi=reg_combi,
    lag_dv=LAG_DV_NAME,
)
result_boom = render_regress_table(
    reg_panel=reg_panel.query("is_boom == True"),
    file_name="boom",
    reg_combi=reg_combi,
    lag_dv=LAG_DV_NAME,
)
