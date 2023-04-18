"""
Functions to prepare the main token-date panel.
"""

import pandas as pd
from tqdm import tqdm

from environ.constants import (
    PANEL_VAR_INFO,
    SAMPLE_PERIOD,
    PROCESSED_DATA_PATH,
    DEPENDENT_VARIABLES,
)
from environ.process.market.dollar_exchange_rate import dollar_df
from environ.process.market.prepare_market_data import market_data
from environ.process.market.stable_share import stable_share_df
from environ.tabulate.panel.panel_generator import _merge_boom_bust
from environ.process.market.market_cap import mcap
from environ.utils.data_loader import load_data
from environ.utils.variable_constructer import (
    name_log_return_variable,
    share_variable_columns,
    log_return_panel,
    return_vol_panel,
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

    # calculate the share of the variables
    for var_name in tqdm(
        PANEL_VAR_INFO["share_var"],
        desc="Construct share variables",
    ):
        panel_main = share_variable_columns(
            data=panel_main,
            variable=var_name,
        )

    # calculate the log return
    panel_main = log_return_panel(
        data=panel_main,
        variable="dollar_exchange_rate",
        output_variable="log_return",
    )

    # calculate the volatility
    panel_main = return_vol_panel(
        data=panel_main,
        variable="log_return",
        output_variable="std",
        rolling_window_vol=30,
    )

    # construct the correlation variables
    for var_name, source_var in tqdm(
        PANEL_VAR_INFO["corr_var"].items(),
        desc="Construct correlation variables",
    ):
        panel_main[var_name] = (
            panel_main.groupby("Token")[name_log_return_variable(source_var, 1)]
            .rolling(30)
            .corr(panel_main["log_return"])
        )

    # merge boom bust cycles
    panel_main = _merge_boom_bust(panel_main)

    # fill the na values
    var_without_na = list(set(DEPENDENT_VARIABLES))
    panel_main[var_without_na] = panel_main[var_without_na].fillna(0)
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
