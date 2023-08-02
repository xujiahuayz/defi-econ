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

reg_panel["daily_supply_return"] = reg_panel["supply_rates"] / 365.2425

# stable non-stable info dict
stable_nonstable_info = {
    "stablecoin": reg_panel[reg_panel["Token"].isin(STABLE_DICT.keys())],
    "non-stablecoin": reg_panel[~reg_panel["Token"].isin(STABLE_DICT.keys())],
    "all": reg_panel,
}

for panel_info, df_panel in stable_nonstable_info.items():
    for dominance in DEPENDENT_VARIABLES + ["ret"]:
        for frequency in [14, 30]:
            print(f"Processing {panel_info} {dominance} {frequency}")

            df_ap = (
                asset_pricing(df_panel, [0.8], dominance, frequency, False)
                .set_index("Portfolios")
                .T
            )

            # save the results in latex keep the index and keep three decimal places
            df_ap.to_latex(
                TABLE_PATH / f"asset_pricing_{panel_info}_{dominance}_{frequency}.tex",
                index=True,
                escape=False,
                float_format="{:0.4f}".format,
            )
