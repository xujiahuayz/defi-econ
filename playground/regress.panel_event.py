from typing import List, Optional, Tuple
import pandas as pd
from linearmodels.panel import PanelOLS
import numpy as np

# get the regression panel dataset from pickled file
import math
import re

import pandas as pd
from matplotlib import pyplot as plt

from environ.constants import (
    ALL_NAMING_DICT,
    COMPOUND_DEPLOYMENT_DATE,
    DEPENDENT_VARIABLES,
    SAMPLE_PERIOD,
    DATA_PATH,
)
from environ.tabulate.render_regression import (
    construct_regress_vars,
    render_regress_table,
    render_regress_table_latex,
)

from environ.process.paneleventstudy import (
    interactionweighted_eventstudy,
    identifycontrols,
    genreltime,
    gencohort,
    gencalendartime_numerics,
)

reg_panel = pd.read_pickle(DATA_PATH / "reg_panel.pkl")

compound_date = pd.DataFrame(
    {
        "Token": v["Token"] if v["Token"] != "ETH" else "WETH",
        "join_compound_time": pd.to_datetime(v["Date"].split(" ")[0]),
    }
    for v in COMPOUND_DEPLOYMENT_DATE
)

data = reg_panel.merge(compound_date, on="Token", how="left")[
    ["Token", "Date", "Volume_share", "join_compound_time"]
]

touse = data["Token"].notna().all(axis=1)

dep_var = "dependent_variable_name"  # Replace this with the actual name of the dependent variable
rel_time_vars = [
    "rel_time_var1",
    "rel_time_var2",
    ...,
]  # Replace with the actual list of relative time variables
