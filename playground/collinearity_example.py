# create a test dummy panel data to test colinearity

import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

from statsmodels.api import OLS

# create data
np.random.seed(123)

entities = [
    "a",
    "b",
    "c",
    "d",
    "e",
]
no_days = 3
df = pd.DataFrame(
    {
        "day": np.repeat(range(no_days), len(entities)),
        "entity": entities * no_days,
        "dv": np.random.normal(size=len(entities) * no_days),
        "treatday": ([1] + [9999] * (len(entities) - 1)) * no_days,
    }
)

df["leadlag"] = df["day"] - df["treatday"]

# create dummy variables with leadlag
dummy_vars_days = pd.get_dummies(df["leadlag"]).rename(
    columns={-1: "minus_1", 0: "zero", 1: "plus_1"}
)

# add the dummy variables to the data
df = pd.concat([df, dummy_vars_days[["minus_1", "zero", "plus_1"]]], axis=1)

df["after_treat"] = (df["day"] >= 1).astype(int)

# try with OLS

# create day dummies
dummy_vars_days = pd.get_dummies(df["day"]).rename(
    columns={0: "day_0", 1: "day_1", 2: "day_2"}
)

dummy_vars_entities = pd.get_dummies(df["entity"], prefix="", prefix_sep="")

# add the dummy variables to the data
processed_panel = pd.concat(
    [df, dummy_vars_days[["day_0", "day_1", "day_2"]], dummy_vars_entities], axis=1
)

model = OLS(
    processed_panel["dv"],
    processed_panel[
        ["minus_1", "zero", "plus_1"] + entities + ["day_0", "day_1", "day_2"]
    ],
)
ols_results = model.fit().summary()


# set index
processed_panel = df.set_index(["entity", "day"])


# run fixed effect regression with sm with entity dummies
model = PanelOLS(
    processed_panel["dv"],
    processed_panel[["minus_1", "zero", "plus_1"]],
    entity_effects=True,
    time_effects=False,
    check_rank=False,
    drop_absorbed=True,
)

pols_results = model.fit()
