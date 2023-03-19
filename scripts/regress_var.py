# get the regression panel dataset from pickled file
from itertools import product
from pathlib import Path

import pandas as pd

from environ.constants import TABLE_PATH
from environ.tabulate.render_regression import (
    construct_regress_vars,
    render_regress_table,
    render_regress_table_latex,
)
from environ.utils.variable_constructer import (
    diff_variable,
    lag_variable,
    name_diff_variable,
    name_lag_variable,
)

reg_panel = pd.read_pickle(Path(TABLE_PATH) / "reg_panel.pkl")

betw_cents = [
    "betweenness_centrality_volume",
    "betweenness_centrality_count",
]
other_dvs = [
    "avg_eigenvector_centrality",
    # "stableshare",
]
all_dev = betw_cents + other_dvs
reg_panel[all_dev] = reg_panel[all_dev].fillna(0)

reg_panel = diff_variable(
    data=reg_panel,
    variable=all_dev,
    entity_variable="Token",
    time_variable="Date",
    lag=1,
)

total_lag = 1
lag_range = range(1, total_lag + 1)
for lag in lag_range:
    reg_panel = lag_variable(
        reg_panel,
        # [name_diff_variable(v, lag=1) for v in all_dev],
        all_dev,
        time_variable="Date",
        entity_variable="Token",
        lag=lag,
    )

reg_combi = []
for b in betw_cents:
    # dependent_variables = [name_diff_variable(v, lag=1) for v in other_dvs + [b]]
    dependent_variables = other_dvs + [b]
    # fill the missing values with 0 for all dependent variables
    ivs = [
        name_lag_variable(dv, lag)
        for dv, lag in product(dependent_variables, lag_range)
    ]
    reg_combi.extend(
        construct_regress_vars(
            dependent_variables=dependent_variables,
            iv_chunk_list=[[ivs]],
            with_lag_dv=False,
            without_lag_dv=False,
        )
    )


for k, q in {"full": "", "boom": "is_boom", "bust": "~is_boom"}.items():
    reg_result = render_regress_table(
        reg_panel=reg_panel.query(q) if q else reg_panel,
        reg_combi=reg_combi,
        method="panel",
        standard_beta=False,
        lag_dv="",
        robust=True,
    )

    result_full_latex_interact = render_regress_table_latex(
        result_table=reg_result, file_name=f"{k}_dom_var"
    )
