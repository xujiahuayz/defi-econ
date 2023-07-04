"""
Script to render the asset pricing table
"""

import pandas as pd

from environ.constants import (
    PROCESSED_DATA_PATH,
    TABLE_PATH,
    DEPENDENT_VARIABLES,
    STABLE_DICT,
)
from environ.process.asset_pricing.double_sorting import asset_pricing

# load the regression panel dataset
reg_panel = pd.read_pickle(
    PROCESSED_DATA_PATH / "panel_main.pickle.zip", compression="zip"
)

# table to store the results
df_tab = pd.DataFrame()

# stable non-stable info dict
stable_nonstable_info = {
    "stablecoin": reg_panel[reg_panel["Token"].isin(STABLE_DICT.keys())],
    "non-stablecoin": reg_panel[~reg_panel["Token"].isin(STABLE_DICT.keys())],
}

for panel_info, df_panel in stable_nonstable_info.items():
    for dominance in DEPENDENT_VARIABLES + ["ret"]:
        for frequency in [14, 30]:
            df_ap = asset_pricing(
                reg_panel,
                dominance,
                3,
                frequency,
            )

        # add the dominance and frequency
        df_ap["dominance"] = dominance
        df_ap["frequency"] = frequency
        df_ap["panel"] = panel_info

        # append to the table
        df_tab = pd.concat([df_tab, df_ap], axis=0)

# transpose the table
df_tab = df_tab.set_index(["dominance", "frequency"]).T

# save the table in latex format
df_tab.to_latex(TABLE_PATH / "asset_pricing.tex", escape=False)
