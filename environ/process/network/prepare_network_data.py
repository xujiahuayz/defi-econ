# -*- coding: utf-8 -*-
"""
Prepare the dataset for the network graph
"""
import os
from os import path
import datetime
import pandas as pd
from environ.utils.config_parser import Config


def load_volume_dataset(date: datetime.datetime, uni_version: str) -> pd.DataFrame:
    """
    Load the volume dataset file from local file as dataframe
    """

    # Initialize configuration
    config = Config()

    date_str = date.strftime("%Y%m%d")

    if uni_version == "v2":
        data_source = path.join(
            config["dev"]["config"]["data"]["UNISWAP_V2_DATA_PATH"],
            "directional_volume/top50_directional_volume_v2_" + date_str + ".csv",
        )
    elif uni_version == "v3":
        data_source = path.join(
            config["dev"]["config"]["data"]["UNISWAP_V3_DATA_PATH"],
            "directional_volume/top50_directional_volume_v3_" + date_str + ".csv",
        )

    # Load the dataframe from the top 50 pairs
    df_top50_pairs_dir_volume = pd.read_csv(data_source)
    df_top50_pairs_dir_volume = df_top50_pairs_dir_volume.drop(columns=["Unnamed: 0"])

    return df_top50_pairs_dir_volume


def get_primary_token_list(date: datetime.datetime, uni_version: str) -> pd.DataFrame:
    """
    Get the primary token list as the nodes of network from the volume dataset.
    """

    df_top50_pairs_dir_volume = load_volume_dataset(date, uni_version)

    # Select the distinct token symbol
    df_primary_token = pd.concat(
        [
            df_top50_pairs_dir_volume[["token0"]].rename(columns={"token0": "token"}),
            df_top50_pairs_dir_volume[["token1"]].rename(columns={"token1": "token"}),
        ],
        ignore_index=True,
    )
    df_primary_token = df_primary_token.drop_duplicates(["token"]).reset_index(
        drop=True
    )

    if uni_version == "v2":
        tvl_symbol = "reserveUSD"
    elif uni_version == "v3":
        tvl_symbol = "tvlUSD"

    # Calculate total tvl
    for index_token, row_token in df_primary_token.iterrows():

        # Get the symbol of this token from the primary token list
        token = row_token["token"]

        # Global variable for this token
        total_tvl = 0

        # Get the pools involving this token as token0 or token1
        # TODO: potentially need to divide by 2 for V2
        # definitely for V3 need to also check the calculation altogether
        for _, row_pool in df_top50_pairs_dir_volume.iterrows():
            if token in {row_pool["token0"], row_pool["token1"]}:
                total_tvl = total_tvl + row_pool[tvl_symbol]

        df_primary_token.loc[index_token, "total_tvl"] = total_tvl

    return df_primary_token


def get_node_flow(date, uni_version) -> pd.DataFrame:
    """
    Get the inflow and outflow trading volume as the edges of the network from the volume dataset.
    """

    df_top50_pairs_dir_volume = load_volume_dataset(date, uni_version)

    df_edge = pd.DataFrame()

    for _, row_pool in df_top50_pairs_dir_volume.iterrows():
        row_0to1 = pd.DataFrame(
            {
                "Source": [row_pool["token0"]],
                "Target": [row_pool["token1"]],
                "Volume": [row_pool["token0To1VolumeUSD"]],
            }
        )

        row_1to0 = pd.DataFrame(
            {
                "Source": [row_pool["token1"]],
                "Target": [row_pool["token0"]],
                "Volume": [row_pool["token1To0VolumeUSD"]],
            }
        )

        # Add a new row to the dataframe
        df_edge = pd.concat([df_edge, row_0to1], ignore_index=True, axis=0)
        df_edge = pd.concat([df_edge, row_1to0], ignore_index=True, axis=0)

    return df_edge


def prepare_network_data(target_date: datetime.datetime, uniswap_version: str) -> None:
    """
    Prepare the network data and save to file
    """
    # Initialize configuration
    config = Config()

    df_node_list = get_primary_token_list(target_date, uniswap_version)
    # Write dataframe to csv
    target_date_str = target_date.strftime("%Y%m%d")
    node_file_name = path.join(
        config["dev"]["config"]["data"]["NETWORK_DATA_PATH"],
        uniswap_version
        + "/primary_tokens/primary_tokens_"
        + uniswap_version
        + "_"
        + target_date_str
        + ".csv",
    )

    df_node_list.to_csv(node_file_name)

    df_edge_list = get_node_flow(target_date, uniswap_version)
    # Write dataframe to csv
    edge_file_name = path.join(
        config["dev"]["config"]["data"]["NETWORK_DATA_PATH"],
        uniswap_version
        + "/inout_flow/inout_flow_tokens_"
        + uniswap_version
        + "_"
        + target_date_str
        + ".csv",
    )

    df_edge_list.to_csv(edge_file_name)
