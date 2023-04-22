# get the regression panel dataset from pickled file
import pandas as pd

from environ.constants import (
    DEPENDENT_VARIABLES,
    SAMPLE_PERIOD,
    PROCESSED_DATA_PATH,
    TABLE_PATH,
)
from environ.tabulate.render_regression import (
    construct_regress_vars,
    render_regress_table,
    render_regress_table_latex,
)
from environ.utils.variable_constructer import (
    lag_variable_columns,
    name_interaction_variable,
    name_lag_variable,
)

reg_panel = pd.read_pickle(
    PROCESSED_DATA_PATH / "panel_main.pickle.zip", compression="zip"
)
reg_panel[DEPENDENT_VARIABLES].isna().sum()


iv_chunk_list_unlagged = [
    [
        [
            # "clustering_coefficient",
            "mcap_share",
            "TVL_share",
            "Supply_share",
            "std",
        ]
    ],
    [
        # ["Stable", "depegging_degree"],
        # ["pegging_degree"],
        # ["depeg_pers"],
        ["stableshare"],
    ],
    [
        # ["corr_gas_with_laggedreturn"],
        ["corr_gas"]
    ],
    [
        [
            "corr_eth"
            #   , "corr_sp"
        ]
    ],
]

LAG_DV_NAME = "\it Dominance_{t-1}"

iv_chunk_list = []
iv_set = set()
for ivs_chunk in iv_chunk_list_unlagged:
    this_ivs_chunk = []
    for ivs in ivs_chunk:
        this_ivs = []
        for v in ivs:
            if v not in ["is_boom", "Stable", "is_in_compound"]:
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
    if v not in ["is_boom", "Stable", "is_in_compound"]
]
variables.extend(DEPENDENT_VARIABLES)
reg_panel = lag_variable_columns(
    data=reg_panel,
    variable=DEPENDENT_VARIABLES + list(iv_set),
    time_variable="Date",
    entity_variable="Token",
    lag=1,
)
for iv in iv_set:
    lagged_var = name_lag_variable(iv)
    reg_panel[name_interaction_variable(lagged_var, "is_boom")] = (
        reg_panel[lagged_var] * reg_panel["is_boom"]
    )

# restrict to SAMPLE_PERIOD
reg_panel = reg_panel.loc[
    (reg_panel["Date"] >= SAMPLE_PERIOD[0]) & (reg_panel["Date"] <= SAMPLE_PERIOD[1])
]

# iv_chunk_list.append([["is_in_compound"]])
reg_combi_interact = construct_regress_vars(
    dependent_variables=DEPENDENT_VARIABLES,
    iv_chunk_list=iv_chunk_list,
    # no need to lag the ivs as they are already lagged
    lag_iv=False,
    with_lag_dv=True,
    without_lag_dv=False,
)


result_full_interact = render_regress_table(
    reg_panel=reg_panel,
    reg_combi=reg_combi_interact,
    lag_dv=LAG_DV_NAME,
    panel_index_columns=(["Token", "Date"], [True, False]),
    standard_beta=False,
    robust=True,
)

result_full_latex_interact = render_regress_table_latex(
    result_table=result_full_interact,
    file_name=TABLE_PATH / "slides_full_dom",
)
