import numpy as np
import pandas as pd
from tqdm import tqdm

from environ.constants import DEPENDENT_VARIABLES, PANEL_VAR_INFO, PROCESSED_DATA_PATH
from environ.utils.variable_constructer import (
    name_log_return_variable,
    name_log_return_vol_variable,
    return_vol,
    share_variable_columns,
)

reg_panel = pd.read_pickle(
    PROCESSED_DATA_PATH / "panel_main.pickle.zip", compression="zip"
)

# fill the na values
# NOTE: NA must be processed BEFORE constructing the share variables
var_without_na = PANEL_VAR_INFO["share_var"] + ["stableshare", "Supply_share"]

reg_panel[var_without_na] = reg_panel[var_without_na].fillna(0)
reg_panel[var_without_na] = reg_panel[var_without_na].clip(lower=0)


reg_panel["volume_ultimate"] = (
    reg_panel["vol_in_full_len"] + reg_panel["vol_out_full_len"]
)


for var_name in tqdm(
    PANEL_VAR_INFO["share_var"],
    desc="Construct share variables",
):
    reg_panel = share_variable_columns(
        data=reg_panel,
        variable=var_name,
    )


reg_panel[DEPENDENT_VARIABLES] = reg_panel[DEPENDENT_VARIABLES].fillna(0)
reg_panel[DEPENDENT_VARIABLES] = reg_panel[DEPENDENT_VARIABLES].clip(lower=0)


var = "dollar_exchange_rate"
rolling_window_return = 1
rolling_window_std = 30
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

reg_panel = return_vol(
    data=reg_panel,
    variable=var,
    rolling_window_return=rolling_window_return,
    rolling_window_vol=rolling_window_std,
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
            .rolling(rolling_window_std)
            .corr(group_data[variable_log_return])
        )

        # Set the 'corr_gas' values in the 'reg_panel' DataFrame using the indices of the 'group_data' DataFrame
        reg_panel.loc[corr_gas.index, k] = corr_gas


reg_panel["std"] = reg_panel[
    name_log_return_vol_variable("dollar_exchange_rate", 1, 30)
]  # * np.sqrt(7 / 30)

reg_panel.to_pickle(PROCESSED_DATA_PATH / "panel_main.pickle.zip", compression="zip")

# check na values of dependent variables
reg_panel[DEPENDENT_VARIABLES].isna().sum()
