import numpy as np
import pandas as pd

from environ.constants import PROCESSED_DATA_PATH
from environ.utils.variable_constructer import name_log_return_variable

reg_panel = pd.read_pickle(
    PROCESSED_DATA_PATH / "panel_main.pickle.zip", compression="zip"
)

var = "dollar_exchange_rate"
rolling_window_return = 1
grouped_data = reg_panel.groupby(var)
# fill the missing values with the previous value with linear interpolation
# add this to reg_panel
# TODO: add this to pkl
reg_panel[var] = grouped_data[var].fillna(method="ffill")
# impute all na with the previous value
reg_panel[var] = reg_panel[var].replace(0, np.nan).interpolate(method="linear")
reg_panel[name_log_return_variable(var, rolling_window_return)] = np.log(
    reg_panel[var] / reg_panel[var].shift(rolling_window_return)
)

# calculate the correlation between the gas price and the exchange rate log return

reg_panel["corr_gas"] = (
    reg_panel.groupby("Token")[
        name_log_return_variable("gas_price_usd", rolling_window_return)
    ]
    .rolling(30)
    .corr(reg_panel[name_log_return_variable(var, rolling_window_return)])
)
