# -*- coding: utf-8 -*-
"""
Plot the network graph based on processed network dataset
"""

from os import path
import os
import datetime
import networkx as nx
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from environ.utils.config_parser import Config

# Initialize configuration
config = Config()


def prepare_volume(date: datetime.datetime, data_source: str) -> None:
    """
    Function to calculate volume-related independent variables
    """

    # Convert the datetime to the string
    date_str = date.strftime("%Y%m%d")

    # Edge data
    edge_data = []

    if (data_source == "v2") | (data_source == "merged"):
        edge_data_v2 = pd.read_csv(
            path.join(
                config["dev"]["config"]["data"]["NETWORK_DATA_PATH"],
                "v2"
                + "/inout_flow/inout_flow_tokens_"
                + "v2"
                + "_"
                + date_str
                + ".csv",
            ),
            index_col=0,
        )

        # Change data format at the presentation layer
        edge_data_v2["Source_symbol"] = [i[12:-2] for i in edge_data_v2["Source"]]
        edge_data_v2 = edge_data_v2.drop(columns=["Source"]).rename(
            columns={"Source_symbol": "Source"}
        )
        edge_data_v2["Target_symbol"] = [i[12:-2] for i in edge_data_v2["Target"]]
        edge_data_v2 = edge_data_v2.drop(columns=["Target"]).rename(
            columns={"Target_symbol": "Target"}
        )
        edge_data_v2 = edge_data_v2[["Source", "Target", "Volume"]]

        edge_data.append(edge_data_v2)

    if (data_source == "v3") | (data_source == "merged"):
        # List for the token data of v3
        edge_data_v3_path = os.listdir(
            path.join(
                config["dev"]["config"]["data"]["NETWORK_DATA_PATH"],
                "v3" + "/inout_flow/",
            )
        )

        # Check whether the uniswap v3 have data, and decide whether to merge
        if "inout_flow_tokens_" + "v3" + "_" + date_str + ".csv" in edge_data_v3_path:
            edge_data_v3 = pd.read_csv(
                path.join(
                    config["dev"]["config"]["data"]["NETWORK_DATA_PATH"],
                    "v3"
                    + "/inout_flow/inout_flow_tokens_"
                    + "v3"
                    + "_"
                    + date_str
                    + ".csv",
                ),
                index_col=0,
            )
            edge_data.append(edge_data_v3)

    edge_data = pd.concat(edge_data)
    edge_data = edge_data.groupby(["Source", "Target"])["Volume"].sum().reset_index()

    # Save the volume data
    edge_data.to_csv(
        path.join(
            config["dev"]["config"]["data"]["NETWORK_DATA_PATH"],
            data_source + "/volume/volume_" + data_source + "_" + date_str + ".csv",
        )
    )

    # Calculate and save the volume_in data
    volume_in_data = edge_data.copy()
    volume_in_data = (
        volume_in_data.groupby(["Target"])["Volume"]
        .sum()
        .reset_index()
        .rename(columns={"Target": "Token"})
    )
    volume_in_data.to_csv(
        path.join(
            config["dev"]["config"]["data"]["NETWORK_DATA_PATH"],
            data_source
            + "/volume_in/volume_in_"
            + data_source
            + "_"
            + date_str
            + ".csv",
        )
    )

    # Calculate and save the volume_in_share data
    volume_in_share_data = volume_in_data.copy()
    volume_in_share_data["Volume"] = (
        volume_in_share_data["Volume"] / volume_in_share_data["Volume"].sum()
    )
    volume_in_share_data.to_csv(
        path.join(
            config["dev"]["config"]["data"]["NETWORK_DATA_PATH"],
            data_source
            + "/volume_in_share/volume_in_share_"
            + data_source
            + "_"
            + date_str
            + ".csv",
        )
    )

    # Calculate and save the volume_out data
    volume_out_data = edge_data.copy()
    volume_out_data = (
        volume_out_data.groupby(["Source"])["Volume"]
        .sum()
        .reset_index()
        .rename(columns={"Source": "Token"})
    )
    volume_out_data.to_csv(
        path.join(
            config["dev"]["config"]["data"]["NETWORK_DATA_PATH"],
            data_source
            + "/volume_out/volume_out_"
            + data_source
            + "_"
            + date_str
            + ".csv",
        )
    )

    # Calculate and save the volume_out_share data
    volume_out_share_data = volume_out_data.copy()
    volume_out_share_data["Volume"] = (
        volume_out_share_data["Volume"] / volume_out_share_data["Volume"].sum()
    )
    volume_out_share_data.to_csv(
        path.join(
            config["dev"]["config"]["data"]["NETWORK_DATA_PATH"],
            data_source
            + "/volume_out_share/volume_out_share_"
            + data_source
            + "_"
            + date_str
            + ".csv",
        )
    )

    # Calculate and save the volume_total data
    volume_total_data = []
    volume_total_data.append(volume_in_data)
    volume_total_data.append(volume_out_data)
    volume_total_data = pd.concat(volume_total_data)
    volume_total_data = (
        volume_total_data.groupby(["Token"])["Volume"].sum().reset_index()
    )
    volume_total_data.to_csv(
        path.join(
            config["dev"]["config"]["data"]["NETWORK_DATA_PATH"],
            data_source
            + "/volume_total/volume_total_"
            + data_source
            + "_"
            + date_str
            + ".csv",
        )
    )

    # Calculate and save the volume_share data
    volume_share_data = volume_total_data.copy()
    volume_share_data["Volume"] = (
        volume_share_data["Volume"] / volume_share_data["Volume"].sum()
    )
    volume_share_data.to_csv(
        path.join(
            config["dev"]["config"]["data"]["NETWORK_DATA_PATH"],
            data_source
            + "/volume_share/volume_share_"
            + data_source
            + "_"
            + date_str
            + ".csv",
        )
    )


