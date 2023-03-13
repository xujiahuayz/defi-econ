# get the regression panel dataset from pickled file
from typing import Union

import pandas as pd

from environ.utils.variable_constructer import (
    lag_variable,
    name_boom_interact_var,
    name_lag_variable,
)

# Get the regression panel dataset from pickled file

# Lag all variable except the Date and Token
def add_lag_interact_vars(
    reg_panel: pd.DataFrame, variables: Union[list[str], None] = None
) -> pd.DataFrame:
    for variable in variables if variables else reg_panel.columns:
        # only proceed if the variable is numeric
        if reg_panel[variable].dtype in ("float64", "int64", "float32", "int32"):
            reg_panel = lag_variable(reg_panel, variable, "Date", "Token")
            lagged_var = name_lag_variable(variable)
            reg_panel[name_boom_interact_var(lagged_var)] = (
                reg_panel[lagged_var] * reg_panel["is_boom"]
            )
    return reg_panel
