import re

import pandas as pd

from environ.constants import DEPENDENT_VARIABLES, SAMPLE_PERIOD
from environ.tabulate.render_regression import (
    construct_regress_vars,
    render_regress_table,
)


def panel_event_regression(
    diff_in_diff_df: pd.DataFrame,
    window: int = 14,
    control_with_treated: bool = True,
    lead_lag_interval: int | None = None,
    reltime_dummy: str = "rel_time",
    dummy_prefix_sep: str = "_",
    **kwargs,
) -> pd.DataFrame:

    diff_in_diff_df[reltime_dummy] = diff_in_diff_df["lead_lag"].map(
        lambda x: (str(int(x // lead_lag_interval)) if -window <= x <= window else "NA")
        if lead_lag_interval
        else (str(int(x >= 0)) if x >= 0 else "NA")
    )

    # add time_to_join as a categorical variable
    diff_in_diff_df = pd.get_dummies(
        diff_in_diff_df, columns=[reltime_dummy], prefix_sep=dummy_prefix_sep
    ).drop(columns=[f"{reltime_dummy}{dummy_prefix_sep}NA"])

    time_to_treat_cols = diff_in_diff_df.columns[
        diff_in_diff_df.columns.str.contains(reltime_dummy + dummy_prefix_sep)
    ]

    # sort time_to_treat_cols by the number of days with  minus sign for some
    # split by FACTOR_PREFIX and convert the last element to int and then sort
    time_to_treat_cols = sorted(
        time_to_treat_cols,
        key=lambda x: int(re.split(dummy_prefix_sep, x)[-1]),
    )

    reg_combi = construct_regress_vars(
        dependent_variables=DEPENDENT_VARIABLES,
        iv_chunk_list=[[list(time_to_treat_cols)]],
        lag_iv=False,
        with_lag_dv=False,
        without_lag_dv=False,
    )

    all_added_dates = set(
        diff_in_diff_df.loc[(diff_in_diff_df["lead_lag"] == 0), "Date"]
    )

    did_reg_panel_full = pd.DataFrame()
    for treated_date in all_added_dates:
        # obs_start_date should be 30 days before treated_dates
        obs_start_date = treated_date - pd.Timedelta(days=window)
        obs_end_date = treated_date + pd.Timedelta(days=window)

        if obs_start_date >= pd.to_datetime(SAMPLE_PERIOD[0]):

            did_reg_panel = diff_in_diff_df.loc[
                (diff_in_diff_df["Date"] >= obs_start_date)
                & (diff_in_diff_df["Date"] <= obs_end_date)
            ]

            sum_dummies_grouped = did_reg_panel.groupby("Token")["has_been_treated"]

            # select control group
            sum_dummies = (
                (sum_dummies_grouped.prod() == 1)  # already treated
                if control_with_treated
                else (sum_dummies_grouped.sum() == 0)  # never treated
            )

            additional_tokens = set(sum_dummies[sum_dummies].index)

            # select treated tokens, which are those with lead_lag == 0 at treated_date
            treated_tokens = set(
                did_reg_panel.loc[
                    (did_reg_panel["Date"] == treated_date)
                    & (did_reg_panel["lead_lag"] == 0),
                    "Token",
                ]
            )

            did_reg_panel_full = did_reg_panel_full.append(
                did_reg_panel.loc[
                    did_reg_panel["Token"].isin(additional_tokens | treated_tokens)
                ]
            )

    # restrict to SAMPE_PERIOD
    did_reg_panel_full = did_reg_panel_full[
        (did_reg_panel_full["Date"] >= SAMPLE_PERIOD[0])
        & (did_reg_panel_full["Date"] <= SAMPLE_PERIOD[1])
    ]

    did_result = render_regress_table(
        reg_panel=did_reg_panel_full,
        reg_combi=reg_combi,
        **kwargs,
    )
    return did_result
