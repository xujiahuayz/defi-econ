# get the regression panel dataset from pickled file
import math
import re

import pandas as pd
from matplotlib import pyplot as plt

from environ.constants import (
    ALL_NAMING_DICT,
    COMPOUND_DEPLOYMENT_DATE,
    DATA_PATH,
    DEPENDENT_VARIABLES,
    SAMPLE_PERIOD,
)
from environ.tabulate.render_regression import (
    construct_regress_vars,
    render_regress_table,
    render_regress_table_latex,
)


reg_panel = pd.read_pickle(DATA_PATH / "processed" / "reg_panel_new.pkl")


compound_date = pd.DataFrame(
    {
        "Token": v["Token"] if v["Token"] != "ETH" else "WETH",
        "join_compound_day": pd.to_datetime(v["Date"].split(" ")[0]),
    }
    for v in COMPOUND_DEPLOYMENT_DATE
)

reg_panel = reg_panel.merge(compound_date, on="Token", how="left")

TIME_TO_JOIN = "time_to_join"
FACTOR_PREFIX = "_"

all_added_dates = set(
    # take only the date in '2019-05-07 01:20:54' without time
    compound_date["join_compound_day"]
)


for window in [14, 30]:

    diff_in_diff_df = reg_panel[
        ["Token", "Date", "join_compound_day"] + DEPENDENT_VARIABLES
    ]
    diff_in_diff_df[TIME_TO_JOIN] = (
        reg_panel["Date"] - reg_panel["join_compound_day"]
    ).dt.days.map(
        lambda x: str(int(x // 1))
        if (not math.isnan(x) and -window <= x <= window)
        else "NA"
    )

    # add time_to_join as a categorical variable
    diff_in_diff_df = pd.get_dummies(
        diff_in_diff_df, columns=[TIME_TO_JOIN], prefix_sep=FACTOR_PREFIX
    ).drop(columns=[f"{TIME_TO_JOIN}{FACTOR_PREFIX}NA"])

    time_to_treat_cols = diff_in_diff_df.columns[
        diff_in_diff_df.columns.str.contains(TIME_TO_JOIN + FACTOR_PREFIX)
    ]

    # sort time_to_treat_cols by the number of days with  minus sign for some
    # split by FACTOR_PREFIX and convert the last element to int and then sort
    time_to_treat_cols = sorted(
        time_to_treat_cols,
        key=lambda x: int(re.split(FACTOR_PREFIX, x)[-1]),
    )

    reg_combi = construct_regress_vars(
        dependent_variables=DEPENDENT_VARIABLES,
        iv_chunk_list=[[["constant"] + list(time_to_treat_cols)]],
        lag_iv=False,
        with_lag_dv=False,
        without_lag_dv=False,
    )

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
            treated_and_control_tokens = compound_date.loc[
                (compound_date["join_compound_day"] == treated_dates)
                | ~(compound_date["join_compound_day"] <= obs_end_date),
                "Token",
            ]

            did_reg_panel_full = did_reg_panel_full.append(
                did_reg_panel.loc[
                    did_reg_panel["Token"].isin(treated_and_control_tokens)
                    | did_reg_panel["join_compound_day"].isnull()
                ]
            )

    # restrict to SAMPE_PERIOD
    did_reg_panel_full = did_reg_panel_full[
        (did_reg_panel_full["Date"] >= SAMPLE_PERIOD[0])
        & (did_reg_panel_full["Date"] <= SAMPLE_PERIOD[1])
    ]

    did_reg_panel_full["constant"] = 1

    did_result = render_regress_table(
        reg_panel=did_reg_panel_full,
        reg_combi=reg_combi,
        standard_beta=False,
        panel_index_columns=(["Token", "Date"], [True, True]),
        robust=True,
    )

    did_result_latex = render_regress_table_latex(
        result_table=did_result.rename(
            index=lambda x: x.replace(TIME_TO_JOIN, "TimeToJoin\\")
            if x in time_to_treat_cols
            else x
        ),
        file_name=f"DID_{window}",
    )

    # get all the rows with index in time_to_treat_cols, ignore items in time_to_treat_cols that are not in the index
    plot_df = did_result.loc[did_result.index.intersection(list(time_to_treat_cols)), :]
    plot_df["time_to_join"] = plot_df.index.map(lambda x: int(x.split("_")[-1]))
    # sort by time_to_join
    plot_df = plot_df.sort_values(by="time_to_join")

    # get the number for each cell, where the string separates can be either $ or ^, and take the first one
    plot_df_co = (
        plot_df[did_result.columns]
        .apply(lambda x: x.str.split(r"[$^]").str[1])
        .astype(float)
    )
    plot_df_se = (
        plot_df[did_result.columns]
        .applymap(lambda x: re.findall(r"\$\s*([\d.]+)\s*\$", x)[-1])
        .astype(float)
    )

    x = plot_df["time_to_join"]
    # plot the result
    for k, v in did_result.loc["regressand"].iteritems():
        plt.plot(x, plot_df_co[k], label=f"${ALL_NAMING_DICT[v]}$")
        # stop after the first one

        # plot the standard error band
        plt.fill_between(
            x,
            plot_df_co[k] - 1.96 * plot_df_se[k],
            plot_df_co[k] + 1.96 * plot_df_se[k],
            alpha=0.2,
        )
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left", borderaxespad=0.0)

    # plot verticle line at 0
    plt.axvline(x=0, color="black", linestyle="--")
    # plot horizontal line at 0
    plt.axhline(y=0, color="black", linestyle="--")
    plt.show()
    plt.close()
