import pandas as pd
from environ.constants import PROCESSED_DATA_PATH, DEPENDENT_VARIABLES
from environ.utils.variable_constructer import ma_variable_columns


# load the regression panel dataset
reg_panel = pd.read_pickle(
    PROCESSED_DATA_PATH / "panel_main.pickle.zip", compression="zip"
)
