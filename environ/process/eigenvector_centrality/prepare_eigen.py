"""
Script to generate the eigenvector centrality for atomic swaps.
"""

import glob
import os
import warnings

import networkx as nx
import numpy as np
import pandas as pd
from tqdm import tqdm

from environ.constants import NETWORK_DATA_PATH, BETWEENNESS_DATA_PATH

# Ignore warnings
warnings.filterwarnings("ignore")


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


def _generate_node_edge(
    file_name: str, edge_col: list[str], weight_col: list[str]
) -> tuple[np.ndarray, np.ndarray]:
    """
    Function to generate the node and edge arrays
    """

    # load the data
    df_network = pd.read_csv(file_name)

    # Exclude "LOOP" AND "SPOON", and "Error" in intermediary
    df_network = df_network[
        (df_network["label"] == "0") & (df_network["intermediary"] != "Error")
    ].copy()

    # # unwrap the dictionary {'symbol': 'DAI'} by extracting the
    # # value after ': '' and before ''}' using split
    # for col in edge_col:
    #     df_network[col] = df_network[col].apply(
    #         lambda x: x.split(": '")[1].split("'}")[0]
    #     )

    # get the edge list
    edge = df_network[edge_col].to_numpy()

    # get the weight list
    weight = df_network[weight_col].to_numpy()

    return edge, weight


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


def eigencent_generator(
    file_root: str = str(NETWORK_DATA_PATH / "v2" / "inout_flow"),
    filter_name: str = "",
    edge_col: list[str] = ["ultimate_source", "ultimate_target"],
    weight_col: list[str] = ["volume_usd"],
    save_root: str = str(NETWORK_DATA_PATH / "eigen_centrality"),
) -> None:
    """
    Aggreate function to generate the eigenvector centrality
    """

    # load the data
    file_name_lst = _load_in_data_lst(file_root, filter_name=filter_name)

    # check if the save folder exists
    if not os.path.exists(save_root):
        os.makedirs(save_root)

    # loop through the data
    for file_name in tqdm(file_name_lst, desc="Generating eigenvector centrality"):
        # get the date
        date = file_name.split("_")[-1].split(".")[0]

        # generate the node and edge arrays
        edge, weight = _generate_node_edge(file_name, edge_col, weight_col)

        # if the weight is empty, skip
        if not weight.any():
            continue

        # compute the eigenvector centrality
        eigen_centrality_df = _compute_eigencent(edge, weight)

        # save the data
        eigen_centrality_df.to_csv(
            save_root + f"/eigen_centrality_{filter_name}_{date}.csv",
            index=False,
        )


if __name__ == "__main__":
    for version in ["v2", "v3", "merged"]:
        eigencent_generator(
            file_root=str(NETWORK_DATA_PATH / version / "inout_flow"),
            edge_col=["Source", "Target"],
            weight_col=["Volume"],
            save_root=str(NETWORK_DATA_PATH / version / "eigen_centrality_pool"),
        )

    # for version in ["v3", "v2v3"]:
    #     eigencent_generator(
    #         file_root=str(BETWEENNESS_DATA_PATH / "swap_route"),
    #         filter_name=version,
    #         edge_col=["ultimate_source", "ultimate_target"],
    #         weight_col=["volume_usd"],
    #         save_root=str(NETWORK_DATA_PATH / version / "eigen_centrality_swap")
    #         if version != "v2v3"
    #         else str(NETWORK_DATA_PATH / "merged" / "eigen_centrality_swap"),
    #     )
