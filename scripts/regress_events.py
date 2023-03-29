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

from environ.process.paneleventstudy import (
    interactionweighted_eventstudy,
    identifycontrols,
    genreltime,
    gencohort,
    gencalendartime_numerics,
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

reg_panel["treat"] = (reg_panel["Date"] >= reg_panel["join_compound_day"]).astype(float)

df = identifycontrols(data=reg_panel, event="treat", group="Token")
df = genreltime(
    data=df,
    group="Token",
    event="treat",
    reltime="reltime",
    calendartime="Date",
    check_balance=False,
)

df = gencohort(
    data=df,
    group="Token",
    event="treat",
    cohort="cohort",
    calendartime="Date",
    check_balance=False,
)


df = gencalendartime_numerics(
    data=df,
    group="Token",
    event="treat",
    calendartime="Date",
    calendartime_numerics="ct",
)


est_iw = interactionweighted_eventstudy(
    data=df,
    outcome="avg_eigenvector_centrality",
    event="treat",
    cohort="cohort",
    group="Token",
    reltime="reltime",
    calendartime="ct",
    covariates=[],
    check_balance=False,
)

TIME_TO_JOIN = "time_to_join"
FACTOR_PREFIX = "_"

reg_panel[TIME_TO_JOIN] = (
    reg_panel["Date"] - reg_panel["join_compound_day"]
).dt.days.map(
    lambda x: int(x // 1) if (not math.isnan(x) and -28 <= x <= 28) else -99999
)


# add time_to_join as a categorical variable
reg_panel_with_dummies = pd.get_dummies(
    reg_panel, columns=[TIME_TO_JOIN], prefix_sep=FACTOR_PREFIX
).drop(columns=[f"{TIME_TO_JOIN}{FACTOR_PREFIX}-99999"])

time_to_treat_cols = reg_panel_with_dummies.columns[
    reg_panel_with_dummies.columns.str.contains(TIME_TO_JOIN + FACTOR_PREFIX)
]


did_reg_panel = reg_panel[
    ["Token", "Date", "join_compound_day", TIME_TO_JOIN] + DEPENDENT_VARIABLES
].merge(
    reg_panel_with_dummies[list(time_to_treat_cols)],
    left_index=True,
    right_index=True,
)


outcome = interactionweighted_eventstudy(
    data=did_reg_panel,
    outcome="avg_eigenvector_centrality",
    event="has_joined",
    cohort="join_compound_day",
    group="Token",
    reltime=TIME_TO_JOIN,
    calendartime="Date",
    covariates=[],
    check_balance=False,
)
