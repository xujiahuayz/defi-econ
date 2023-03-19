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
]

# fill the missing values with 0 for all dependent variables
for dv in dependent_variables:
    reg_panel[dv] = reg_panel[dv].fillna(0)


iv_chunk_list_unlagged = [
    [["betweenness_centrality_count"], ["betweenness_centrality_volume"]],
    [[], ["avg_eigenvector_centrality"]],
]


reg_combi_interact = construct_regress_vars(
    dependent_variables=dependent_variables,
    iv_chunk_list=iv_chunk_list_unlagged,
    # no need to lag the ivs as they are already lagged
    lag_iv=False,
    with_lag_dv=False,
    without_lag_dv=False,
)


result_r2 = render_regress_table(
    reg_panel=reg_panel,
    reg_combi=reg_combi_interact,
    method="ols",
    standard_beta=False,
    robust=False,
)

result_full_latex_interact = render_regress_table_latex(
    result_table=result_r2, file_name="full_vshare", method="ols"
)
