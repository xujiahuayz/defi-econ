"""
Script to implement asset pricing using dominance as indicator
"""

import pandas as pd
from environ.process.asset_pricing.double_sorting import (
    stable_nonstable_split,
    asset_pricing,
)
from environ.constants import (
    PROCESSED_DATA_PATH,
    FIGURE_PATH,
    DEPENDENT_VARIABLES,
)


# load the regression panel dataset
reg_panel = pd.read_pickle(
    PROCESSED_DATA_PATH / "panel_main.pickle.zip", compression="zip"
)

# split the dataframe into stablecoin and non stablecoin
df_panel_stablecoin, df_panel_nonstablecoin = stable_nonstable_split(reg_panel)

# stable non-stable info dict
stable_nonstable_info = {
    "stablecoin": df_panel_stablecoin,
    "nonstablecoin": df_panel_nonstablecoin,
}

# iterate through the dominance
for panel_info, df_panel in stable_nonstable_info.items():
    for dominance in DEPENDENT_VARIABLES:
        for frequency in [14, 30]:
            asset_pricing(
                df_panel,
                str(FIGURE_PATH / f"{panel_info}_{dominance}_{frequency}.pdf"),
                dominance,
                "supply_rates",
                0.1,
                frequency,
            )
