"""
Script to render the asset pricing table
"""

import pandas as pd

from environ.constants import PROCESSED_DATA_PATH, TABLE_PATH, DEPENDENT_VARIABLES
from environ.process.asset_pricing.double_sorting import asset_pricing

# load the regression panel dataset
reg_panel = pd.read_pickle(
    PROCESSED_DATA_PATH / "panel_main.pickle.zip", compression="zip"
)

for dominance in DEPENDENT_VARIABLES:
    for frequency in [14, 30]:
        asset_pricing(
            reg_panel,
            dominance,
            3,
            frequency,
        )
