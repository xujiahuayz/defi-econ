# -*- coding: utf-8 -*-
"""
Plot the network graph based on processed network dataset
"""

from os import path
import datetime
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
from defi_econ.constants import NETWORK_DATA_PATH


def plot_network(date) -> None:
    """
    Plot the network by networkx
    """
    date_str = date.strftime("%Y%m%d")

    # Define the network instance, for directional graph
    G = nx.MultiDiGraph()

    # Node data
    node_data = pd.read_csv(
        path.join(NETWORK_DATA_PATH, "primary_tokens_" + date_str + ".csv"), index_col=0
    )

    for index, row in node_data.iterrows():
        token = row["token"]
        total_tvl = row["total_tvl"]
        G.add_node(token, tvl=total_tvl)

    # Edge data
    edge_data = pd.read_csv(
        path.join(NETWORK_DATA_PATH, "inout_flow_tokens_" + date_str + ".csv"),
        index_col=0,
    )

    for index, row in edge_data.iterrows():
        source = row["Source"]
        target = row["Target"]
        dir_volume = row["Volume"]
        G.add_edge(source, target, weight=dir_volume)

    # Get the lists of weights for node sizes and edge widths
    node_sizes = nx.get_node_attributes(G, "tvl")
    edge_widths = nx.get_edge_attributes(G, "weight")

    # Scale the varaibles to fit the node and edge parameters
    node_sizes_scaler = 300000
    edge_widths_scaler = 20000000

    # Plot the network
    pos = nx.circular_layout(G)
    plt.figure(figsize=(16, 12))
    # nx.draw(G, node_size=node_sizes, pos=pos, with_labels = True, connectionstyle='arc3,rad=0.3')
    nx.draw_networkx_nodes(
        G, pos, node_size=[i / node_sizes_scaler for i in list(node_sizes.values())]
    )
    nx.draw_networkx_edges(
        G,
        pos,
        connectionstyle="arc3,rad=0.2",
        width=[i / edge_widths_scaler for i in list(edge_widths.values())],
    )
    nx.draw_networkx_labels(G, pos, font_size=14, verticalalignment="bottom")

    plt.savefig(path.join(NETWORK_DATA_PATH, "network_" + date_str + ".jpg"))


if __name__ == "__main__":
    target_date = datetime.datetime(2022, 5, 31, 0, 0)
    plot_network(target_date)
