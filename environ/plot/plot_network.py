"""
Script to plot the network graph
"""

import ast
import datetime
import os
from typing import Literal

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd

from environ.constants import NETWORK_DATA_PATH, STABLE_DICT

SHUFLLE_LST = [
    ("USDC", 3, 0),
    ("USDT", 3, 1),
    ("DAI", 3, 2),
    ("WBTC", 4, 1),
    ("APE", 4, 2),
    ("WETH", 4, 3),
]
NODE_SIZE_SCALER = 300000
EDGE_WIDTHS_SCALER = 500


def load_token_data(
    date: datetime.datetime, uni_version: Literal["v2", "v3", "merged"] = "merged"
) -> pd.DataFrame:
    """
    Function to load the token data
    """

    # convert the date to string
    date_str = date.strftime("%Y%m%d")

    # load the data
    match uni_version:
        case "v2":
            token_data = pd.read_csv(
                f"{NETWORK_DATA_PATH}/v2/primary_tokens/primary_tokens_v2_{date_str}.csv",
                index_col=0,
            )
            # convert the dict columns to dict
            token_data["token"] = token_data["token"].apply(
                lambda x: ast.literal_eval(x)["symbol"]
            )

        case "v3":
            token_data = pd.read_csv(
                f"{NETWORK_DATA_PATH}/v3/primary_tokens/primary_tokens_v3_{date_str}.csv",
                index_col=0,
            )
        case "merged":
            df_v2 = pd.read_csv(
                f"{NETWORK_DATA_PATH}/v2/primary_tokens/primary_tokens_v2_{date_str}.csv",
                index_col=0,
            )
            # convert the dict columns to dict
            df_v2["token"] = df_v2["token"].apply(
                lambda x: ast.literal_eval(x)["symbol"]
            )

            # if the path exists
            df_v3 = (
                pd.read_csv(
                    f"{NETWORK_DATA_PATH}/v3/primary_tokens/primary_tokens_v3_{date_str}.csv",
                    index_col=0,
                )
                if os.path.exists(
                    f"{NETWORK_DATA_PATH}/v3/primary_tokens/primary_tokens_v3_{date_str}.csv"
                )
                else pd.DataFrame()
            )

            # merge the data
            token_data = pd.concat([df_v2, df_v3], ignore_index=True)

            # sum by group
            token_data = token_data.groupby(["token"])["total_tvl"].sum().reset_index()

    # label the stable coin
    token_data["stable"] = 0

    for stable_coin, _ in STABLE_DICT.items():
        token_data.loc[token_data["token"] == stable_coin, "stable"] = 1

    # return the data
    return token_data.sort_values(by=["stable"], ascending=False, ignore_index=True)


def shuffle_token_data(node_data: pd.DataFrame) -> pd.DataFrame:
    """
    Function to shuffle the token data to aviud overlapping
    """

    # get the stable and non stable count
    stable_count = len(node_data[node_data["stable"] == 1])
    nonstable_count = len(node_data[node_data["stable"] == 0])

    # shuffle the list
    for _, row in node_data.iterrows():
        for token, idx_1, idx_2 in SHUFLLE_LST:
            if row["token"] == token:
                insert_index = (
                    stable_count + round(nonstable_count / idx_1 * idx_2) + 0.5
                )
                current_index = node_data[node_data["token"] == token].index
                node_data.loc[insert_index] = row
                node_data = node_data.drop(labels=current_index, axis=0)
                node_data = node_data.sort_index().reset_index(drop=True)

    return node_data


def load_edge_data(
    date: datetime.datetime, uni_version: Literal["v2", "v3", "merged"] = "merged"
):
    """
    Function to load the inout flow
    """

    # get the date string
    date_str = date.strftime("%Y%m%d")

    # get the edge data
    edge_data = pd.read_csv(
        f"{NETWORK_DATA_PATH}/{uni_version}/inout_flow"
        + f"/inout_flow_tokens_{uni_version}_{date_str}.csv",
    )

    # convert the dict if the version is v2 for Source and Target
    if uni_version == "v2":
        edge_data["Source"] = edge_data["Source"].apply(
            lambda x: ast.literal_eval(x)["symbol"]
        )
        edge_data["Target"] = edge_data["Target"].apply(
            lambda x: ast.literal_eval(x)["symbol"]
        )

    return edge_data


def plot_network(
    date: datetime.datetime, uni_version: Literal["v2", "v3", "merged"] = "merged"
) -> None:
    """
    Function to plot the network graph
    """

    date_str = date.strftime("%Y%m%d")

    # initialize the graph
    volume_graph = nx.MultiDiGraph()

    # get the token data
    token_data = load_token_data(date, uni_version)

    # shuffle the token data
    node_data = shuffle_token_data(token_data)

    # create nodes
    for _, row in node_data.iterrows():
        volume_graph.add_node(
            row["token"],
            tvl=row["total_tvl"],
            stable=row["stable"],
        )

    # get the edge data
    edge_data = load_edge_data(date, uni_version)

    # create edges
    for _, row in edge_data.iterrows():
        volume_graph.add_edge(
            row["Source"],
            row["Target"],
            weight=row["Volume"],
        )

    # get the lists of weights for node sizes and edge widths
    node_sizes = nx.get_node_attributes(volume_graph, "tvl")
    node_colors = nx.get_node_attributes(volume_graph, "stable")
    edge_widths = nx.get_edge_attributes(volume_graph, "weight")

    # plot the network
    pos = nx.circular_layout(volume_graph)
    plt.figure(figsize=(16, 12))

    plt.title(
        label=f"Directional Trading Volume among Top 50 Pools in Uniswap at {date_str}",
        fontdict={"fontsize": 12},
        loc="center",
    )

    nx.draw_networkx_nodes(
        volume_graph,
        pos,
        node_size=[i / NODE_SIZE_SCALER for i in list(node_sizes.values())],
        node_color=[
            "tab:orange" if i == 1 else "tab:blue" for i in list(node_colors.values())
        ],
        alpha=0.8,
    )

    nx.draw_networkx_edges(
        volume_graph,
        pos,
        connectionstyle="arc3,rad=0.2",
        arrowstyle="-|>",
        arrowsize=20,
        alpha=0.3,
        width=[np.sqrt(i) / EDGE_WIDTHS_SCALER for i in list(edge_widths.values())],
    )
    nx.draw_networkx_labels(volume_graph, pos, font_size=18, verticalalignment="bottom")

    # save the plot
    plt.savefig(
        f"{NETWORK_DATA_PATH}/{uni_version}/network_graph/network_{uni_version}_{date_str}.jpg",
    )

    plt.close()


if __name__ == "__main__":
    plot_network(datetime.datetime(2021, 5, 1), "v2")
