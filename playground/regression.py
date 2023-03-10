# get the regression panel dataset from pickled file
from os import path

import pandas as pd
from environ.constants import TABLE_PATH
from linearmodels.panel import PanelOLS


reg_panel = pd.read_pickle(path.join(TABLE_PATH, "reg_panel.pkl"))

# Define the dependent variable
y = reg_panel["Supply_share"]

# Define the independent variables
X = reg_panel[["is_boom", "mcap_share"]]


# Run the fixed-effect regression
model = PanelOLS(y, X, entity_effects=True, drop_absorbed=True).fit()

# Print the summary of the regression results
print(model.summary)
