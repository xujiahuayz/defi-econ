"""
Util to merge data from different sources
"""

import glob
from pathlib import Path

import pandas as pd


def load_data(
    panel_main: pd.DataFrame,
    data_path: str | Path,
    data_col: list[str],
    rename_dict: dict[str, str],
    **kwargs,
) -> pd.DataFrame:
    """
    Function to load in the data and merge them together

    Args:
        panel_main (pd.DataFrame): Main panel to merge the data with
        data_path (str): Path to the data
        rename_dict (dict[str, str]): Dictionary to rename the columns
        date_col (list[str]): List of columns to keep

    Returns:
        pd.DataFrame: Merged dataframe
    """

    df_merged = pd.DataFrame()
    for file_name in glob.glob("*.csv", root_dir=data_path):
        df_data = pd.read_csv(str(data_path) + file_name)
        df_data["Date"] = file_name.split("_")[-1].split(".")[0]
        df_merged = pd.concat([df_merged, df_data])

    df_merged.rename(columns=rename_dict, inplace=True)

    return panel_main.merge(df_merged[data_col], **kwargs)


def load_data_herf(
    herf_main: pd.DataFrame,
    data_path: str | Path,
    data_col: str,
    **kwargs,
) -> pd.DataFrame:
    """
    Function to load in the data, calculate the herfindahl index and merge them together
    """

    df_merged = []
    for file_name in glob.glob("*.csv", root_dir=data_path):
        df_data = pd.read_csv(str(data_path) + file_name, index_col=None, header=0)
        df_merged.append(
            (file_name.split("_")[-1].split(".")[0], (df_data[data_col] ** 2).sum())
        )

    df_merged = pd.DataFrame(df_merged, columns=["Date", f"herfindahl_{data_col}"])

    return herf_main.merge(df_merged, **kwargs)
