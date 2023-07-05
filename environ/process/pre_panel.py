"""
Functions to prepare the main token-date panel.
"""

import numpy as np
import pandas as pd
from tqdm import tqdm

from environ.constants import (
    DEPENDENT_VARIABLES,
    PANEL_VAR_INFO,
    PROCESSED_DATA_PATH,
    SAMPLE_PERIOD,
)
from environ.process.market.dollar_exchange_rate import dollar_df
from environ.process.market.market_cap import mcap
from environ.process.market.prepare_market_data import market_data
from environ.process.market.stable_share import stable_share_df
from environ.tabulate.panel.panel_generator import _merge_boom_bust
from environ.utils.data_loader import load_data
from environ.utils.variable_constructer import (
    name_log_return_variable,
    return_vol,
    share_variable_columns,
)


def construct_panel(merge_on: list[str]) -> pd.DataFrame:
    """
    Function to construct the main token-date panel
    """

    # create a blank panel with Date and Token as columns
    panel_main = pd.DataFrame(columns=merge_on)

    # iterate through the variables
    for var_info in tqdm(PANEL_VAR_INFO["panel_var"], desc="Merge panel data"):
        # load the data
        panel_main = load_data(
            panel_main=panel_main,
            data_path=var_info["data_path"],
            data_col=list(set(var_info["data_col"] + merge_on)),
            rename_dict=var_info["rename_dict"],
            how="outer",
            on=merge_on,
        )

    # calculate the volume_ultimate
    panel_main["volume_ultimate"] = (
        panel_main["vol_in_full_len"] + panel_main["vol_out_full_len"]
    )

    # clean up the anomalies of AAVE
    panel_main.loc[
        ((panel_main["Date"] == "2020-10-07") | (panel_main["Date"] == "2020-10-08"))
        & (panel_main["Token"] == "AAVE"),
        "TVL",
    ] = panel_main.loc[
        (panel_main["Date"] == "2020-10-06") & (panel_main["Token"] == "AAVE"),
        "TVL",
    ].values[
        0
    ]

    # merge the other data such as dollar exchange rate
    for df_name in [dollar_df, stable_share_df, mcap]:
        panel_main = panel_main.merge(
            df_name,
            how="left",
            on=merge_on,
        )

    # merge the market data
    panel_main = panel_main.merge(
        market_data,
        how="left",
        on=["Date"],
    )

    # fill the na values
    # NOTE: NA must be processed BEFORE constructing the share variables
    var_without_na = PANEL_VAR_INFO["share_var"] + [
        "stableshare",
        "Supply_share",
        "borrow_rate",
        "supply_rates",
    ]

    panel_main[var_without_na] = panel_main[var_without_na].fillna(0)
    panel_main[var_without_na] = panel_main[var_without_na].clip(lower=0)

    # calculate the share of the variables
    for var_name in tqdm(
        PANEL_VAR_INFO["share_var"],
        desc="Construct share variables",
    ):
        panel_main = share_variable_columns(
            data=panel_main,
            variable=var_name,
        )

    var = "dollar_exchange_rate"
    rolling_window_return = 1
    rolling_window_std = 30
    variable_log_return = name_log_return_variable(var, rolling_window_return)

    # grouped_data = panel_main.groupby(var)
    # # fill the missing values with the previous value with linear interpolation
    # # add this to reg_panel
    # panel_main[var] = grouped_data[var].fillna(method="ffill")
    # # impute all na with the previous value
    # panel_main[var] = panel_main[var].replace(0, np.nan).interpolate(method="linear")

    # fill the missing values with the previous value with linear interpolation
    panel_main.sort_values(by=["Token", "Date"], inplace=True)
    panel_main[var] = panel_main[var].replace(0, np.nan)
    panel_main[var] = panel_main.groupby("Token")[var].fillna(method="ffill")

    panel_main[variable_log_return] = np.log(
        panel_main[var] / panel_main[var].shift(rolling_window_return)
    )

    panel_main = return_vol(
        data=panel_main,
        variable=var,
        rolling_window_return=rolling_window_return,
        rolling_window_vol=rolling_window_std,
    )

    grouped_reg_panel = panel_main.groupby("Token")

    for k, w in {
        "corr_gas": "gas_price_usd",
        "corr_eth": "ether_price_usd",
        "corr_sp": "S&P",
    }.items():
        for group in grouped_reg_panel:
            _, group_data = group

            price_log_return = name_log_return_variable(w, rolling_window_return)

            corr_gas = (
                group_data[price_log_return]
                .rolling(rolling_window_std)
                .corr(group_data[variable_log_return])
            )

            # Set the 'corr_gas' values in the 'reg_panel' DataFrame
            # using the indices of the 'group_data' DataFrame
            panel_main.loc[corr_gas.index, k] = corr_gas

    # merge boom bust cycles
    panel_main = _merge_boom_bust(panel_main)

    # fill the na values
    panel_main[DEPENDENT_VARIABLES] = panel_main[DEPENDENT_VARIABLES].fillna(0)
    panel_main[DEPENDENT_VARIABLES] = panel_main[DEPENDENT_VARIABLES].clip(lower=0)

    return panel_main.loc[
        (panel_main["Date"] >= SAMPLE_PERIOD[0])
        & (panel_main["Date"] <= SAMPLE_PERIOD[1])
    ]


if __name__ == "__main__":
    # save the panel as a zip pickle
    construct_panel(merge_on=["Token", "Date"]).to_pickle(
        PROCESSED_DATA_PATH / "panel_main.pickle.zip", compression="zip"
    )
