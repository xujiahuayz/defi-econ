"""
Tabulate the summary statistics of the data.
"""

import pandas as pd

from environ.constants import DEPENDENT_VARIABLES, SAMPLE_PERIOD, TABLE_PATH
from environ.tabulate.render_summary import render_summary_table_latex

# get the regressuib panel dataset from pickle file
regression_panel = pd.read_pickle(TABLE_PATH / "reg_panel.pkl")
regression_panel[DEPENDENT_VARIABLES] = regression_panel[DEPENDENT_VARIABLES].fillna(0)
# for all value < 0 for DEPENDENT_VARIABLES, set to 0
# TODO: check why this is necessary -- why some eigenvector centrality values are negative?
regression_panel[DEPENDENT_VARIABLES] = regression_panel[DEPENDENT_VARIABLES].clip(
    lower=0
)

# generate the summary table
res = render_summary_table_latex(
    file_name="dominance_vars",
    data=regression_panel[
        (regression_panel["Date"] >= SAMPLE_PERIOD[0])
        & (regression_panel["Date"] <= SAMPLE_PERIOD[1])
    ],
    sum_column=DEPENDENT_VARIABLES,
)
