"""
Util to merge data from different sources
"""

import glob

import pandas as pd


def load_data(
    panel_main: pd.DataFrame,
    data_path: str,
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
        merge_key (list[str], optional): List of columns to merge on. Defaults to ["Token", "Date"].
        merge_way (Literal["left", "outer"], optional): Merge way. Defaults to "left".

    Returns:
        pd.DataFrame: Merged dataframe
    """

    # get the list of files in a given path
    files_lst = glob.glob(data_path + "/*.csv")

    # a list to store the dataframes
    df_lst = []

    # loop through the list of files
    for file in files_lst:
        # load in the data
        df_data = pd.read_csv(file)

        # add the date column
        df_data["Date"] = file.split("_")[-1].split(".")[0]

        # append the data to the list
        df_lst.append(df_data)

    # merge the dataframes together
    df_merged = pd.concat(df_lst)

    # rename the columns
    df_merged = df_merged.rename(columns=rename_dict)

    # keep the columns that are needed
    merge_key = kwargs.pop("merge_key", ["Token", "Date"])
    df_merged = df_merged[merge_key + data_col]

    # merge the data with the main panel
    merge_way = kwargs.pop("merge_way", "outer")
    panel_main = panel_main.merge(df_merged, on=merge_key, how=merge_way)

    return panel_main
