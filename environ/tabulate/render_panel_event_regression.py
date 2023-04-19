import re

import pandas as pd

from environ.constants import DEPENDENT_VARIABLES
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
    # TODO: consider removing this variable
    treatment_delay: int = 0,
    dependent_variables: list[str] = DEPENDENT_VARIABLES,
    covariates: list[str] | None = None,
    **kwargs,
) -> pd.DataFrame:
    diff_in_diff_df[reltime_dummy] = diff_in_diff_df["lead_lag"].map(
        lambda x: (
            str(int(x // lead_lag_interval))
            if -window <= x <= window
            # and int(x // lead_lag_interval) != 0
            else "NA"
        )
        if lead_lag_interval
        else (str(int(x >= treatment_delay)) if x >= treatment_delay else "NA")
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
        key=lambda x: int(re.split(pattern=dummy_prefix_sep, string=x)[-1]),
    )

    reg_combi = construct_regress_vars(
        dependent_variables=dependent_variables,
        iv_chunk_list=[
            [
                list(time_to_treat_cols) + covariates
                if covariates
                else []
                + [
                    # "after_treated_date",
                    #    "const"
                ]
                # + ([] if lead_lag_interval else ["after_treated_date"])
            ]
        ],
        lag_iv=False,
        with_lag_dv=False,
        without_lag_dv=False,
    )

    token_dates = diff_in_diff_df.loc[
        (diff_in_diff_df["lead_lag"] == 0), ["Token", "Date"]
    ]
    all_added_dates = set(token_dates["Date"])

    diff_in_diff_df = diff_in_diff_df.loc[
        diff_in_diff_df["Token"].isin(
            diff_in_diff_df.loc[diff_in_diff_df["lead_lag"] >= 0]["Token"]
        )
    ]

    did_reg_panel_full = pd.DataFrame()
    for treated_date in all_added_dates:
        # obs_start_date should be 30 days before treated_dates
        obs_start_date = treated_date - window
        obs_end_date = treated_date + window
        # select treated tokens
        treated_tokens = set(
            token_dates.loc[(token_dates["Date"] == treated_date)]["Token"]
        )
        if (
            obs_start_date
            >= diff_in_diff_df.loc[diff_in_diff_df["Token"].isin(treated_tokens)][
                "Date"
            ].min()
        ):
            did_reg_panel = diff_in_diff_df.loc[
                (diff_in_diff_df["Date"] >= obs_start_date - treatment_delay)
                & (diff_in_diff_df["Date"] <= obs_end_date)
            ]

            sum_dummies_grouped = did_reg_panel.groupby("Token")["has_been_treated"]

            # select control group
            sum_dummies = (  # sum_dummies_grouped.count() == 2 * window + 1) & (
                (sum_dummies_grouped.prod() == 1)
                if control_with_treated
                else (sum_dummies_grouped.sum() == 0)
            )

            if sum_dummies.sum() > 0:
                additional_tokens = set(sum_dummies[sum_dummies].index)

                # remove tokens with time_to_treat_cols != 0

                did_reg_panel = did_reg_panel.loc[
                    did_reg_panel["Token"].isin(additional_tokens | treated_tokens)
                    & (did_reg_panel["Date"] >= obs_start_date)
                ]
                # TODO: hanlde the below when a token is added exactly at the beginning of the window
                # assert (
                #     did_reg_panel.loc[~did_reg_panel["Token"].isin(treated_tokens), time_to_treat_cols].sum().sum()
                #     == 0
                # ), "untreated tokens should have 0 in time_to_treat_cols"
                # TODO: too implicit, need to make it more explicit
                if lead_lag_interval is None:
                    # doing the binary style, need interactive variable
                    did_reg_panel.loc[
                        ~did_reg_panel["Token"].isin(treated_tokens), time_to_treat_cols
                    ] = 0
                # did_reg_panel["after_treated_date"] = (
                #     did_reg_panel["Date"] >= treated_date
                # ).astype(int)
                did_reg_panel_full = pd.concat(
                    [did_reg_panel_full, did_reg_panel], axis=0, ignore_index=True
                )

    # did_reg_panel_full["const"] = 1
    did_result = render_regress_table(
        reg_panel=did_reg_panel_full,
        reg_combi=reg_combi,
        **kwargs,
    )
    return did_result
