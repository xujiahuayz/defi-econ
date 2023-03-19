# get the regression panel dataset from pickled file
import pandas as pd

from environ.constants import SAMPLE_PERIOD, TABLE_PATH
from environ.tabulate.render_regression import (
    construct_regress_vars,
    render_regress_table,
    render_regress_table_latex,
)
from environ.utils.variable_constructer import (
    lag_variable,
    name_interaction_variable,
    name_lag_variable,
)

reg_panel = pd.read_pickle(TABLE_PATH / "reg_panel.pkl")