# def plot_network(date: datetime.datetime, uniswap_version: str) -> None:
def prepare_network_graph(
    date: datetime.datetime, data_source: str, directed: bool
) -> None:
    """
    Plot the network by networkx
    """

    # Convert the datetime to the string
    date_str = date.strftime("%Y%m%d")

    # Define the graph
    if directed:
        G = nx.MultiDiGraph()
    else:
        G = nx.MultiGraph()

    # token data
    token_data = []

    if (data_source == "v2") | (data_source == "merged"):
        token_data_v2 = pd.read_csv(
            path.join(
                config["dev"]["config"]["data"]["NETWORK_DATA_PATH"],
                "v2"
                + "/primary_tokens/primary_tokens_"
                + "v2"
                + "_"
                + date_str
                + ".csv",
            ),
            index_col=0,
        )

        # Change data format at the presentation layer for Uniswap 2
        token_data_v2["token_symbol"] = [i[12:-2] for i in token_data_v2["token"]]
        token_data_v2 = token_data_v2.drop(columns=["token"]).rename(
            columns={"token_symbol": "token"}
        )[["token", "total_tvl"]]

        token_data.append(token_data_v2)

    if (data_source == "v3") | (data_source == "merged"):
        # List for the token data of v3
        token_data_v3_path = os.listdir(
            path.join(
                config["dev"]["config"]["data"]["NETWORK_DATA_PATH"],
                "v3" + "/primary_tokens/",
            )
        )

        # Check whether the uniswap v3 have data, and decide whether to merge
        if "primary_tokens_" + "v3" + "_" + date_str + ".csv" in token_data_v3_path:
            token_data_v3 = pd.read_csv(
                path.join(
                    config["dev"]["config"]["data"]["NETWORK_DATA_PATH"],
                    "v3"
                    + "/primary_tokens/primary_tokens_"
                    + "v3"
                    + "_"
                    + date_str
                    + ".csv",
                ),
                index_col=0,
            )
            token_data.append(token_data_v3)

    # Generate token data
    token_data = pd.concat(token_data)
    token_data = token_data.groupby(["token"])["total_tvl"].sum().reset_index()

    token_data.to_csv(
        path.join(
            config["dev"]["config"]["data"]["NETWORK_DATA_PATH"],
            data_source + "/tvl/tvl_" + data_source + "_" + date_str + ".csv",
        ),
        index=False,
    )

    tvl_share = token_data.copy()
    tvl_share["total_tvl"] = tvl_share["total_tvl"] / tvl_share["total_tvl"].sum()
    tvl_share.to_csv(
        path.join(
            config["dev"]["config"]["data"]["NETWORK_DATA_PATH"],
            data_source
            + "/tvl_share/tvl_share_"
            + data_source
            + "_"
            + date_str
            + ".csv",
        ),
        index=False,
    )

    token_lib = []

    if (data_source == "v2") | (data_source == "merged"):
        token_lib_v2 = pd.DataFrame.from_dict(
            config["dev"]["config"]["token_library"]["v2"]
        )
        token_lib.append(token_lib_v2)

    if (data_source == "v3") | (data_source == "merged"):
        token_lib_v3 = pd.DataFrame.from_dict(
            config["dev"]["config"]["token_library"]["v3"]
        )
        token_lib.append(token_lib_v3)

    token_lib = pd.concat(token_lib)
    token_lib = token_lib.drop_duplicates("token").set_index("token")

    # label stable coin or non-stable coin
    token_data = token_data.join(token_lib, on="token", how="left")
    # token_data = token_data.drop(columns=["eigenvector_centrality"])

    # Sort the order by stablecoin
    token_data = token_data.sort_values(
        by=["stable"], ascending=False, ignore_index=True
    )

    stable_count = len(token_data[token_data["stable"] == 1])
    nonstable_count = len(token_data[token_data["stable"] == 0])

    node_data = token_data.copy()

    # Shuffle the list to make BIG 6(USDC, USDT, DAI, WBTC, WETH, APE) separate to avoid overlap
    for _, row in token_data.iterrows():
        if row["token"] == "USDC":
            insert_index = round(stable_count / 3 * 0) + 0.5
            current_index = node_data[node_data["token"] == "USDC"].index
            node_data.loc[insert_index] = row
            node_data = node_data.drop(labels=current_index, axis=0)
            node_data = node_data.sort_index().reset_index(drop=True)
        elif row["token"] == "USDT":
            insert_index = round(stable_count / 3 * 1) + 0.5
            current_index = node_data[node_data["token"] == "USDT"].index
            node_data.loc[insert_index] = row
            node_data = node_data.drop(labels=current_index, axis=0)
            node_data = node_data.sort_index().reset_index(drop=True)
        elif row["token"] == "DAI":
            insert_index = round(stable_count / 3 * 2) + 0.5
            current_index = node_data[node_data["token"] == "DAI"].index
            node_data.loc[insert_index] = row
            node_data = node_data.drop(labels=current_index, axis=0)
            node_data = node_data.sort_index().reset_index(drop=True)
        elif row["token"] == "WBTC":
            insert_index = stable_count + round(nonstable_count / 4 * 1) + 0.5
            current_index = node_data[node_data["token"] == "WBTC"].index
            node_data.loc[insert_index] = row
            node_data = node_data.drop(current_index, axis=0)
            node_data = node_data.sort_index().reset_index(drop=True)
        elif row["token"] == "APE":
            insert_index = stable_count + round(nonstable_count / 4 * 2) + 0.5
            current_index = node_data[node_data["token"] == "APE"].index
            node_data.loc[insert_index] = row
            node_data = node_data.drop(labels=current_index, axis=0)
            node_data = node_data.sort_index().reset_index(drop=True)
        elif row["token"] == "WETH":
            insert_index = stable_count + round(nonstable_count / 4 * 3) + 0.5
            current_index = node_data[node_data["token"] == "WETH"].index
            node_data.loc[insert_index] = row
            node_data = node_data.drop(labels=current_index, axis=0)
            node_data = node_data.sort_index().reset_index(drop=True)

    for _, row in node_data.iterrows():
        token = row["token"]
        # total_tvl = row["total_tvl"]
        # stable = row["stable"]
        G.add_node(token, tvl=row["total_tvl"], stable=row["stable"])

    # Edge data
    edge_data = []

    if (data_source == "v2") | (data_source == "merged"):
        edge_data_v2 = pd.read_csv(
            path.join(
                config["dev"]["config"]["data"]["NETWORK_DATA_PATH"],
                "v2"
                + "/inout_flow/inout_flow_tokens_"
                + "v2"
                + "_"
                + date_str
                + ".csv",
            ),
            index_col=0,
        )

        # Change data format at the presentation layer
        edge_data_v2["Source_symbol"] = [i[12:-2] for i in edge_data_v2["Source"]]
        edge_data_v2 = edge_data_v2.drop(columns=["Source"]).rename(
            columns={"Source_symbol": "Source"}
        )
        edge_data_v2["Target_symbol"] = [i[12:-2] for i in edge_data_v2["Target"]]
        edge_data_v2 = edge_data_v2.drop(columns=["Target"]).rename(
            columns={"Target_symbol": "Target"}
        )
        edge_data_v2 = edge_data_v2[["Source", "Target", "Volume"]]

        edge_data.append(edge_data_v2)
    if (data_source == "v3") | (data_source == "merged"):
        # List for the token data of v3
        edge_data_v3_path = os.listdir(
            path.join(
                config["dev"]["config"]["data"]["NETWORK_DATA_PATH"],
                "v3" + "/inout_flow/",
            )
        )

        # Check whether the uniswap v3 have data, and decide whether to merge
        if "inout_flow_tokens_" + "v3" + "_" + date_str + ".csv" in edge_data_v3_path:
            edge_data_v3 = pd.read_csv(
                path.join(
                    config["dev"]["config"]["data"]["NETWORK_DATA_PATH"],
                    "v3"
                    + "/inout_flow/inout_flow_tokens_"
                    + "v3"
                    + "_"
                    + date_str
                    + ".csv",
                ),
                index_col=0,
            )
            edge_data.append(edge_data_v3)

    edge_data = pd.concat(edge_data)
    edge_data = edge_data.groupby(["Source", "Target"])["Volume"].sum().reset_index()

    # If the graph is undirected, we need to sum the volume of the two directions
    if not directed:
        edge_data["token_pair"] = edge_data.apply(
            lambda x: frozenset([x["Source"], x["Target"]]), axis=1
        )
        # sum up the volume for the same token pair and keep the source and target
        edge_data = (
            edge_data.groupby("token_pair")
            .agg({"Source": "first", "Target": "first", "Volume": "sum"})
            .reset_index()
            .drop(columns=["token_pair"])
        )

    for _, row in edge_data.iterrows():
        source = row["Source"]
        target = row["Target"]
        dir_volume = row["Volume"]
        G.add_edge(source, target, weight=dir_volume)

    # Compute degree and centrality
    df_centrality = node_data.copy()
    df_centrality["eigenvector_centrality"] = nx.eigenvector_centrality_numpy(
        G, weight="weight"
    ).values()
    betweenness_centrality_dict = nx.betweenness_centrality(
        G, k=None, normalized=True, weight=None, endpoints=False, seed=None
    )
    df_centrality["betweenness_centrality"] = df_centrality.apply(
        lambda x: betweenness_centrality_dict[x.token], axis=1
    )
    df_centrality["degree"] = [i[1] for i in list(G.degree())]
    df_centrality["in_degree"] = [i[1] for i in list(G.in_degree())]
    df_centrality["out_degree"] = [i[1] for i in list(G.out_degree())]
    df_centrality["weighted_degree"] = [i[1] for i in list(G.degree(weight="weight"))]
    df_centrality["weighted_in_degree"] = [
        i[1] for i in list(G.in_degree(weight="weight"))
    ]
    df_centrality["weighted_out_degree"] = [
        i[1] for i in list(G.out_degree(weight="weight"))
    ]

    df_centrality.to_csv(
        path.join(
            config["dev"]["config"]["data"]["NETWORK_DATA_PATH"],
            data_source
            + "/inflow_centrality/centrality_"
            + data_source
            + "_"
            + date_str
            + ".csv",
        )
    )

    G = G.reverse()
    # Compute out degree and centrality
    df_centrality_out = node_data.copy()
    df_centrality_out["eigenvector_centrality"] = nx.eigenvector_centrality_numpy(
        G, weight="weight"
    ).values()
    df_centrality_out["weighted_degree"] = [
        i[1] for i in list(G.degree(weight="weight"))
    ]
    df_centrality_out["weighted_in_degree"] = [
        i[1] for i in list(G.in_degree(weight="weight"))
    ]
    df_centrality_out["weighted_out_degree"] = [
        i[1] for i in list(G.out_degree(weight="weight"))
    ]

    df_centrality_out.to_csv(
        path.join(
            config["dev"]["config"]["data"]["NETWORK_DATA_PATH"],
            data_source
            + "/outflow_centrality/centrality_"
            + data_source
            + "_"
            + date_str
            + ".csv",
        )
    )
