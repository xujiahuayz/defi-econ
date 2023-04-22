import pandas as pd
from environ.constants import PROCESSED_DATA_PATH, DEPENDENT_VARIABLES
from environ.utils.variable_constructer import ma_variable_columns


# load the regression panel dataset
reg_panel = pd.read_pickle(
    PROCESSED_DATA_PATH / "panel_main.pickle.zip", compression="zip"
)

reg_panel = ma_variable_columns(
    reg_panel,
    DEPENDENT_VARIABLES,
    time_variable="Date",
    entity_variable="Token",
    rolling_window_ma=30,
)

#  find medium value of all tokens' 30 day moving average for each day

reg_panel[[f"{var}_median" for var in DEPENDENT_VARIABLES]] = reg_panel.groupby("Date")[
    DEPENDENT_VARIABLES
].transform("median")
