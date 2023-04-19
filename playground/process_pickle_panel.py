import numpy as np
import pandas as pd

from environ.constants import PROCESSED_DATA_PATH
from environ.utils.variable_constructer import name_log_return_variable

reg_panel = pd.read_pickle(
    PROCESSED_DATA_PATH / "panel_main.pickle.zip", compression="zip"
)

var = "dollar_exchange_rate"
rolling_window_return = 1
variable_log_return = name_log_return_variable(var, rolling_window_return)
grouped_data = reg_panel.groupby(var)
# fill the missing values with the previous value with linear interpolation
# add this to reg_panel
reg_panel[var] = grouped_data[var].fillna(method="ffill")
# impute all na with the previous value
reg_panel[var] = reg_panel[var].replace(0, np.nan).interpolate(method="linear")
reg_panel[variable_log_return] = np.log(
    reg_panel[var] / reg_panel[var].shift(rolling_window_return)
)

grouped_reg_panel = reg_panel.groupby("Token")

for k, w in {
    "corr_gas": "gas_price_usd",
    "corr_eth": "ether_price_usd",
    "corr_sp": "S&P",
}.items():
    for group in grouped_reg_panel:
        token, group_data = group

        price_log_return = name_log_return_variable(w, rolling_window_return)

        corr_gas = (
            group_data[price_log_return]
            .rolling(30)
            .corr(group_data[variable_log_return])
        )

        # Set the 'corr_gas' values in the 'reg_panel' DataFrame using the indices of the 'group_data' DataFrame
        reg_panel.loc[corr_gas.index, k] = corr_gas

reg_panel.to_pickle(PROCESSED_DATA_PATH / "panel_main.pickle.zip", compression="zip")
