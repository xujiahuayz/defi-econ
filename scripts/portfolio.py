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
