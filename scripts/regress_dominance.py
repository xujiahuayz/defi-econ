# get the regression panel dataset from pickled file
from itertools import product
from pathlib import Path

import pandas as pd

from environ.constants import TABLE_PATH
from environ.utils.lags import lag_variable, name_lag_variable
from playground.regression import render_regress_table

dependent_variables = [
    "avg_eigenvector_centrality",
    "betweenness_centrality_volume",
    "betweenness_centrality_count",
    "Volume_share",
]

iv_chunk_list_unlagged = [
    [["std", "corr_gas", "mcap_share", "Supply_share"]],
    [
        ["Stable", "depegging_degree"],
        ["pegging_degree"],
        ["depeg_pers"],
        ["stableshare"],
    ],
    [["corr_eth"], ["corr_sp"]],
]

# lag all iv above
iv_chunk_list = [
    [
        [name_lag_variable(v) if v not in ["Stable"] else v for v in iv]
        for iv in iv_chunk
    ]
    for iv_chunk in iv_chunk_list_unlagged
]

reg_combi = [
    (dv, [x for y in iv_combi for x in y])
    for dv in dependent_variables
    for iv_combi in product(*([[[name_lag_variable(dv)]]] + iv_chunk_list))
]

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
