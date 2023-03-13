# get the regression panel dataset from pickled file
from pathlib import Path

import pandas as pd

from environ.constants import TABLE_PATH
from environ.utils.variable_constructer import (
    lag_variable,
    name_boom_interact_var,
    name_lag_variable,
)
from environ.tabulate.render_regression import (
    construct_regress_vars,
    render_regress_table,
    render_regress_table_latex,
)
from scripts.prepare_panel import add_lag_interact_vars

reg_panel = pd.read_pickle(Path(TABLE_PATH) / "reg_panel.pkl")


dependent_variables = [
    "avg_eigenvector_centrality",
    "betweenness_centrality_volume",
    "betweenness_centrality_count",
    "Volume_share",
    "TVL_share",
]

# fill the missing values with 0 for all dependent variables
for dv in dependent_variables:
    reg_panel[dv] = reg_panel[dv].fillna(0)


iv_chunk_list_unlagged = [
    [["std", "corr_gas", "mcap_share", "Supply_share"]],
    [
        # ["Stable", "depegging_degree"],
        # ["pegging_degree"],
        # ["depeg_pers"],
        ["stableshare"],
    ],
    [["corr_eth", "corr_sp"]],
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
                lagged_var = name_lag_variable(v)
                this_ivs.extend([lagged_var, name_boom_interact_var(lagged_var)])
                iv_set.add(v)
            else:
                this_ivs.append(v)
        this_ivs_chunk.append(this_ivs)
    iv_chunk_list.append(this_ivs_chunk)


# # Get the regression panel dataset from pickled file
# reg_panel = pd.read_pickle(Path(TABLE_PATH) / "reg_panel.pkl")

# # Lag all variable except the Date and Token
# for variable in reg_panel.columns:
#     if variable in (iv_set | set(dependent_variables)):
#         reg_panel = lag_variable(reg_panel, variable, "Date", "Token")
#         lagged_var = name_lag_variable(variable)
#         reg_panel[name_boom_interact_var(lagged_var)] = (
#             reg_panel[lagged_var] * reg_panel["is_boom"]
#         )

reg_combi_interact = construct_regress_vars(
    dependent_variables=dependent_variables,
    iv_chunk_list=iv_chunk_list,
    # no need to lag the ivs as they are already lagged
    lag_iv=False,
    with_lag_dv=True,
    without_lag_dv=False,
)

reg_panel = add_lag_interact_vars(reg_panel)
result_full_interact = render_regress_table(
    reg_panel=reg_panel,
    reg_combi=reg_combi_interact,
    lag_dv=LAG_DV_NAME,
    method="panel",
)

result_full_latex_interact = render_regress_table_latex(
    result_table=result_full_interact, method="panel", file_name="full_dom"
)

reg_combi = construct_regress_vars(
    dependent_variables=dependent_variables,
    iv_chunk_list=iv_chunk_list_unlagged,
    lag_iv=True,
    with_lag_dv=True,
    without_lag_dv=False,
)

result_full = render_regress_table(
    reg_panel=reg_panel,
    reg_combi=reg_combi,
    lag_dv=LAG_DV_NAME,
    method="panel",
)

result_full_latex = render_regress_table_latex(
    result_table=result_full, method="panel", file_name="full_dom_no_interact"
)

result_boom = render_regress_table(
    reg_panel=reg_panel.query("is_boom"),
    reg_combi=reg_combi,
    lag_dv=LAG_DV_NAME,
    method="panel",
)

result_boom_latex = render_regress_table_latex(
    result_table=result_boom, method="panel", file_name="boom_dom"
)

result_bust = render_regress_table(
    reg_panel=reg_panel.query("is_boom == False"),
    reg_combi=reg_combi,
    lag_dv=LAG_DV_NAME,
    method="panel",
)

result_bust_latex = render_regress_table_latex(
    result_table=result_bust, method="panel", file_name="bust_dom"
)

# create week colume based on Date
reg_panel_by_week = reg_panel.reset_index()
# sort by date
reg_panel_by_week = reg_panel_by_week.sort_values("Date")
reg_panel_by_week["Date"] = reg_panel_by_week["Date"].apply(
    lambda x: int(x.timestamp() // (7 * 24 * 60 * 60))
)
reg_panel_by_week["is_boom"] = reg_panel_by_week["is_boom"].astype(int)
# average variables by week
reg_panel_by_week = reg_panel_by_week.groupby(["Token", "Date"]).mean()
reg_panel_by_week["is_boom"] = reg_panel_by_week["is_boom"] > 3.5

reg_panel_by_week = add_lag_interact_vars(reg_panel_by_week)

result_full_week = render_regress_table(
    reg_panel=reg_panel_by_week,
    reg_combi=reg_combi,
    lag_dv=LAG_DV_NAME,
    method="panel",
)

result_full_latex = render_regress_table_latex(
    result_table=result_full_week, method="panel", file_name="full_dom_week"
)


# create week colume based on Date
reg_panel_weekend = reg_panel.reset_index()
# sort by date
reg_panel_weekend = reg_panel_weekend.sort_values("Date")
reg_panel_weekend["day_of_week"] = reg_panel_weekend["Date"].apply(
    lambda x: int(x.timestamp() // (24 * 60 * 60) % 7)
)
reg_panel_weekend.set_index(["Token", "Date"], inplace=True)
reg_panel_weekend = reg_panel_weekend.query("day_of_week == 0")
reg_panel_weekend = add_lag_interact_vars(reg_panel_weekend)

result_weekend = render_regress_table(
    reg_panel=reg_panel_weekend,
    reg_combi=reg_combi,
    lag_dv=LAG_DV_NAME,
    method="panel",
)

result_weekend_latex = render_regress_table_latex(
    result_table=result_weekend, method="panel", file_name="full_weekend"
)
