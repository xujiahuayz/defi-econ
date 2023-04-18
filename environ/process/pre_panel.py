"""
Functions to prepare the main token-date panel.
"""

import pandas as pd
from tqdm import tqdm

from environ.constants import PANEL_VAR_INFO
from environ.process.market.prepare_market_data import market_data
from environ.utils.data_loader import load_data
from environ.utils.variable_constructer import name_log_return_variable
from environ.process.market.dollar_exchange_rate import dollar_df


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

    # merge the dollar exchange rate
    panel_main = panel_main.merge(
        dollar_df,
        how="left",
        on=merge_on,
    )

    # merge the market data
    panel_main = panel_main.merge(
        market_data,
        how="left",
        on=["Date"],
    )

    # construct the correlation variables
    for var_name, source_var in tqdm(
        PANEL_VAR_INFO["corr_var"].items(),
        desc="Construct correlation variables",
    ):
        panel_main[var_name] = panel_main.groupby("Token")[
            name_log_return_variable(source_var, 1)
        ].transform(lambda x: x.rolling(30).corr(panel_main["dollar_exchange_rate"]))

    print(panel_main)

    return panel_main


if __name__ == "__main__":
    # save the panel to the test folder
    construct_panel(merge_on=["Token", "Date"]).to_csv(
        "test/panel_main.csv", index=False
    )
