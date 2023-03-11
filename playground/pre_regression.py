"""
run regression on the panel data
"""

import re
from os import path

import pandas as pd

from environ.constants import NAMING_DICT_OLD, TABLE_PATH
from environ.tabulate.panel.depeg_persist import _merge_depeg_persistancy
from environ.tabulate.panel.fiat_stable_price import _merge_fiat_underlying
from environ.tabulate.panel.panel_generator import _merge_boom_bust
from environ.tabulate.panel.unit_of_acct import _merge_pegging

# read csv file as pd.DataFrame where Date column is parsed as datetime
reg_panel = pd.read_csv(
    path.join(TABLE_PATH, "regression_panel.csv"), parse_dates=["Date"]
)


# TODO: the below would not be necessary if the column names were not changed
# in the first place - need to revert column names to original in respective scripts
# remove non-alphanumeric characters from column names
reg_panel.columns = reg_panel.columns.str.replace(r"\W", "")
NAMING_DICT_reverted = {re.sub(r"\W+", "", v): k for k, v in NAMING_DICT_OLD.items()}
reg_panel = reg_panel.rename(columns=NAMING_DICT_reverted)

# merge boom bust cycles
reg_panel = _merge_boom_bust(reg_panel)
reg_panel = _merge_fiat_underlying(
    reg_panel, new_price_col_name="exchange_to_underlying"
)
reg_panel = _merge_depeg_persistancy(reg_panel, price_col_name="exchange_to_underlying")
reg_panel = _merge_pegging(reg_panel, price_col_name="exchange_to_underlying")


reg_panel = reg_panel.set_index(["Token", "Date"])

# pickle the reg_panel
reg_panel.to_pickle(path.join(TABLE_PATH, "reg_panel.pkl"))
