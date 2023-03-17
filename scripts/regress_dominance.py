# get the regression panel dataset from pickled file
from pathlib import Path

import pandas as pd

from environ.constants import TABLE_PATH
from environ.tabulate.render_regression import (
    construct_regress_vars,
    render_regress_table,
    render_regress_table_latex,
)
from environ.utils.variable_constructer import (
    lag_variable,
    name_interaction_variable,
    name_lag_variable,
)

reg_panel = pd.read_pickle(Path(TABLE_PATH) / "reg_panel.pkl")


dependent_variables = [
    "Volume_share",
    # "volume_in_share",
    # "volume_out_share",
]

# fill the missing values with 0 for all dependent variables
for dv in dependent_variables:
    reg_panel[dv] = reg_panel[dv].fillna(0)


iv_chunk_list_unlagged = [
    [["betweenness_centrality_count"], ["betweenness_centrality_volume"]],
    [[], ["avg_eigenvector_centrality"]],
]

LAG_DV_NAME = "$\it Dominance_{t-1}$"


iv_chunk_list = []
iv_set = set()
for ivs_chunk in iv_chunk_list_unlagged:
    this_ivs_chunk = []
    for ivs in ivs_chunk:
        this_ivs = []
        for v in ivs:
            if v not in ["is_boom", "Stable"]:
                lagged_var = (
                    v if v == "corr_gas_with_laggedreturn" else name_lag_variable(v)
                )
                this_ivs.extend(
                    [lagged_var, name_interaction_variable(lagged_var, "is_boom")]
                )
                iv_set.add(v)
            else:
                this_ivs.append(v)
        this_ivs_chunk.append(this_ivs)
    iv_chunk_list.append(this_ivs_chunk)


# flatten iv_chunk_list_unlagged and dependent_variables
variables = [
    v
    for ivs_chunk in iv_chunk_list_unlagged
    for ivs in ivs_chunk
    for v in ivs
    if v not in ["is_boom", "Stable", "corr_gas_with_laggedreturn"]
]
variables.extend(dependent_variables)
reg_panel = lag_variable(
    data=reg_panel,
    variable=dependent_variables + list(iv_set),
    time_variable="Date",
    entity_variable="Token",
    lag=1,
)
for iv in iv_set:
    lagged_var = name_lag_variable(iv)
    reg_panel[name_interaction_variable(lagged_var, "is_boom")] = (
        reg_panel[lagged_var] * reg_panel["is_boom"]
    )


reg_combi_interact = construct_regress_vars(
    dependent_variables=dependent_variables,
    iv_chunk_list=iv_chunk_list_unlagged,
    # no need to lag the ivs as they are already lagged
    lag_iv=False,
    with_lag_dv=False,
    without_lag_dv=False,
)


result_full_interact = render_regress_table(
    reg_panel=reg_panel,
    reg_combi=reg_combi_interact,
    lag_dv=LAG_DV_NAME,
    method="ols",
    standard_beta=False,
)

result_full_latex_interact = render_regress_table_latex(
    result_table=result_full_interact, file_name="full_vshare", method="ols"
)
