"""
Script to render the asset pricing table
"""

import pandas as pd

from environ.constants import (
    DEPENDENT_VARIABLES,
    PROCESSED_DATA_PATH,
    STABLE_DICT,
    TABLE_PATH,
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
            print(f"Processing {panel_info} {dominance} {frequency}")

            df_ap = asset_pricing(
                df_panel,
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

# Create a dictionary to store subtables
subtables = {}

# Group the DataFrame by panel, dominance, and frequency
grouped = df_tab.groupby(["panel", "dominance", "frequency"])

# Generate subtables for each group
for (panel, dominance, frequency), group in grouped:
    subtables[(panel, dominance, frequency)] = group.drop(
        ["panel", "dominance", "frequency"], axis=1
    )

# Concatenate subtables vertically into one table
table = pd.concat(subtables.values(), axis=1, keys=subtables.keys())

# Transpose the table
table = table.swapaxes(0, 1)

# Save the table in latex format
table.to_latex(
    TABLE_PATH / "asset_pricing.tex",
    column_format="rcl",
    escape=False,
    header=False,
)

# Save the table in pickle format
table.to_pickle(PROCESSED_DATA_PATH / "asset_pricing.pickle.zip", compression="zip")
