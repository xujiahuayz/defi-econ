"""
Script to generate the eigenvector centrality for atomic swaps.
"""

import glob
import os
import warnings

from typing import Literal
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

        # convert the edge to str
        df_network[edge_col] = df_network[edge_col].astype(str)

        # convert the edge to undirected
        df_network["edge"] = df_network[edge_col].apply(
            lambda x: tuple(sorted(x)), axis=1
        )
        df_network = df_network.groupby("edge")[weight_col].sum().reset_index()
        df_network[edge_col[0]] = df_network["edge"].apply(lambda x: x[0])
        df_network[edge_col[1]] = df_network["edge"].apply(lambda x: x[1])

    return df_network


def _generate_node_edge(
    df_network: pd.DataFrame,
    edge_col: list[str],
    weight_col: list[str],
) -> tuple[np.ndarray, np.ndarray]:
    """
    Function to generate the node and edge arrays
    """

    # get the edge list
    edge = df_network[edge_col].to_numpy()

    # get the weight list
    weight = df_network[weight_col].to_numpy()

    return edge, weight


def _compute_indicator(
    edge: np.ndarray,
    weight: np.ndarray,
    graph_type: Literal["directed_multi", "undirected_multi", "directed", "undirected"],
    indicator_type: Literal["eigenvector", "clustering"] = "eigenvector",
) -> pd.DataFrame:
    """
    compute indicators for a given graph
    :param edge: a numpy array of edges
    :param weight: a numpy array of weights
    :param graph_type: a string to indicate the type of graph
    :param indicator_type: a string to indicate the type of indicator
    :return: a dataframe of eigenvector centrality
    """

    match graph_type:
        case "directed_multi":
            # create a directed multi graph
            graph = nx.MultiDiGraph()
        case "undirected_multi":
            # create a undirected multi graph
            graph = nx.MultiGraph()
        case "directed":
            # create a directed graph
            graph = nx.DiGraph()
        case "undirected":
            # create a undirected graph
            graph = nx.Graph()

    # unique list of the nodes
    token_lst = np.unique(edge)

    # add nodes
    for i in token_lst:
        graph.add_node(i)

    # add edges
    for i, edge_data in enumerate(edge):
        graph.add_edge(edge_data[0], edge_data[1], weight=weight[i][0])

    # a dataframe to store the results with one column equal to token_lst
    graph_df = pd.DataFrame(token_lst, columns=["Token"])

    if indicator_type == "eigenvector":
        # if the graph is directed
        if graph_type in ["directed_multi", "directed"]:
            # compute the eigenvector centrality
            graph_df["Inflow_centrality"] = nx.eigenvector_centrality_numpy(
                graph, weight="weight"
            ).values()

            # reverse the graph
            graph_reverse = graph.reverse()

            # compute the eigenvector centrality
            graph_df["Outflow_centrality"] = nx.eigenvector_centrality_numpy(
                graph_reverse, weight="weight"
            ).values()
        else:
            # compute the eigenvector centrality
            graph_df["eigenvector_centrality"] = nx.eigenvector_centrality_numpy(
                graph, weight="weight"
            ).values()

    if indicator_type == "clustering":
        # compute the eigenvector centrality
        graph_df["clustering_coefficient"] = nx.clustering(
            graph, weight="weight"
        ).values()

    return graph_df


