"""
Script to prepare the vol_full_len dataframe
"""

import ast
import os

import pandas as pd
from tqdm import tqdm

from environ.constants import BETWEENNESS_DATA_PATH, NETWORK_DATA_PATH
from environ.utils.data_loarder import _load_in_data_lst, _preprocessing


def _preprocess_volume(
    df_network: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Function to preprocess the volume dataframe
    """

    # convert intermediary to list
    df_network["intermediary"] = df_network["intermediary"].map(ast.literal_eval)

    # prepare three data frame for ultimate source, ultimate target and intermediary
    # separately and with the volume
    df_us = df_network[["ultimate_source", "volume_usd"]].copy()
    df_ut = df_network[["ultimate_target", "volume_usd"]].copy()

    # rename the columns
    df_us.columns = ["Token", "volume"]
    df_ut.columns = ["Token", "volume"]

    # drop all the intermediary that is empty
    df_inter = df_network[df_network["intermediary"].map(lambda x: len(x) > 0)].copy()

    # iterate through the intermediary and create a new row for each
    # intermediary
    df_inter_lst = []
    for _, row in df_inter.iterrows():
        for inter in row["intermediary"]:
            df_inter_lst.append(
                {
                    "Token": inter,
                    "volume": row["volume_usd"],
                }
            )

    # convert the list to dataframe
    df_inter = pd.DataFrame(df_inter_lst)

    # group the dataframe by token and sum the volume
    df_us = df_us.groupby("Token").sum().reset_index()
    df_ut = df_ut.groupby("Token").sum().reset_index()
    df_inter = df_inter.groupby("Token").sum().reset_index()

    # calculatet the volume share
    df_us["volume_share"] = df_us["volume"] / df_us["volume"].sum()
    df_ut["volume_share"] = df_ut["volume"] / df_ut["volume"].sum()
    df_inter["volume_share"] = df_inter["volume"] / df_inter["volume"].sum()

    # return three dataframes
    return df_us, df_ut, df_inter


def vol_full_len_generator(
    file_root: str = str(NETWORK_DATA_PATH / "v2" / "inout_flow"),
    save_name: str = "vol_full_len",
    save_root_in: str = str(BETWEENNESS_DATA_PATH / "v2" / "vol_in_full_len"),
    save_root_out: str = str(BETWEENNESS_DATA_PATH / "v2" / "vol_out_full_len"),
    save_root_inter: str = str(BETWEENNESS_DATA_PATH / "v2" / "vol_inter_full_len"),
    filter_name: str = "",
):
    """
    Function to generate the full-length volume in and out dataframe
    """

    # load the data
    file_name_lst = _load_in_data_lst(
        file_root=file_root,
        filter_name=filter_name,
    )

    # check if the save folder exists
    if not os.path.exists(save_root_in):
        os.makedirs(save_root_in)
    if not os.path.exists(save_root_out):
        os.makedirs(save_root_out)
    if not os.path.exists(save_root_inter):
        os.makedirs(save_root_inter)

    # loop through the files
    for file_name in tqdm(file_name_lst):
        # get the date
        date = file_name.split("_")[-1].split(".")[0]

        # load the file
        df_network = pd.read_csv(file_name)

        # preliminary preprocess the data
        df_network = _preprocessing(
            df_network,
            edge_col=["ultimate_source", "ultimate_target"],
            weight_col=["volume_usd"],
            dict2str=False,
            exclude_special_route=True,
            aggreate_weight=False,
            convert_undirected=False,
        )

        try:
            # preprocess the volume
            df_us, df_ut, df_inter = _preprocess_volume(df_network)
        except:
            # ignore zero weight
            continue

        # save the data
        df_us.to_csv(
            os.path.join(save_root_out, f"{save_name}_{filter_name}_{date}.csv"),
            index=False,
        )

        df_ut.to_csv(
            os.path.join(save_root_in, f"{save_name}_{filter_name}_{date}.csv"),
            index=False,
        )

        df_inter.to_csv(
            os.path.join(save_root_inter, f"{save_name}_{filter_name}_{date}.csv"),
            index=False,
        )


if __name__ == "__main__":
    for version in ["v2", "v3", "v2v3"]:
        vol_full_len_generator(
            file_root=str(BETWEENNESS_DATA_PATH / "swap_route"),
            save_name="vol_full_len",
            save_root_in=str(NETWORK_DATA_PATH / version / "vol_in_full_len")
            if version != "v2v3"
            else str(NETWORK_DATA_PATH / "merged" / "vol_in_full_len"),
            save_root_out=str(NETWORK_DATA_PATH / version / "vol_out_full_len")
            if version != "v2v3"
            else str(NETWORK_DATA_PATH / "merged" / "vol_out_full_len"),
            save_root_inter=str(NETWORK_DATA_PATH / version / "vol_inter_full_len")
            if version != "v2v3"
            else str(NETWORK_DATA_PATH / "merged" / "vol_inter_full_len"),
            filter_name=version,
        )
