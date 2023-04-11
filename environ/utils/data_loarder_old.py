"""
Utils related to data loading
"""

import glob
import pandas as pd


def _load_in_data_lst(
    file_root: str,
    filter_name: str = "",
) -> list:
    """
    Function to generate a list of dataframes from a given path
    """

    # get the list of files
    path = file_root
    file_lst = glob.glob(path + "/*.csv")

    # isolate the file with specific version
    file_name_lst = (
        [file_name for file_name in file_lst if filter_name == file_name.split("_")[-2]]
        if filter_name
        else file_lst
    )

    return file_name_lst


def _preprocessing(
    df_network: pd.DataFrame,
    edge_col: list[str],
    weight_col: list[str],
    dict2str: bool = False,
    exclude_special_route: bool = True,
    aggreate_weight: bool = False,
    convert_undirected: bool = False,
) -> pd.DataFrame:
    """
    Function to preprocess the network dataframe
    """

    if dict2str:
        # unwrap the dictionary {'symbol': 'DAI'} by extracting the
        # value after ': '' and before ''}' using split
        for col in edge_col:
            df_network[col] = df_network[col].apply(
                lambda x: x.split(": '")[1].split("'}")[0]
            )

    if exclude_special_route:
        # Exclude "LOOP" AND "SPOON", and "Error" in intermediary
        df_network = df_network[
            (df_network["label"] == "0") & (df_network["intermediary"] != "Error")
        ].copy()

    # convert the weight to float
    df_network[weight_col] = df_network[weight_col].astype(float)

    if aggreate_weight:
        # sum up dathe weight
        df_network = df_network.groupby(edge_col)[weight_col].sum().reset_index()

    if convert_undirected:
        # convert the edge to undirected
        df_network["edge"] = df_network[edge_col].apply(
            lambda x: tuple(sorted(x)), axis=1
        )
        df_network = df_network.groupby("edge")[weight_col].sum().reset_index()
        df_network[edge_col[0]] = df_network["edge"].apply(lambda x: x[0])
        df_network[edge_col[1]] = df_network["edge"].apply(lambda x: x[1])

    return df_network
