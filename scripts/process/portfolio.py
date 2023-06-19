"""
Script to implement asset pricing using dominance as indicator
"""

import pandas as pd
from environ.process.asset_pricing.double_sorting import (
    asset_pricing,
)
from environ.constants import (
    PROCESSED_DATA_PATH,
    FIGURE_PATH,
    DEPENDENT_VARIABLES,
    STABLE_DICT,
)


# load the regression panel dataset
reg_panel = pd.read_pickle(
    PROCESSED_DATA_PATH / "panel_main.pickle.zip", compression="zip"
)

stable_nonstable_info = {
    "stablecoin": reg_panel[reg_panel["Token"].isin(STABLE_DICT.keys())],
    "nonstablecoin": reg_panel[~reg_panel["Token"].isin(STABLE_DICT.keys())],
}

# iterate through the dominance
for panel_info, df_panel in stable_nonstable_info.items():
    for dominance in DEPENDENT_VARIABLES:
        for frequency in [14, 30]:
            asset_pricing(
                df_panel,
                FIGURE_PATH / f"{panel_info}_{dominance}_{frequency}.pdf",
                dominance,
                "supply_rates",
                0.1,
                frequency,
            )
