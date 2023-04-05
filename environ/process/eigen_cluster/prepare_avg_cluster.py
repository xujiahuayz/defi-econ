"""
Script to generate the eigenvector centrality for atomic swaps.
"""

import warnings

import networkx as nx
import numpy as np
import pandas as pd
from tqdm import tqdm

from data.constants import NETWORK_DATA_PATH, TABLE_PATH, BETWEENNESS_DATA_PATH
from environ.process.eigen_cluster.prepare_eigen_cluster import (
    _load_in_data_lst,
    _generate_node_edge,
)

# Ignore warnings
warnings.filterwarnings("ignore")


def _compute_avg_cluster(
    edge: np.ndarray,
    weight: np.ndarray,
) -> float:
    """
    Function to compute the average clustering coefficient.
    """

    # create a graph
    graph = nx.Graph()

    # unique list of the nodes
    token_lst = np.unique(edge)

    # add nodes
    for i in token_lst:
        graph.add_node(i)

    # add edges
    for i, edge_data in enumerate(edge):
        graph.add_edge(edge_data[0], edge_data[1], weight=weight[i][0])

    return nx.average_clustering(graph)


def indicator_generator(
    file_root: str = str(NETWORK_DATA_PATH / "v2" / "inout_flow"),
    filter_name: str = "",
    edge_col: list[str] = ["ultimate_source", "ultimate_target"],
    weight_col: list[str] = ["volume_usd"],
    exclude_special_route: bool = True,
    dict2str: bool = False,
    aggreate_weight: bool = False,
    convert_undirected: bool = False,
) -> pd.DataFrame:
    """
    Aggreate function to generate the average clustering coefficient.
    """

    # load the data
    file_name_lst = _load_in_data_lst(file_root, filter_name=filter_name)

    # a dataframe to store the data with column "Date", "avg_cluster"
    avg_cluster_df = pd.DataFrame(columns=["Date", "avg_cluster"])

    # loop through the data
    for file_name in tqdm(
        file_name_lst, desc="Generating average clustering coefficient"
    ):
        # get the date
        date = file_name.split("_")[-1].split(".")[0]

        # generate the node and edge arrays
        edge, weight = _generate_node_edge(
            file_name,
            edge_col,
            weight_col,
            exclude_special_route,
            dict2str,
            aggreate_weight,
            convert_undirected,
        )

        # if the weight is empty, skip
        if not weight.any():
            continue

        # compute the average clustering coefficient
        avg_cluster = _compute_avg_cluster(edge, weight)

        # append to the dataframe
        avg_cluster_df = avg_cluster_df.append(
            {"Date": date, "avg_cluster": avg_cluster}, ignore_index=True
        )

    # convert the date column to datetime
    avg_cluster_df["Date"] = pd.to_datetime(avg_cluster_df["Date"])

    return avg_cluster_df


if __name__ == "__main__":
    # load in the data
    series_df = pd.read_pickle(TABLE_PATH / "herf_panel.pkl")

    # convert the date column to datetime
    series_df["Date"] = pd.to_datetime(series_df["Date"])

    # compute the average clustering coefficient
    avg_cluster_df = indicator_generator(
        file_root=str(BETWEENNESS_DATA_PATH / "swap_route"),
        filter_name="v2v3",
        edge_col=["ultimate_source", "ultimate_target"],
        weight_col=["volume_usd"],
        exclude_special_route=True,
        dict2str=False,
        aggreate_weight=False,
        convert_undirected=True,
    )

    # merge the data
    series_df = series_df.merge(
        avg_cluster_df,
        how="left",
        left_on="Date",
        right_on="Date",
    )

    # save the data
    series_df.to_pickle(TABLE_PATH / "herf_panel_merged.pkl")
