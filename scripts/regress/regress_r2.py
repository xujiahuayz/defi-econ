# get the regression panel dataset from pickled file

import pandas as pd

from environ.constants import TABLE_PATH, PROCESSED_DATA_PATH
from environ.tabulate.render_regression import (
    construct_regress_vars,
    render_regress_table,
    render_regress_table_latex,
)


reg_panel = pd.read_pickle(
    PROCESSED_DATA_PATH / "panel_main.pickle.zip", compression="zip"
)


dependent_variables = [
    "Volume_share",
    "total_eigen_centrality_undirected",
]


iv_chunk_list_unlagged = [
    [
        ["volume_ultimate_share", "vol_inter_full_len_share"],
        ["eigen_centrality_undirected", "betweenness_centrality_volume"],
    ],
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
    result_table=result_r2, file_name=TABLE_PATH / "full_vshare"
)
