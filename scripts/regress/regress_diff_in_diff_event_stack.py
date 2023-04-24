# get the regression panel dataset from pickled file

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from environ.constants import (
    AAVE_DEPLOYMENT_DATE,
    ALL_NAMING_DICT,
    COMPOUND_DEPLOYMENT_DATE,
    DEPENDENT_VARIABLES,
    FIGURE_PATH,
    PROCESSED_DATA_PATH,
    SAMPLE_PERIOD,
    TABLE_PATH,
)
from environ.tabulate.render_panel_event_regression import panel_event_regression
from environ.tabulate.render_regression import render_regress_table_latex
from environ.utils.variable_constructer import (
    name_interaction_variable,
    return_vol,
)

# combine AAVE and COMPOUND deployment date list
plf_list = AAVE_DEPLOYMENT_DATE + COMPOUND_DEPLOYMENT_DATE
# change the format of each element in the list to {'DAI': ['2019-05-07 01:20:54', '2019-05-07 01:20:54']}

INTERVAL_IN_SECONDS = 3600 * 24 * 1

name_map = {"ETH": "WETH", "WBTC2": "WBTC"}
plf_dict: dict[str, list] = {}
for v in plf_list:
    # replace the token name 'ETH' with 'WETH' and WBTC2 with WBTC
    token = name_map.get(v["Token"], v["Token"])
    # convert date from string to timestamp
    date = int(pd.to_datetime(v["Date"]).timestamp()) // INTERVAL_IN_SECONDS
    if token in plf_dict:
        plf_dict[token].append(date)
    else:
        plf_dict[token] = [date]

# get the earliest date for each token
plf_date = pd.DataFrame(
    {"Token": k, "earliest_join_time": min(v), "join_time_list": v}
    for k, v in plf_dict.items()
)


reg_panel = pd.read_pickle(
    PROCESSED_DATA_PATH / "panel_main.pickle.zip", compression="zip"
)
# restrict to SAMPE_PERIOD
reg_panel = reg_panel[
    (reg_panel["Date"] >= SAMPLE_PERIOD[0]) & (reg_panel["Date"] <= SAMPLE_PERIOD[1])
]

variable = "dollar_exchange_rate"
rolling_window_return = 1
rolling_window_vol = 30
reg_panel = return_vol(
    reg_panel,
    variable=variable,
    rolling_window_return=rolling_window_return,
    rolling_window_vol=rolling_window_vol,
)
reg_panel["Date"] = reg_panel["Date"].astype(int) // (10**9 * INTERVAL_IN_SECONDS)
# average by Date and Token
reg_panel = reg_panel.groupby(["Date", "Token"]).mean(numeric_only=True).reset_index()

reg_panel = reg_panel.merge(plf_date, on="Token", how="left")


RELTIME_DUMMY = "rel_time"
FACTOR_PREFIX = "_"

all_added_dates = set(plf_date["join_time_list"].sum())

indvs = [
    "mcap_share",
    "stableshare",
    "std"
    #  "Supply_share",
    #  "TVL_share"
]

dvs = DEPENDENT_VARIABLES + [
    # name_log_return_vol_variable(variable, rolling_window_return, rolling_window_vol)
]
diff_in_diff_df = reg_panel.loc[:, ["Token", "Date"] + dvs + indvs]


def lead_lag(date: float, join_time_list: list[float]) -> float:
    # if join_time_list is not NaN
    if join_time_list is not np.nan:
        return date - min(join_time_list, key=lambda d: abs(d - date))
    else:
        return np.nan


# lead_lag is the time difference between the date of the observation and the date of the nearest treatment from join_time_list
diff_in_diff_df["lead_lag"] = reg_panel.apply(
    lambda row: lead_lag(row["Date"], row["join_time_list"]), axis=1
)

diff_in_diff_df["lead_lag"] = reg_panel["Date"] - reg_panel["earliest_join_time"]

diff_in_diff_df["has_been_treated"] = diff_in_diff_df["lead_lag"] >= 0

for lead_lag_interval in [None, 7]:
    did_result = panel_event_regression(
        diff_in_diff_df=diff_in_diff_df,
        window=7 * 9,
        control_with_treated=False,
        lead_lag_interval=lead_lag_interval,
        reltime_dummy=RELTIME_DUMMY,
        dummy_prefix_sep=FACTOR_PREFIX,
        standard_beta=False,
        panel_index_columns=(["Token", "Date"], [True, True]),
        robust=False,
        treatment_delay=0,
        dependent_variables=dvs,
        covariates=indvs,
    )

    # get index that contains RELTIME_DUMMY
    time_to_treat_cols = [k for k in did_result.index if RELTIME_DUMMY in k]

    if lead_lag_interval is None:
        did_result = did_result.rename(
            index={
                f"{RELTIME_DUMMY}{FACTOR_PREFIX}1": name_interaction_variable(
                    "is_treated_token", "after_treated_date"
                )
            }
        )
    did_result_latex = render_regress_table_latex(
        result_table=did_result,
        file_name=TABLE_PATH
        / f"slides_did_event_stack_{'leadlag' if lead_lag_interval else 'noleadlag'}",
    )

    if lead_lag_interval:
        # get all the rows with index in time_to_treat_cols, ignore items in time_to_treat_cols that are not in the index
        plot_df = did_result.loc[
            did_result.index.intersection(list(time_to_treat_cols)), :
        ]
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
            .applymap(lambda x: float(x.split("($")[1].split("$)")[0]))
            .astype(float)
        )

        x = plot_df["time_to_join"]
        # plot the result
        for k, v in did_result.loc["regressand"].items():
            plt.plot(x, plot_df_co[k], label=f"{'$'+ALL_NAMING_DICT[v]+'$' if v in ALL_NAMING_DICT else v}")  # type: ignore

            # plot the standard error band
            plt.fill_between(
                x,
                plot_df_co[k] - 1.96 * plot_df_se[k],  # type: ignore
                plot_df_co[k] + 1.96 * plot_df_se[k],  # type: ignore
                alpha=0.2,
            )
        plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left", borderaxespad=0.0)

        # plot verticle line at 0
        plt.axvline(x=0, color="black", linestyle="--")
        # plot horizontal line at 0
        plt.axhline(y=0, color="black", linestyle="--")
        # add x axis label
        plt.xlabel("Time to be included in any PLF (weeks)")
        # save pdf
        plt.savefig(
            FIGURE_PATH / f"did_event_stack_lead_lag.pdf",
            bbox_inches="tight",
        )
        plt.show()
        plt.close()
