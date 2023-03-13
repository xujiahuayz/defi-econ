# get the regression panel dataset from pickled file
from itertools import product
from os import path

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

iv_chunk_main = [["std", "corr_gas", "mcap_share", "Supply_share"]]
iv_chunk_eth = [["corr_eth"], ["corr_sp"]]

# lag all iv above
iv_chunk_main = [list(map(name_lag_variable, iv)) for iv in iv_chunk_main]
iv_chunk_eth = [list(map(name_lag_variable, iv)) for iv in iv_chunk_eth]
iv_chunk_stable = [
    ["Stable", name_lag_variable("depegging_degree")],
    [name_lag_variable("pegging_degree")],
    [name_lag_variable("depeg_pers")],
    [name_lag_variable("stableshare")],
]
LAG_DV_NAME = "$\it Dominance_{t-1}$"

reg_combi = []
for dv in dependent_variables:
    lag_dv_name = name_lag_variable(dv)
    # determines whether to include lagged dependent variable
    dv_lag = [[lag_dv_name]]
    for iv_combi in product(dv_lag, iv_chunk_main, iv_chunk_stable, iv_chunk_eth):
        iv = [x for y in iv_combi for x in y]
        reg_combi.append((dv, iv))


# Get the regression panel dataset from pickled file
reg_panel = pd.read_pickle(path.join(TABLE_PATH, "reg_panel.pkl"))

# Lag all variable except the Date and Token
for variable in reg_panel.columns:
    if variable not in ["Date", "Token"]:
        reg_panel = lag_variable(reg_panel, variable, "Date", "Token")

result_full = render_regress_table(
    reg_panel=reg_panel, file_name="full", reg_combi=reg_combi
)
result_bust = render_regress_table(
    reg_panel=reg_panel[reg_panel["is_boom"] != True],
    file_name="bust",
    reg_combi=reg_combi,
)
result_boom = render_regress_table(
    reg_panel=reg_panel[reg_panel["is_boom"] == True],
    file_name="boom",
    reg_combi=reg_combi,
)
