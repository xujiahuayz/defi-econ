"""
Script to generate the eigenvector centrality for atomic swaps.
"""

import glob
import os
from pathlib import Path
from typing import Literal
from tqdm import tqdm
import networkx as nx
import warnings

import pandas as pd
import numpy as np

from environ.constants import BETWEENNESS_DATA_PATH, NETWORK_DATA_PATH

# Ignore warnings
warnings.filterwarnings("ignore")


def _compute_eigencent(
    edge: np.ndarray,
    weight: np.ndarray,
) -> pd.DataFrame:
    """
    compute the eigenvector centrality for a given graph
    :param edge: a numpy array of edges
    :param weight: a numpy array of weights
    :return: a dataframe of eigenvector centrality
    """

    # Define the graph
    eigen_graph = nx.MultiDiGraph()

    # unique list of the nodes
    token_lst = np.unique(edge)

    # add nodes
    for i in token_lst:
        eigen_graph.add_node(i)

    # add edges
    for i, edge_data in enumerate(edge):
        eigen_graph.add_edge(edge_data[0], edge_data[1], weight=weight[i][0])

    # a dataframe to store the results with one column equal to token_lst
    eigen_centrality_df = pd.DataFrame(token_lst, columns=["Token"])

    # compute the eigenvector centrality
    eigen_centrality_df["Inflow_centrality"] = nx.eigenvector_centrality_numpy(
        eigen_graph, weight="weight"
    ).values()

    # reverse the graph
    eigen_graph_reverse = eigen_graph.reverse()

    # compute the eigenvector centrality
    eigen_centrality_df["Outflow_centrality"] = nx.eigenvector_centrality_numpy(
        eigen_graph_reverse, weight="weight"
    ).values()

    return eigen_centrality_df


def get_eigencent_atomic(uni_ver: Literal["v2", "v3", "v2v3"] = "v2") -> None:
    """
    Calculate the eigenvector centrality for atomic swaps.
    """

    # Path to store the data
    path = str(Path(NETWORK_DATA_PATH) / "atomic_swap")

    # If there is no data in data/data_network/atomic, create the folder
    if not os.path.exists(path):
        os.makedirs(path)

    # get the list of files
    path = str(Path(BETWEENNESS_DATA_PATH) / "swap_route")
    file_lst = glob.glob(path + "/*.csv")

    # isolate the file with specific version
    file_name = [
        file_name for file_name in file_lst if uni_ver == file_name.split("_")[-2]
    ]

    # iterate through the files
    for file in tqdm(file_name):
        # read the file
        swaps_tx_route = pd.read_csv(file)

        # isolate the date
        date = file.split("_")[-1].split(".")[0]

        # Exclude "LOOP", "SPOON", and "Error"
        swaps_tx_route = swaps_tx_route[
            (swaps_tx_route["label"] == "0")
            & (swaps_tx_route["intermediary"] != "Error")
        ].copy()

        # get the list of edges
        edge = swaps_tx_route[["ultimate_source", "ultimate_target"]].values

        # get the list of weights
        weight = swaps_tx_route[["volume_usd"]].values

        # compute the eigenvector centrality
        eigen_centrality_df = _compute_eigencent(edge, weight)

        # save the results
        eigen_centrality_df.to_csv(
            str(
                Path(NETWORK_DATA_PATH)
                / "atomic_swap"
                / f"eigen_centrality_{uni_ver}_{date}.csv"
            ),
            index=False,
        )


if __name__ == "__main__":
    for uniswap_version in ["v2", "v3", "v2v3"]:
        get_eigencent_atomic(uniswap_version)
