"""
compare running panel OLS regression with linearmodels and statsmodels with dummies
"""
import time
from typing import Callable

import numpy as np
import pandas as pd
import statsmodels.api as sm
from linearmodels.panel import PanelOLS

# create data
np.random.seed(123)
nentity = 200
nperiods = 1000
nobs = nentity * nperiods
entity = np.repeat(np.arange(nentity), nperiods)
period = np.tile(np.arange(nperiods), nentity)
y = np.random.normal(size=nobs)
x1 = np.random.normal(size=nobs)
x2 = np.random.normal(size=nobs)
x3 = np.random.normal(size=nobs)
x4 = np.random.normal(size=nobs)

iv = ["x1", "x2", "x3", "x4"]
# create dataframe
df = pd.DataFrame(
    {
        "entity": entity,
        "period": period,
        "y": y,
        "x1": x1,
        "x2": x2,
        "x3": x3,
        "x4": x4,
    }
)


# timer decorator
def timer(func: Callable) -> Callable:
    """ """

    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        # round time to 6 decimals
        print(f"{func.__name__} took {round(end - start, 6)} seconds")
        return result

    return wrapper


@timer
def run_sm(df: pd.DataFrame):
    """ """
    # run fixed effect regression with sm with entity dummies
    # create entity dummies
    dummy_vars = pd.get_dummies(df["entity"])

    # add the dummy variables to the data
    processed_panel = pd.concat([df, dummy_vars], axis=1)

    model = sm.OLS(
        processed_panel["y"],
        processed_panel[iv + list(dummy_vars.columns)],
    ).fit()
    param_dict = [{v: f"{model.params[v]:.4f}"} for v in iv]
    # # print regression name, prameters of iv, and r2 to exactly 4 decimals like [{v: f'{model.params[v]:.4f}'} for v in iv]
    print(f"sm.OLS: {param_dict}, r^2: {model.rsquared:.4f}")
    return model


@timer
def run_panelOLS(df: pd.DataFrame):
    """ """
    # run fixed effect regression with linearmodels with panelOLS
    # set entity and period as index
    df = df.set_index(["entity", "period"])
    # run fixed effect regression with panelOLS
    model = PanelOLS(df["y"], df[iv], entity_effects=True).fit()
    param_dict = [{v: f"{model.params[v]:.4f}"} for v in iv]
    # print regression name, prameters of iv, and r2 to exactly 4 decimals
    print(f"PanelOLS: {param_dict}, r^2: {model.rsquared:.4f}")
    return model


if __name__ == "__main__":
    # run fixed effect regression with sm with entity dummies
    model1 = run_sm(df)

    # run fixed effect regression with linearmodels with panelOLS
    model2 = run_panelOLS(df)