def indicator_generator(
    file_root: str = str(NETWORK_DATA_PATH / "v2" / "inout_flow"),
    filter_name: str = "",
    edge_col: list[str] = ["ultimate_source", "ultimate_target"],
    weight_col: list[str] = ["volume_usd"],
    save_root: str = str(NETWORK_DATA_PATH / "eigen_centrality"),
    save_name: str = "eigen_centrality",
    exclude_special_route: bool = True,
    dict2str: bool = False,
    aggreate_weight: bool = False,
    indicator_type: Literal["eigenvector", "clustering"] = "eigenvector",
    convert_undirected: bool = False,
    graph_type: Literal[
        "directed_multi", "undirected_multi", "directed", "undirected"
    ] = "directed",
) -> None:
    """
    Aggreate function to generate the eigenvector centrality
    :param file_root: a string to indicate the root of the data
    :param filter_name: a string to indicate the filter name
    :param edge_col: a list of strings to indicate the edge columns
    :param weight_col: a list of strings to indicate the weight columns
    :param save_root: a string to indicate the root of the save folder
    :param exclude_special_route: a boolean to indicate whether to exclude the special route
    :param dict2str: a boolean to indicate whether to convert the dictionary to string
    :param aggreate_weight: a boolean to indicate whether to aggreate the weight
    :param indicator_type: a string to indicate the type of indicator
    :param convert_undirected: a boolean to indicate whether to convert the
    directed graph to undirected
    :param graph_type: a string to indicate the type of graph
    :return: None
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

        # load the data
        df_network = pd.read_csv(file_name)

        # preprocess the data
        df_network = _preprocessing(
            df_network,
            edge_col,
            weight_col,
            dict2str,
            exclude_special_route,
            aggreate_weight,
            convert_undirected,
        )

        # generate the node and edge arrays
        edge, weight = _generate_node_edge(df_network, edge_col, weight_col)

        # if the weight is empty, skip
        if not weight.any():
            continue

        # compute the indicator
        eigen_centrality_df = _compute_indicator(
            edge, weight, graph_type, indicator_type
        )

        # save the data
        eigen_centrality_df.to_csv(
            save_root + f"/{save_name}_{filter_name}_{date}.csv",
            index=False,
        )


if __name__ == "__main__":
    # compute the clustering coefficient
    # for version in ["v2", "v3", "v2v3"]:
    #     indicator_generator(
    #         file_root=str(BETWEENNESS_DATA_PATH / "swap_route"),
    #         filter_name=version,
    #         edge_col=["ultimate_source", "ultimate_target"],
    #         weight_col=["volume_usd"],
    #         save_root=str(NETWORK_DATA_PATH / version / "clustering_ind")
    #         if version != "v2v3"
    #         else str(NETWORK_DATA_PATH / "merged" / "clustering_ind"),
    #         save_name="clustering_coefficient",
    #         exclude_special_route=True,
    #         dict2str=False,
    #         aggreate_weight=False,
    #         graph_type="undirected",
    #         indicator_type="clustering",
    #         convert_undirected=True,
    #     )

    # compute the simple undirected eigenvector centrality using full-length routes
    for version in ["v2", "v3", "merged"]:
        indicator_generator(
            file_root=str(NETWORK_DATA_PATH / version / "inout_flow"),
            edge_col=["Source", "Target"],
            weight_col=["Volume"],
            save_root=str(NETWORK_DATA_PATH / version / "total_eigen_centrality_undirected"),
            save_name="total_eigen_centrality_undirected",
            exclude_special_route=False,
            dict2str=False,
            aggreate_weight=False,
            graph_type="undirected",
            indicator_type="eigenvector",
            convert_undirected=True,
        )

    # # compute the simple undirected eigenvector centrality using total volume
    # for version in ["v2", "v3", "v2v3"]:
    #     indicator_generator(
    #         file_root=str(BETWEENNESS_DATA_PATH / "swap_route"),
    #         filter_name=version,
    #         edge_col=["ultimate_source", "ultimate_target"],
    #         weight_col=["volume_usd"],
    #         save_root=str(NETWORK_DATA_PATH / version / "eigen_centrality_undirected")
    #         if version != "v2v3"
    #         else str(NETWORK_DATA_PATH / "merged" / "eigen_centrality_undirected"),
    #         save_name="eigen_centrality",
    #         exclude_special_route=True,
    #         dict2str=False,
    #         aggreate_weight=True,
    #         graph_type="undirected",
    #         indicator_type="eigenvector",
    #         convert_undirected=True,
    #     )


    # compute the multi undirected eigenvector centrality using full-length routes
    # for version in ["v2", "v3", "v2v3"]:
    #     indicator_generator(
    #         file_root=str(BETWEENNESS_DATA_PATH / "swap_route"),
    #         filter_name=version,
    #         edge_col=["ultimate_source", "ultimate_target"],
    #         weight_col=["volume_usd"],
    #         save_root=str(
    #             NETWORK_DATA_PATH / version / "eigen_centrality_undirected_multi"
    #         )
    #         if version != "v2v3"
    #         else str(
    #             NETWORK_DATA_PATH / "merged" / "eigen_centrality_undirected_multi"
    #         ),
    #         save_name="eigen_centrality",
    #         exclude_special_route=True,
    #         dict2str=False,
    #         aggreate_weight=False,
    #         graph_type="undirected_multi",
    #         indicator_type="eigenvector",
    #         convert_undirected=False,
    #     )

    # for version in ["v2", "v3", "merged"]:
    #     eigencent_generator(
    #         file_root=str(NETWORK_DATA_PATH / version / "inout_flow"),
    #         edge_col=["Source", "Target"],
    #         weight_col=["Volume"],
    #         save_root=str(NETWORK_DATA_PATH / version / "eigen_centrality_pool"),
    #         exclude_special_route=False,
    #         dict2str=True,
    #         aggreate_weight=False,
    #         multi_graph=True,
    #     )

    # for version in ["v2", "v3", "v2v3"]:
    #     eigencent_generator(
    #         file_root=str(BETWEENNESS_DATA_PATH / "swap_route"),
    #         filter_name=version,
    #         edge_col=["ultimate_source", "ultimate_target"],
    #         weight_col=["volume_usd"],
    #         save_root=str(NETWORK_DATA_PATH / version / "eigen_centrality_swap")
    #         if version != "v2v3"
    #         else str(NETWORK_DATA_PATH / "merged" / "eigen_centrality_swap"),
    #     )
