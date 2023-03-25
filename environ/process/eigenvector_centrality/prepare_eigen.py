"""
Script to generate the eigenvector centrality for atomic swaps.
"""

from pathlib import Path
import glob
from typing import Literal

import pandas as pd

from environ.constants import BETWEENNESS_DATA_PATH


def get_eigencent(uni_ver: Literal["v2", "v3", "v2v3"] = "v2") -> None:
    """
    Calculate the eigenvector centrality for atomic swaps.
    """

    # get the list of files
    path = str(Path(BETWEENNESS_DATA_PATH) / "swap_route")
    file_lst = glob.glob(path + "/*.csv")

    # isolate the file with specific version
    file_name = [
        file_name for file_name in file_lst if uni_ver == file_name.split("_")[-2]
    ]

    print(file_name)


if __name__ == "__main__":
    get_eigencent()
