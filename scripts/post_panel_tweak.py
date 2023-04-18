"""
Script to get the std
"""

import pandas as pd
from environ.constants import PROCESSED_DATA_PATH


# load the regression panel dataset
reg_panel = pd.read_pickle(
    PROCESSED_DATA_PATH / "panel_main.pickle.zip", compression="zip"
)


print(reg_panel.keys())
