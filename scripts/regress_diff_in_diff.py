# get the regression panel dataset from pickled file
import numpy as np
import pandas as pd

from environ.constants import COMPOUND_DEPLOYMENT_DATE, SAMPLE_PERIOD, TABLE_PATH
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

reg_panel = pd.read_pickle(TABLE_PATH / "reg_panel.pkl")
# convert COMPOUND_DEPLOYMENT_DATE to dataframe and convert 'Date' column to datetime
compound_tokens = pd.DataFrame(COMPOUND_DEPLOYMENT_DATE)[["Token", "Date"]]
compound_tokens["join_compound_date"] = pd.to_datetime(compound_tokens["Date"])
# change ETH under Token to WETH
compound_tokens.loc[compound_tokens["Token"] == "ETH", "Token"] = "WETH"
# add a column to indicate whether the token was added to compound within the sample period
compound_tokens["added_within_sample"] = [
    1 if v else np.nan
    for v in compound_tokens["join_compound_date"] >= SAMPLE_PERIOD[0]
]

# merge compound_tokens with reg_panel
reg_panel = reg_panel.merge(
    compound_tokens[["Token", "join_compound_date", "added_within_sample"]],
    on=["Token"],
    how="left",
)

reg_panel["is_in_compound"] = reg_panel["Date"] >= reg_panel["join_compound_date"]

reg_panel["const"] = 1
reg_panel["is_in_compound"] = reg_panel["is_in_compound"].astype(int)

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

reg_panel[name_interaction_variable("is_in_compound", "added_within_sample")] = (
    reg_panel["is_in_compound"] * reg_panel["added_within_sample"]
)

iv_chunk_list_unlagged = [
    [
        [
            # "const",
            "is_in_compound",
            "added_within_sample",
            # name_interaction_variable("is_in_compound", "added_within_sample"),
        ]
    ]
]


# restrict to SAMPLE_PERIOD
reg_panel = reg_panel.loc[
    (reg_panel["Date"] >= SAMPLE_PERIOD[0]) & (reg_panel["Date"] <= SAMPLE_PERIOD[1])
]

# iv_chunk_list.append([["is_in_compound"]])
reg_combi_interact = construct_regress_vars(
    dependent_variables=dependent_variables,
    iv_chunk_list=iv_chunk_list_unlagged,
    lag_iv=False,
    with_lag_dv=False,
    without_lag_dv=False,
)


result_full_interact = render_regress_table(
    reg_panel=reg_panel,
    reg_combi=reg_combi_interact,
    method="ols",
    standard_beta=False,
    robust=False,
)

result_full_latex_interact = render_regress_table_latex(
    result_table=result_full_interact, file_name="diff_in_diff"
)
