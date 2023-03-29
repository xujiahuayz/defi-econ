# get the regression panel dataset from pickled file
import math
import re

import pandas as pd
from matplotlib import pyplot as plt

from environ.constants import (
    ALL_NAMING_DICT,
    COMPOUND_DEPLOYMENT_DATE,
    DEPENDENT_VARIABLES,
    SAMPLE_PERIOD,
    TABLE_PATH,
)
from environ.tabulate.render_regression import (
    construct_regress_vars,
    render_regress_table,
    render_regress_table_latex,
)

reg_panel = pd.read_pickle(TABLE_PATH / "reg_panel.pkl")

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

reg_panel[TIME_TO_JOIN] = (
    reg_panel["Date"] - reg_panel["join_compound_day"]
).dt.days.map(
    lambda x: str(int(x // 1)) if (not math.isnan(x) and -28 <= x <= 28) else "NA"
)

# add time_to_join as a categorical variable
reg_panel = pd.get_dummies(
    reg_panel, columns=[TIME_TO_JOIN], prefix_sep=FACTOR_PREFIX
).drop(columns=[f"{TIME_TO_JOIN}{FACTOR_PREFIX}NA"])

time_to_treat_cols = reg_panel.columns[
    reg_panel.columns.str.contains(TIME_TO_JOIN + FACTOR_PREFIX)
]

iv_chunk_list_unlagged = [[list(time_to_treat_cols)]]

reg_combi = construct_regress_vars(
    dependent_variables=DEPENDENT_VARIABLES,
    iv_chunk_list=iv_chunk_list_unlagged,
    lag_iv=False,
    with_lag_dv=False,
    without_lag_dv=False,
)

# restrict to SAMPE_PERIOD
reg_panel = reg_panel[
    (reg_panel["Date"] >= SAMPLE_PERIOD[0]) & (reg_panel["Date"] <= SAMPLE_PERIOD[1])
]


did_result = render_regress_table(
    reg_panel=reg_panel,
    reg_combi=reg_combi,
    standard_beta=False,
    panel_index_columns=(["Token", "Date"], [True, True]),
    robust=False,
)

did_result_latex = render_regress_table_latex(
    result_table=did_result,
    file_name="DID_time_to_join",
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
    # if k == plot_df.columns[0]:
    #     break
# place legend outside the plot
plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left", borderaxespad=0.0)

# plot verticle line at 0
plt.axvline(x=0, color="black", linestyle="--")
