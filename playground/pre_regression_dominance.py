"""
run regression on the panel data
"""

import re
from os import path

import pandas as pd

from environ.constants import NAMING_DICT_OLD, TABLE_PATH
from environ.tabulate.panel.panel_generator import _merge_boom_bust
from environ.process.market.prepare_market_data import market_data
from environ.utils.variable_constructer import (
    name_log_return_variable,
)

# read csv file as pd.DataFrame where Date column is parsed as datetime
reg_panel = pd.read_csv(
    path.join(TABLE_PATH, "regression_panel.csv"), parse_dates=["Date"]
)


# TODO: the below would not be necessary if the column names were not changed
# in the first place - need to revert column names to original in respective scripts
# remove non-alphanumeric characters from column names
reg_panel.columns = reg_panel.columns.str.replace(r"\W", "")
NAMING_DICT_reverted = {re.sub(r"\W+", "", v): k for k, v in NAMING_DICT_OLD.items()}
reg_panel.rename(columns=NAMING_DICT_reverted, inplace=True)

# get gas price from reg_panel


# merge market data
reg_panel = reg_panel.merge(market_data, on=["Date"], how="left")
# calculate rolling 30-day correlation between daily returns Token and daily gas_price return per Token level

# gas_price_old = reg_panel[["Date", "GasPrice"]].drop_duplicates(subset=["Date"])


reg_panel["corr_gas"] = reg_panel.groupby("Token")[
    name_log_return_variable("gas_price_usd", 1)
].transform(lambda x: x.rolling(30).corr(reg_panel["dollar_exchange_rate"]))

reg_panel["corr_eth"] = reg_panel.groupby("Token")[
    name_log_return_variable("ether_price_usd", 1)
].transform(lambda x: x.rolling(30).corr(reg_panel["dollar_exchange_rate"]))


reg_panel["corr_sp"] = reg_panel.groupby("Token")[
    name_log_return_variable("S&P", 1)
].transform(lambda x: x.rolling(30).corr(reg_panel["dollar_exchange_rate"]))


# merge boom bust cycles
reg_panel = _merge_boom_bust(reg_panel)
# reg_panel = _merge_fiat_underlying(
#     reg_panel, new_price_col_name="exchange_to_underlying"
# )
# reg_panel = _merge_depeg_persistancy(reg_panel, price_col_name="exchange_to_underlying")
# reg_panel = _merge_pegging(reg_panel, price_col_name="exchange_to_underlying")


reg_panel = reg_panel.set_index(["Token", "Date"])


# pickle the reg_panel
reg_panel.to_pickle(path.join(TABLE_PATH, "reg_panel.pkl"))
