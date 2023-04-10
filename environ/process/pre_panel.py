"""
Functions to prepare the main token-date panel.
"""

import pandas as pd
from tqdm import tqdm

from environ.constants import PANEL_VAR_INFO
from environ.utils.data_loader import load_data


def construct_panel() -> pd.DataFrame:
    """
    Function to construct the main token-date panel
    """

    # create a blank panel with Date and Token as columns
    panel_main = pd.DataFrame(columns=["Date", "Token"])

    # iterate through the variables
    for _, var_info in tqdm(PANEL_VAR_INFO.items(), desc="Constructing main panel"):
        # load the data
        panel_main = load_data(
            panel_main=panel_main,
            data_path=var_info["data_path"],
            rename_dict=var_info["rename_dict"],
            data_col=var_info["data_col"],
            merge_key=var_info["merge_key"],
            merge_way=var_info["merge_way"],
        )

    return panel_main


if __name__ == "__main__":
    print(construct_panel())
    pass
