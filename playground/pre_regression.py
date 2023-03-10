"""
run regression on the panel data
"""

import re
import pandas as pd
from environ.constants import TABLE_PATH, NAMING_DICT_OLD
from os import path


from environ.tabulate.panel.panel_generator import _merge_boom_bust

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


reg_panel = reg_panel.set_index(["Token", "Date"])

# pickle the reg_panel
reg_panel.to_pickle(path.join(TABLE_PATH, "reg_panel.pkl"))
