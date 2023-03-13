# get the regression panel dataset from pickled file
from pathlib import Path

import pandas as pd

from environ.constants import TABLE_PATH
from environ.utils.variable_constructer import (
    lag_variable,
)
from environ.tabulate.render_regression import (
    construct_regress_vars,
    render_regress_table,
    render_regress_table_latex,
)

from environ.utils.variable_constructer import (
    name_log_return_vol_variable,
)

dependent_variables = [
    "herfindahl_volume",
    "herfindahl_betweenness_centrality_count",
    "herfindahl_betweenness_centrality_volume",
    "herfindahl_tvl",
]

iv_chunk_list_unlagged = [
    [
        [
            "is_boom",
            "total_volumes",
            name_log_return_vol_variable(
                "S&P", rolling_window_return=1, rolling_window_vol=30
            ),
            "gas_price_usd",
            name_log_return_vol_variable(
                "gas_price_usd", rolling_window_return=1, rolling_window_vol=30
            ),
            "const",
        ]
    ],
]


reg_combi = construct_regress_vars(
    dependent_variables=dependent_variables,
    iv_chunk_list=iv_chunk_list_unlagged,
    lag_iv=False,
    with_lag_dv=True,
    without_lag_dv=False,
)

# Get the regression panel dataset from pickled file
herf_panel = pd.read_pickle(Path(TABLE_PATH) / "herf_panel.pkl")

# Lag all variable except the Date and Token
for variable in herf_panel.columns:
    if variable not in ["is_boom", "boom", "bust", "Date", "const"]:
        herf_panel = lag_variable(herf_panel, variable, time_variable="Date")

# make is_boom numeric
herf_panel["is_boom"] = herf_panel["is_boom"].astype(int)
herf_panel["const"] = 1

LAG_DV_NAME = "$\it HHI_{t-1}$"

result_full = render_regress_table(
    reg_panel=herf_panel,
    reg_combi=reg_combi,
    lag_dv=LAG_DV_NAME,
    method="ols",
    standard_beta=True,
)
result_full_latex = render_regress_table_latex(
    result_table=result_full, file_name="full_herf", method="ols"
)
