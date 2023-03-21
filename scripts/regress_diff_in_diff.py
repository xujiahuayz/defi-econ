# get the regression panel dataset from pickled file
import pandas as pd

from environ.constants import COMPOUND_DEPLOYMENT_DATE, SAMPLE_PERIOD, TABLE_PATH
from environ.tabulate.render_regression import (
    construct_regress_vars,
    render_regress_table,
    render_regress_table_latex,
)
from environ.utils.variable_constructer import name_interaction_variable

reg_panel = pd.read_pickle(TABLE_PATH / "reg_panel.pkl")

compound_date = [
    {
        "Token": v["Token"] if v["Token"] != "ETH" else "WETH",
        "join_compound_day": pd.to_datetime(v["Date"].split(" ")[0]),
    }
    for v in COMPOUND_DEPLOYMENT_DATE
]

# add a column to indicate whether the token was added to compound within the sample period
all_added_dates = set(
    # take only the date in '2019-05-07 01:20:54' without time
    v["join_compound_day"]
    for v in compound_date
)

dependent_variables = [
    "avg_eigenvector_centrality",
    "betweenness_centrality_volume",
    "betweenness_centrality_count",
    "Volume_share",
    "TVL_share",
]


iv_chunk_list_unlagged = [
    [
        [
            # "const",
            "is_treated_token",
            "after_treated_date",
            name_interaction_variable("is_treated_token", "after_treated_date"),
        ]
    ]
]

reg_combi = construct_regress_vars(
    dependent_variables=dependent_variables,
    iv_chunk_list=iv_chunk_list_unlagged,
    lag_iv=False,
    with_lag_dv=False,
    without_lag_dv=False,
)

diff_in_diff_df = reg_panel[["Token", "Date"] + dependent_variables]
# do the same as above but without SettingWithCopyWarning
diff_in_diff_df = diff_in_diff_df.assign(
    after_treated_date=0, is_treated_token=0
).fillna(0)

for window in [14]:

    did_reg_panel_full = pd.DataFrame()
    for treated_dates in set(all_added_dates):
        # obs_start_date should be 30 days before treated_dates
        obs_start_date = treated_dates - pd.Timedelta(days=window)
        obs_end_date = treated_dates + pd.Timedelta(days=window)

        if obs_start_date >= pd.to_datetime(SAMPLE_PERIOD[0]):
            did_reg_panel = diff_in_diff_df.loc[
                (diff_in_diff_df["Date"] >= obs_start_date)
                & (diff_in_diff_df["Date"] <= obs_end_date)
            ]
            # find out tokens that were added to compound on treated_dates
            treated_tokens = []
            omitted_tokens = []
            for v in compound_date:
                if v["join_compound_day"] == treated_dates:
                    treated_tokens.append(v["Token"])
                elif v["join_compound_day"] < obs_end_date:
                    omitted_tokens.append(v["Token"])
            # remove omitted tokens did_reg_panel
            did_reg_panel = did_reg_panel.loc[
                ~did_reg_panel["Token"].isin(omitted_tokens)
            ]
            # set 'is_treated_token' to 1 for treated tokens
            did_reg_panel.loc[
                did_reg_panel["Token"].isin(treated_tokens), "is_treated_token"
            ] = 1
            # set 'after_treated_date' to 1 for dates after treated_dates
            did_reg_panel.loc[
                did_reg_panel["Date"] >= treated_dates, "after_treated_date"
            ] = 1

            did_reg_panel_full = did_reg_panel_full.append(did_reg_panel)

    did_reg_panel_full[
        name_interaction_variable("is_treated_token", "after_treated_date")
    ] = (
        did_reg_panel_full["is_treated_token"]
        * did_reg_panel_full["after_treated_date"]
    )

    did_result = render_regress_table(
        reg_panel=did_reg_panel_full,
        reg_combi=reg_combi,
        method="ols",
        standard_beta=False,
        robust=False,
    )

    did_result_latex = render_regress_table_latex(
        result_table=did_result,
        file_name=f"DID_{window}",
    )
