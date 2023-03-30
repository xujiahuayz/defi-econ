# get the regression panel dataset from pickled file
import re

import pandas as pd
from matplotlib import pyplot as plt

from environ.constants import (
    ALL_NAMING_DICT,
    COMPOUND_DEPLOYMENT_DATE,
    DATA_PATH,
    DEPENDENT_VARIABLES,
)

from environ.tabulate.render_panel_event_regression import panel_event_regression
from environ.tabulate.render_regression import (
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

RELTIME_DUMMY = "rel_time"
FACTOR_PREFIX = "_"

all_added_dates = set(
    # take only the date in '2019-05-07 01:20:54' without time
    compound_date["join_compound_day"]
)

diff_in_diff_df = reg_panel.loc[:, ["Token", "Date"] + DEPENDENT_VARIABLES]

diff_in_diff_df["lead_lag"] = (
    reg_panel["Date"] - reg_panel["join_compound_day"]
).dt.days

diff_in_diff_df["has_been_treated"] = diff_in_diff_df["lead_lag"] >= 0

did_result = panel_event_regression(
    diff_in_diff_df=diff_in_diff_df,
    window=14,
    control_with_treated=True,
    lead_lag_interval=1,
    reltime_dummy=RELTIME_DUMMY,
    dummy_prefix_sep=FACTOR_PREFIX,
    standard_beta=False,
    panel_index_columns=(["Token", "Date"], [True, True]),
    robust=False,
)

# get index that contains RELTIME_DUMMY
time_to_treat_cols = [k for k in did_result.index if RELTIME_DUMMY in k]

did_result_latex = render_regress_table_latex(
    result_table=did_result,
    file_name=f"DID_test",
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
