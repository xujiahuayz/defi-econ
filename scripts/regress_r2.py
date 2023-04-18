# get the regression panel dataset from pickled file

import pandas as pd

from environ.constants import DATA_PATH, DATA_PATH
from environ.tabulate.render_regression import (
    construct_regress_vars,
    render_regress_table,
    render_regress_table_latex,
)


reg_panel = pd.read_pickle(DATA_PATH / "processed" / "reg_panel_merged.pkl")


dependent_variables = [
    "Volume_share",
]

# fill the missing values with 0 for all dependent variables
for dv in dependent_variables:
    reg_panel[dv] = reg_panel[dv].fillna(0)


iv_chunk_list_unlagged = [
    [[], ["vol_inter_full_len_share"]],
    [[], ["vol_undirected_full_len_share"]],
    # [["betweenness_centrality_count"], ["betweenness_centrality_volume"]],
    # [[], ["eigen_centrality_undirected"]],
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
    standard_beta=False,
    robust=False,
)

result_latex = render_regress_table_latex(
    result_table=result_r2, file_name=DATA_PATH / "full_vshare"
)
