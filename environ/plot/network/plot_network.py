# -*- coding: utf-8 -*-
"""
Plot the network graph based on processed network dataset
"""

from os import path
import datetime
import networkx as nx
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from environ.utils.config_parser import Config


def plot_network(date: datetime, uniswap_version: str) -> None:
    """
    Plot the network by networkx
    """
    # Initialize configuration
    config = Config()

    date_str = date.strftime("%Y%m%d")

    # Define the network instance, for directional graph
    G = nx.MultiDiGraph()

    # token data
    token_data = pd.read_csv(
        path.join(
            config["dev"]["config"]["data"]["NETWORK_DATA_PATH"],
            uniswap_version
            + "/primary_tokens/primary_tokens_"
            + uniswap_version
            + "_"
            + date_str
            + ".csv",
        ),
        index_col=0,
    )

    # Change data format at the presentation layer
    if uniswap_version == "v2":
        token_data["token_symbol"] = [i[12:-2] for i in token_data["token"]]
        token_data = token_data.drop(columns=["token"]).rename(
            columns={"token_symbol": "token"}
        )[["token", "total_tvl"]]

    # token library
    token_lib = pd.read_csv(
        path.join(
            config["dev"]["config"]["data"]["NETWORK_DATA_PATH"],
            "token_library_" + uniswap_version + ".csv",
        ),
        index_col=0,
    )

    # label stable coin or non-stable coin
    token_data = token_data.join(token_lib, on="token", how="left")
    token_data = token_data.drop(columns=["eigenvector_centrality"])
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

    # Node data
    # node_data = pd.read_csv(
    #     path.join(
    #         config["dev"]["config"]["data"]["NETWORK_DATA_PATH"],
    #         "primary_tokens_" + uniswap_version + "_" + date_str + ".csv",
    #     ),
    #     index_col=0,
    # )

    for _, row in node_data.iterrows():
        token = row["token"]
        # total_tvl = row["total_tvl"]
        # stable = row["stable"]
        G.add_node(token, tvl=row["total_tvl"], stable=row["stable"])

    # Edge data
    edge_data = pd.read_csv(
        path.join(
            config["dev"]["config"]["data"]["NETWORK_DATA_PATH"],
            uniswap_version
            + "/inout_flow/inout_flow_tokens_"
            + uniswap_version
            + "_"
            + date_str
            + ".csv",
        ),
        index_col=0,
    )

    # Change data format at the presentation layer
    if uniswap_version == "v2":
        edge_data["Source_symbol"] = [i[12:-2] for i in edge_data["Source"]]
        edge_data = edge_data.drop(columns=["Source"]).rename(
            columns={"Source_symbol": "Source"}
        )
        edge_data["Target_symbol"] = [i[12:-2] for i in edge_data["Target"]]
        edge_data = edge_data.drop(columns=["Target"]).rename(
            columns={"Target_symbol": "Target"}
        )
        edge_data = edge_data[["Source", "Target", "Volume"]]

    for _, row in edge_data.iterrows():
        source = row["Source"]
        target = row["Target"]
        dir_volume = row["Volume"]
        G.add_edge(source, target, weight=dir_volume)

    # Get the lists of weights for node sizes and edge widths
    node_sizes = nx.get_node_attributes(G, "tvl")
    node_colors = nx.get_node_attributes(G, "stable")
    edge_widths = nx.get_edge_attributes(G, "weight")

    # Scale the varaibles to fit the node and edge parameters
    if uniswap_version == "v2":
        node_sizes_scaler = 300000
        # 5x arc line width than v3
        # edge_widths_scaler = 2000000  # linear scaler
        # 2x arc line width than v3?
        edge_widths_scaler = 500
    elif uniswap_version == "v3":
        node_sizes_scaler = 300000
        # edge_widths_scaler = 10000000 # linear scaler
        edge_widths_scaler = 500

    # Plot the network
    pos = nx.circular_layout(G)
    plt.figure(figsize=(16, 12))

    plt.title(
        label="Directional Trading Volume among Top 50 Pools in Uniswap "
        + uniswap_version
        + " at "
        + date_str,
        fontdict={"fontsize": 12},
        loc="center",
    )
    # nx.draw(G, node_size=node_sizes, pos=pos, with_labels = True, connectionstyle='arc3,rad=0.3')
    nx.draw_networkx_nodes(
        G,
        pos,
        node_size=[i / node_sizes_scaler for i in list(node_sizes.values())],
        node_color=[
            "tab:orange" if i == 1 else "tab:blue" for i in list(node_colors.values())
        ],
        alpha=0.8,
    )

    nx.draw_networkx_edges(
        G,
        pos,
        connectionstyle="arc3,rad=0.2",
        arrowstyle="-|>",
        arrowsize=20,
        alpha=0.3,
        width=[np.sqrt(i) / edge_widths_scaler for i in list(edge_widths.values())],
    )
    nx.draw_networkx_labels(G, pos, font_size=18, verticalalignment="bottom")

    plt.savefig(
        path.join(
            config["dev"]["config"]["data"]["NETWORK_DATA_PATH"],
            uniswap_version
            + "/network_graph/network_"
            + uniswap_version
            + "_"
            + date_str
            + ".jpg",
        )
    )

    plt.close()

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
            uniswap_version
            + "/inflow_centrality/centrality_"
            + uniswap_version
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
            uniswap_version
            + "/outflow_centrality/centrality_"
            + uniswap_version
            + "_"
            + date_str
            + ".csv",
        )
    )
