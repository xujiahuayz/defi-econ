"""
Functions to prepare the main token-date panel.
"""

import pandas as pd
from tqdm import tqdm

from environ.constants import PANEL_VAR_INFO
from environ.utils.data_loader import load_data


def construct_panel(merge_on: list[str]) -> pd.DataFrame:
    """
    Function to construct the main token-date panel
    """

    # create a blank panel with Date and Token as columns
    panel_main = pd.DataFrame(columns=merge_on)

    # iterate through the variables
    for var_info in tqdm(PANEL_VAR_INFO, desc="Constructing main panel"):
        # load the data
        panel_main = load_data(
            panel_main=panel_main,
            data_path=var_info["data_path"],
            data_col=list(set(var_info["data_col"] + merge_on)),
            rename_dict=var_info["rename_dict"],
            how="outer",
            on=merge_on,
        )

    return panel_main


if __name__ == "__main__":
    print(construct_panel(merge_on=["Token", "Date"]))
