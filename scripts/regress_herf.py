# get the regression panel dataset from pickled file
import pandas as pd

from environ.constants import TABLE_PATH
from environ.tabulate.render_regression import (
    construct_regress_vars,
    render_regress_table,
    render_regress_table_latex,
)
from environ.utils.variable_constructer import (
    lag_variable,
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
            # "const",
        ]
    ],
]


# Get the regression panel dataset from pickled file
herf_panel = pd.read_pickle(TABLE_PATH / "herf_panel.pkl")

herf_panel = lag_variable(
    herf_panel, dependent_variables + iv_chunk_list_unlagged[0][0], time_variable="Date"
)
dummy_vars = pd.get_dummies(herf_panel["Date"].dt.to_period("Y").astype(str))
herf_panel = pd.concat([herf_panel, dummy_vars], axis=1)
iv_chunk_list_unlagged.append([list(dummy_vars.columns)])

reg_combi = construct_regress_vars(
    dependent_variables=dependent_variables,
    iv_chunk_list=iv_chunk_list_unlagged,
    lag_iv=False,
    with_lag_dv=True,
    without_lag_dv=False,
)


# make is_boom numeric
herf_panel["is_boom"] = herf_panel["is_boom"].astype(int)
# herf_panel["const"] = 1

LAG_DV_NAME = "$\it HHI_{t-1}$"

result_full = render_regress_table(
    reg_panel=herf_panel,
    reg_combi=reg_combi,
    lag_dv=LAG_DV_NAME,
    method="ols",
    standard_beta=False,
    robust=True,
)
result_full_latex = render_regress_table_latex(
    result_table=result_full, file_name="full_herf", method="ols"
)
