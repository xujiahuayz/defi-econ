"""
Functions to prepare the herfin date series.
"""

import pandas as pd
from tqdm import tqdm

from environ.constants import HERFIN_VAR_INFO
from environ.utils.data_loader import load_data_herf


def construct_herfin(merge_on: list[str]) -> pd.DataFrame:
    """
    Function to construct the herfin date series.
    """

    # create a blank panel with Date as columns
    panel_main = pd.DataFrame(columns=merge_on)

    # iterate through the variables
    for var_info in tqdm(HERFIN_VAR_INFO, desc="Constructing herfin series"):
        # load the data
        panel_main = load_data_herf(
            herf_main=panel_main,
            data_path=var_info["data_path"],
            data_col=var_info["data_col"],
            how="outer",
            on=merge_on,
        )

    return panel_main


if __name__ == "__main__":
    print(construct_herfin(merge_on=["Date"]))
