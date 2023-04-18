"""
Function to prepare the number of cliques in the network.
"""

import multiprocessing as mp

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd

from environ.constants import UNISWAP_V2_DATA_PATH, DATA_PATH, TABLE_PATH
from environ.utils.data_loarder import (
    _generate_node_edge,
    _load_in_folder_data_lst,
    _preprocessing,
    _load_in_data_merge,
)


def _compute_clique_num(
    edge: np.ndarray,
    weight: np.ndarray,
) -> int:
    """
    Function to compute the number of cliques in the network.
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

    return sum(1 for _ in nx.find_cliques(graph))


def worker(file_name, queue):
    # load in the data
    df_network = _load_in_data_merge(file_path=file_name)

    # number of transactions
    num_transactions = df_network.shape[0]

    # get the date
    date = file_name.split("_")[-1].split(".")[0]

    # preprocess the data
    df_network = _preprocessing(
        df_network=df_network,
        edge_col=["token0_symbol", "token1_symbol"],
        weight_col=["amountUSD"],
        dict2str=False,
        exclude_special_route=False,
        aggreate_weight=False,
        convert_undirected=True,
    )

    # generate the node and edge
    edge, weight = _generate_node_edge(
        df_network=df_network,
        edge_col=["token0_symbol", "token1_symbol"],
        weight_col=["amountUSD"],
    )

    # if the weight is empty, then skip
    if weight.size == 0:
        return

    # compute the number of cliques
    clique_num = _compute_clique_num(edge, weight)

    # append the data to the list
    queue.put((date, clique_num, num_transactions))


def generate_clique_num(
    file_root: str = str(UNISWAP_V2_DATA_PATH / "swap"),
    num_workers: int = mp.cpu_count(),
) -> pd.DataFrame:
    """
    Aggregate function to generate the number of cliques in the network.
    """

    # get the data path
    file_name_lst = _load_in_folder_data_lst(
        file_root=file_root,
    )

    # create a list for clique number and date
    manager = mp.Manager()
    queue = manager.Queue()

    # create a pool of workers
    pool = mp.Pool(processes=num_workers)

    # iterate through the data
    for file_name in file_name_lst:
        # submit a job to the pool
        pool.apply_async(worker, args=(file_name, queue))

    # close the pool and wait for all jobs to finish
    pool.close()
    pool.join()

    # create a dataframe
    data = []
    while not queue.empty():
        data.append(queue.get())

    df_clique = pd.DataFrame(
        data=data, columns=["Date", "clique_num", "num_transactions"]
    )

    # convert the date to datetime
    df_clique["Date"] = pd.to_datetime(df_clique["Date"])

    # sort the data
    df_clique = df_clique.sort_values(by="Date")

    return df_clique


if __name__ == "__main__":
    # load in the data
    series_df = pd.read_pickle(DATA_PATH / "herf_panel_merged.pkl")

    # convert the date column to datetime
    series_df["Date"] = pd.to_datetime(series_df["Date"])

    df_clique = generate_clique_num(
        file_root=str(UNISWAP_V2_DATA_PATH / "swap"),
    )

    df_clique["norm_clique_num"] = np.log(
        df_clique["clique_num"] / df_clique["num_transactions"]
    )

    # save the data
    df_clique.to_csv(
        "/Users/yichenluo/Desktop/ResearchAssistant/LBS/defi-econ/test/clique_num.csv",
        index=False,
    )

    # Create a figure and axis object
    fig, ax1 = plt.subplots()

    # Create a second axis object that shares the same x-axis
    ax2 = ax1.twinx()

    # Plot the first dataset on the first y-axis
    ax1.plot(df_clique["Date"], df_clique["clique_num"], "b-", label="clique_num")
    ax1.set_xlabel("x")
    ax1.set_ylabel("clique_num", color="b")

    # Plot the second dataset on the second y-axis
    ax2.plot(
        df_clique["Date"], df_clique["num_transactions"], "r-", label="num_transactions"
    )
    ax2.set_ylabel("num_transactions", color="r")

    # Set the limits of the y-axes
    ax1.set_ylim([df_clique["clique_num"].min(), df_clique["clique_num"].max()])
    ax2.set_ylim(
        [df_clique["num_transactions"].min(), df_clique["num_transactions"].max()]
    )

    # Add a legend to the plot
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    lines = lines1 + lines2
    labels = labels1 + labels2
    ax1.legend(lines, labels, loc="upper left")

    # Display the plot
    plt.show()

    # merge the data
    series_df = series_df.merge(
        df_clique,
        on="Date",
        how="left",
    )

    # save the data
    series_df.to_pickle(TABLE_PATH / "herf_panel_merged.pkl")
