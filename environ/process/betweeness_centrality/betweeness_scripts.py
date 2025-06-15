# -*- coding: utf-8 -*-
"""
Compute the betweenness centrality
"""
import json
import datetime
from os import path
import sys
import pandas as pd
import numpy as np
import yaml
from environ.utils.config_parser import Config
import warnings
from collections import Counter, deque

warnings.simplefilter("ignore", category=FutureWarning)
# warnings.filterwarnings("ignore")


def manipulate_data(
    date_label: str, top_list_label: str, uniswap_version: str
) -> pd.DataFrame:
    """
    Read and load the raw data and return the merged (if exists)
    dataset after filtering txs out of top 50 pools
    """

    # Initialize configuration
    config = Config()

    # Step 1: Read File
    if uniswap_version == "v2" or uniswap_version == "v2v3":
        # Path
        # data_file_v2 = path.join(
        #     UNISWAP_V2_DATA_PATH, str("swap/uniswap_v2_swaps_" + date_label + ".csv")
        # )
        data_file_v2 = path.join(
            config["dev"]["config"]["data"]["UNISWAP_V2_DATA_PATH"],
            str("swap/" + top_list_label + "/uniswap_v2_swaps_" + date_label + ".csv"),
        )
        pool_file_v2 = path.join(
            config["dev"]["config"]["data"]["UNISWAP_V2_DATA_PATH"],
            str("pool_list/top50_pairs_list_v2_" + top_list_label + ".csv"),
        )
        # Load
        data_v2 = pd.read_csv(data_file_v2, index_col=0)
        top_pools_v2 = pd.read_csv(pool_file_v2, index_col=0)

        # Add attribute as "Source" and "Target" for the trading direction
        data_v2["amount0"] = data_v2.apply(
            lambda x: float(x.amount0In) - float(x.amount0Out), axis=1
        )
        data_v2["amount1"] = data_v2.apply(
            lambda x: float(x.amount1In) - float(x.amount1Out), axis=1
        )
        data_v2["Source"] = data_v2.apply(
            lambda x: x.token0_symbol if float(x.amount0) > 0 else x.token1_symbol,
            axis=1,
        )
        data_v2["Pool_Out_Volume"] = data_v2.apply(
            lambda x: x.amount0 if x.Source == x.token0_symbol else x.amount1, axis=1
        )
        data_v2["Target"] = data_v2.apply(
            lambda x: x.token1_symbol if float(x.amount0) > 0 else x.token0_symbol,
            axis=1,
        )
        data_v2["Pool_In_Volume"] = data_v2.apply(
            lambda x: x.amount0 if x.Target == x.token0_symbol else x.amount1, axis=1
        )
        data_v2 = data_v2.drop(
            ["amount0In", "amount0Out", "amount1In", "amount1Out", "sender", "to"],
            axis=1,
        )
        data_v2["Version"] = "V2"

        # drop transactions which sub-transactions out of top pools
        drop_tx_list_v2 = data_v2[
            ~data_v2.pool.isin(top_pools_v2["pairAddress"].values)
        ]
        drop_tx_id_list_v2 = drop_tx_list_v2["transaction"]
        drop_tx_id_list_v2 = drop_tx_id_list_v2.unique()

    if uniswap_version == "v3" or uniswap_version == "v2v3":
        # Path
        # data_file_v3 = path.join(
        #     UNISWAP_V3_DATA_PATH, str("swap/uniswap_v3_swaps_" + date_label + ".csv")
        # )
        data_file_v3 = path.join(
            config["dev"]["config"]["data"]["UNISWAP_V3_DATA_PATH"],
            str("swap/" + top_list_label + "/uniswap_v3_swaps_" + date_label + ".csv"),
        )
        pool_file_v3 = path.join(
            config["dev"]["config"]["data"]["UNISWAP_V3_DATA_PATH"],
            str("pool_list/top50_pairs_list_v3_" + top_list_label + ".csv"),
        )
        # Load
        data_v3 = pd.read_csv(data_file_v3, index_col=0)
        top_pools_v3 = pd.read_csv(pool_file_v3, index_col=0)

        # Add attribute as "Source" and "Target" for the trading direction
        data_v3["Source"] = data_v3.apply(
            lambda x: x.token0_symbol if float(x.amount0) > 0 else x.token1_symbol,
            axis=1,
        )
        data_v3["Pool_Out_Volume"] = data_v3.apply(
            lambda x: x.amount0 if x.Source == x.token0_symbol else x.amount1, axis=1
        )
        data_v3["Target"] = data_v3.apply(
            lambda x: x.token1_symbol if float(x.amount0) > 0 else x.token0_symbol,
            axis=1,
        )
        data_v3["Pool_In_Volume"] = data_v3.apply(
            lambda x: x.amount0 if x.Target == x.token0_symbol else x.amount1, axis=1
        )
        data_v3 = data_v3.drop(["sender", "recipient", "origin"], axis=1)
        data_v3["Version"] = "V3"

        # drop transactions which sub-transactions out of top pools
        drop_tx_list_v3 = data_v3[~data_v3.pool.isin(top_pools_v3["id"].values)]
        drop_tx_id_list_v3 = drop_tx_list_v3["transaction"]
        drop_tx_id_list_v3 = drop_tx_id_list_v3.unique()

    if uniswap_version == "subgraph_v3":
        # Path
        # data_file_v3 = path.join(
        #     UNISWAP_V3_DATA_PATH, str("swap/uniswap_v3_swaps_" + date_label + ".csv")
        # )
        # output_file = "/subgraph_swap/uniswap_v3_swaps_" + date_label + ".csv"
        # data_file_v3 = config["dev"]["config"]["data"]["UNISWAP_V3_DATA_PATH"] + output_file
        # # Load
        # data_v3 = pd.read_csv(data_file_v3, index_col=0)

        json_file_path = config["dev"]["config"]["data"]["UNISWAP_V3_DATA_PATH"] + str("/subgraph_swap/uniswap_v3_swaps_" + date_label + ".json")
        with open(json_file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)


        # Notice we are NOT including the top-level 'token0' and 'token1'.
        data_v3= pd.json_normalize(
            json_data,
            sep='_', # Use our preferred separator
            meta=[
                'amount0',
                'amount1',
                'amountUSD',
                'id',
                'logIndex',
                'origin',
                'recipient',
                'sender',
                'sqrtPriceX96',
                'tick',
                # Keep the detailed token info from the 'pool' object
                ['pool', 'id'],
                ['pool', 'token0', 'decimals'],
                ['pool', 'token0', 'id'],
                ['pool', 'token0', 'name'],
                ['pool', 'token0', 'symbol'],
                ['pool', 'token1', 'decimals'],
                ['pool', 'token1', 'id'],
                ['pool', 'token1', 'name'],
                ['pool', 'token1', 'symbol'],
                # Keep the transaction info
                ['transaction', 'blockNumber'],
                ['transaction', 'id'],
                ['transaction', 'timestamp']
            ]
        )
        columns_to_drop = ['token0_id', 'token0_symbol', 'token1_id', 'token1_symbol']
        data_v3 = data_v3.drop(columns=columns_to_drop)
        data_v3 = data_v3.rename(columns={
            'pool_id': 'pool',
            'pool_token0_decimals': 'token0_decimals',
            'pool_token1_decimals': 'token1_decimals',
            'pool_token0_name': 'token0_name',
            'pool_token1_name': 'token1_name',
            'pool_token0_id': 'token0_id',
            'pool_token1_id': 'token1_id',
            'pool_token0_symbol': 'token0_symbol',
            'pool_token1_symbol': 'token1_symbol',
            'transaction_timestamp': 'timestamp',
            'transaction_id': 'transaction',
            'transaction_blockNumber': 'blockNumber',
        })
        types_to_change = {
            'amount0': 'float',
            'amount1': 'float',
            'amountUSD': 'float',
            'logIndex': 'Int64',
            'tick': 'Int64',
            'blockNumber': 'Int64',
            'timestamp': 'Int64',
        }
        data_v3 = data_v3.astype(types_to_change)

        # Add attribute as "Source" and "Target" for the trading direction
        data_v3["Source"] = data_v3.apply(
            lambda x: x.token0_symbol if float(x.amount0) > 0 else x.token1_symbol,
            axis=1,
        )
        data_v3["Pool_Out_Volume"] = data_v3.apply(
            lambda x: x.amount0 if x.Source == x.token0_symbol else x.amount1, axis=1
        )
        data_v3["Target"] = data_v3.apply(
            lambda x: x.token1_symbol if float(x.amount0) > 0 else x.token0_symbol,
            axis=1,
        )
        data_v3["Pool_In_Volume"] = data_v3.apply(
            lambda x: x.amount0 if x.Target == x.token0_symbol else x.amount1, axis=1
        )
        data_v3 = data_v3.drop(
            [
                "sender",
                "recipient",
                "origin",
                "logIndex",
                "tick",
                "sqrtPriceX96",
            ],
            axis=1,
        )
        data_v3["Version"] = "V3"
        drop_tx_id_list_v3 = []
    # Step 2: Merge data file
    if uniswap_version == "v2v3":
        # Merge
        data_merge = pd.concat([data_v2, data_v3], axis=0)
        # Filter transactions within top 50 pools
        drop_tx_id_list_merge = np.concatenate(
            (drop_tx_id_list_v2, drop_tx_id_list_v3), axis=0
        )  # merge
        drop_tx_id_list_merge = np.unique(drop_tx_id_list_merge)  # drop duplicates

    elif uniswap_version == "v2":
        data_merge = data_v2
        drop_tx_id_list_merge = drop_tx_id_list_v2

    elif uniswap_version == "v3" or uniswap_version == "subgraph_v3":
        data_merge = data_v3
        drop_tx_id_list_merge = drop_tx_id_list_v3

    # group by parent transactions
    swaps_merge = data_merge.set_index(["transaction", "pool"])

    if uniswap_version != "subgraph_v3":
        # Filter transactions within top 50 pools
        swaps_merge.drop(drop_tx_id_list_merge, level=0, axis=0, inplace=True)

    # Add the attribute as "Distance" to present the number of sub-transactions
    # swaps_merge["Distance"] = swaps_merge.apply(
    #     lambda x: len(swaps_merge.loc[x.name[0]]), axis=1
    # )

    sizes = swaps_merge.groupby(level=0).size()  # Series: tx-id → count
    swaps_merge["Distance"] = swaps_merge.index.get_level_values(
        0
    ).map(  # 0 == 'transaction'
        sizes
    )  # ← every row gets its size

    # swaps_merge = swaps_merge.dropna()
    return swaps_merge


def make_routes(swaps_merge: pd.DataFrame) -> pd.DataFrame:
    """
    Make the parent transaction to the list-like format and make labels for transaction types
    """

    # Initialize the dataframe for forming routes
    swaps_tx_route = pd.DataFrame(
        columns=[
            "id",
            "route",
            "ultimate_source",
            "ultimate_target",
            "intermediary",
            "pair",
            "pair_str",
            "volume_usd",
            "chain_length",
        ]
    )

    # Step 1: Sort tx for each parent transactions by linking tokens and trading volume
    for p_tx_index in swaps_merge.index.get_level_values(0).unique():
        parent_tx = swaps_merge.loc[p_tx_index, :]

        # Select all the sub-transactions belong to one parent transaction and sort them
        # Sort Algo: pick element from unsorted list, insert it from head OR tail in the sorted list

        # initialize sorted and unsorted list
        unsorted_parent_tx = parent_tx.copy().reset_index()
        # initialize the sorted list by setting the first element as the first element unsorted list
        sorted_parent_tx = pd.DataFrame(
            unsorted_parent_tx.head(1),
            columns=unsorted_parent_tx.head(1).columns.values,
        )
        # drop it from the unsorted list
        unsorted_parent_tx = unsorted_parent_tx.drop(
            labels=sorted_parent_tx.head(1).index, axis=0
        )

        sort_index = 0

        # control the max loop limitation for the parent transactions which can not be sorted like
        # the chain
        iter = 0

        # Do loop until sort all the sub-txs:
        while len(sorted_parent_tx) != len(parent_tx):
            iter += 1

            if iter > 50:  # control variable: assume no chain length over 50
                swaps_tx_route.loc[len(swaps_tx_route.index)] = [
                    p_tx_index,
                    "Error",
                    "Error",
                    "Error",
                    "Error",
                    "Error",
                    "Error",
                    "Error",
                    "Error",
                ]
                # print("Error: Incorrect format at transaction: ", p_tx_index)
                break

            for index, row in unsorted_parent_tx.iterrows():
                # add from head
                if float(sorted_parent_tx.iloc[0]["Pool_Out_Volume"]) + float(
                    row["Pool_In_Volume"]
                ) == 0 and str(sorted_parent_tx.iloc[0]["Source"]) == str(
                    row["Target"]
                ):
                    ## sort_index-=0
                    sorted_parent_tx.loc[-1] = row
                    unsorted_parent_tx.drop(labels=index, axis=0)
                    sorted_parent_tx = sorted_parent_tx.sort_index().reset_index(
                        drop=True
                    )
                    break

                # add from tail
                elif float(sorted_parent_tx.iloc[-1]["Pool_In_Volume"]) + float(
                    row["Pool_Out_Volume"]
                ) == 0 and str(sorted_parent_tx.iloc[0]["Target"]) == str(
                    row["Source"]
                ):
                    sorted_parent_tx.loc[len(sorted_parent_tx)] = row
                    unsorted_parent_tx.drop(labels=index, axis=0)
                    sorted_parent_tx = sorted_parent_tx.sort_index().reset_index(
                        drop=True
                    )
                    break
        # Complete sort the sub-transactions in dataframe

        # Form the sorted sequence in list and get the average trading volume for the parent transaction
        sum_volume = 0
        route_list = []

        # add the source token in each sub-transaction to the route list in the parent transaction
        for index, row in sorted_parent_tx.iterrows():
            route_list.append(row["Source"])
            sum_volume += row["amountUSD"]

        # add the last element
        route_list.append(sorted_parent_tx.iloc[-1]["Target"])

        # get the average trading volume usd in the trading chain
        avg_volume = sum_volume / len(parent_tx)

        # Theoritically, the algo complexity is (N-1)!, but in most cases it is N-1
        swaps_tx_route.loc[len(swaps_tx_route.index)] = [
            p_tx_index,
            route_list,
            route_list[0],
            route_list[-1],
            route_list[1:-1],
            [route_list[0], route_list[-1]],
            str([route_list[0], route_list[-1]]),
            avg_volume,
            len(route_list),
        ]

    # Step: make label
    swaps_tx_route["label"] = 0
    swaps_tx_route["new_list"] = 0

    for index, tx in swaps_tx_route.iterrows():
        # Label the loop transactions (contain loop) like: [A, B, C, A] "LOOP",
        # [A, B, C, A, D] "SPOON"
        # Note: "Spoon" is a special case belonging to "LOOP", so label "LOOP"
        # first then change it to "SPOON"
        if (
            len(tx["route"]) - len(list(set(tx["route"]))) != 0
            and tx["route"] != "Error"
        ):  # duplicate element exists
            swaps_tx_route.loc[index, "label"] = "loop"

            # Identity the "SPOON"
            duplicate_counter = dict(Counter(tx["route"]))
            duplicate_element = {
                key: value for key, value in duplicate_counter.items() if value > 1
            }

            new_list = []  # reformat from [A, B, C, A, D] to [[A, B, C, A], D]
            remaining = tx[
                "route"
            ]  # store the remaining except the "LOOP" part in "SPOON"

            for loop_node, element_count in duplicate_element.items():
                while element_count != 0 and len(remaining) != 0:
                    if loop_node in remaining[remaining.index(loop_node) + 1 :]:
                        loop_start_index = remaining.index(loop_node)
                        if loop_start_index > 0:
                            new_list.append(remaining[:loop_start_index])
                            remaining = remaining[loop_start_index:]

                        loop_end_index = remaining[1:].index(loop_node) + 1
                        new_list.append(remaining[: loop_end_index + 1])
                        remaining = remaining[loop_end_index + 1 :]

                        if len(remaining) != 0:
                            new_list.append(remaining)

                    element_count -= 2

            # If the the remaining part exists beyond "LOOP", label it as "SPOON"
            if len(new_list) > 1:
                swaps_tx_route.loc[index, "label"] = "spoon"

            swaps_tx_route.loc[index, "new_list"] = str(new_list)

        # Label the unformated as "Error"
        elif tx["route"] == "Error":
            swaps_tx_route.loc[index, "label"] = "Error"

    return swaps_tx_route


def make_routes_DAG(swaps_merge: pd.DataFrame) -> pd.DataFrame:
    """
    Computes transaction routes efficiently using a graph-based approach.
    Nodes in the graph are individual swaps.
    """

    processed_routes = []
    unique_parent_tx_ids = swaps_merge.index.get_level_values(0).unique()

    for p_tx_index in unique_parent_tx_ids:
        parent_tx_df = swaps_merge.loc[p_tx_index]

        # If only one sub-transaction, it's a direct swap (or part of a larger tx if index is just pool)
        # To be consistent with multi-hop, we'll process it to get the route list
        # If parent_tx_df is a Series (single row), convert to DataFrame
        if isinstance(parent_tx_df, pd.Series):
            parent_tx_df = parent_tx_df.to_frame().T
            # Need to restore the original index name if it was lost
            parent_tx_df.index.name = (
                swaps_merge.index.names[1] if len(swaps_merge.index.names) > 1 else None
            )

        # Convert sub-swaps to list of dicts for easier processing
        # Add an original_id to map back if needed, or use list index
        sub_swaps_records = []
        for i, (idx, row) in enumerate(parent_tx_df.iterrows()):
            record = row.to_dict()
            record["original_swap_id"] = i  # Using list index as id
            sub_swaps_records.append(record)

        num_swaps = len(sub_swaps_records)

        if num_swaps == 0:
            processed_routes.append(
                {
                    "id": p_tx_index,
                    "route": "Error",
                    "ultimate_source": "Error",
                    "ultimate_target": "Error",
                    "intermediary": "Error",
                    "pair": "Error",
                    "pair_str": "Error",
                    "volume_usd": 0,
                    "chain_length": 0,
                    "label": "Error",
                    "new_list": "Error",
                }
            )
            continue

        # --- Handle single swap transaction ---
        if num_swaps == 1:
            s = sub_swaps_records[0]
            route_list = [s["Source"], s["Target"]]
            avg_volume = s["amountUSD"]
            processed_routes.append(
                {
                    "id": p_tx_index,
                    "route": route_list,
                    "ultimate_source": route_list[0],
                    "ultimate_target": route_list[-1],
                    "intermediary": [],
                    "pair": [route_list[0], route_list[-1]],
                    "pair_str": str([route_list[0], route_list[-1]]),
                    "volume_usd": avg_volume,
                    "chain_length": len(route_list),
                }
            )
            continue

        # --- Graph-based approach for multi-swap transactions ---
        adj = [[] for _ in range(num_swaps)]
        in_degree = [0] * num_swaps
        tolerance = 1e-9  # For float comparisons of volumes

        # 1. Build the Swap Graph
        for i in range(num_swaps):
            for j in range(num_swaps):
                if i == j:
                    continue

                s_i = sub_swaps_records[i]
                s_j = sub_swaps_records[j]

                # Check for connection: s_i -> s_j
                # Target of s_i must be Source of s_j
                # Pool_In_Volume of s_i (what s_i outputs to user/next step)
                # must match Pool_Out_Volume of s_j (what s_j takes as input from user/previous step)
                # The definition of Pool_In_Volume and Pool_Out_Volume implies one is positive and one negative for a link.
                if (
                    str(s_i["Target"]) == str(s_j["Source"])
                    and abs(
                        float(s_i["Pool_In_Volume"]) + float(s_j["Pool_Out_Volume"])
                    )
                    < tolerance
                ):
                    adj[i].append(j)
                    in_degree[j] += 1

        # 2. Find the Start of the Route(s)
        start_nodes_indices = [i for i, degree in enumerate(in_degree) if degree == 0]

        route_indices = []
        error_occurred = False

        if not start_nodes_indices:
            # print(f"Error: No start node (cycle or disjoint) for transaction {p_tx_index}")
            error_occurred = True
        elif len(start_nodes_indices) > 1:
            # This implies multiple independent chains or a complex structure not forming a single path.
            # The original code implicitly tries to form one chain.
            # For simplicity, we can try to process the first one, or mark as error/complex.
            # print(f"Warning: Multiple start nodes for transaction {p_tx_index}. Attempting to find longest chain or first valid.")

            # Attempt to find the longest valid chain starting from any of the start nodes
            best_route_indices = []
            for start_node_idx_candidate in start_nodes_indices:
                current_path = []
                q = deque(
                    [(start_node_idx_candidate, [start_node_idx_candidate])]
                )  # (current_node, path_so_far)

                temp_longest_path = [start_node_idx_candidate]

                while q:
                    curr, path = q.popleft()

                    if len(path) > len(temp_longest_path):
                        temp_longest_path = list(path)

                    found_next = False
                    for neighbor_idx in adj[curr]:
                        if neighbor_idx not in path:  # Avoid simple cycles in path
                            new_path = list(path)  # Make a copy
                            new_path.append(neighbor_idx)
                            q.append((neighbor_idx, new_path))
                            found_next = True

                if len(temp_longest_path) > len(best_route_indices):
                    best_route_indices = temp_longest_path

            if len(best_route_indices) == num_swaps:  # Found a path covering all swaps
                route_indices = best_route_indices
            elif (
                best_route_indices
            ):  # Partial path, might be an error or complex structure
                # print(f"Warning: Could only form partial chain of length {len(best_route_indices)} for {p_tx_index}")
                route_indices = best_route_indices  # Or mark as error
                if (
                    len(route_indices) != num_swaps
                ):  # If not all swaps are covered, it's an error for simple chain assumption
                    error_occurred = True
            else:  # No valid chain found
                error_occurred = True

        else:  # Exactly one start node
            start_node_idx = start_nodes_indices[0]

            # 3. Reconstruct the Route (Path Traversal)
            # We expect a simple path covering all N nodes for a typical multi-hop.
            # This traversal assumes a mostly linear chain from the single start_node.
            current_swap_idx = start_node_idx
            route_indices.append(current_swap_idx)

            visited_in_current_path = {current_swap_idx}

            while len(route_indices) < num_swaps:
                possible_next_swaps = [
                    n for n in adj[current_swap_idx] if n not in visited_in_current_path
                ]

                if not possible_next_swaps:
                    # print(f"Error: Path broken at swap {current_swap_idx} for transaction {p_tx_index}")
                    error_occurred = True
                    break

                if len(possible_next_swaps) > 1:
                    # Branching path. The original algorithm implicitly picked one.
                    # Here, we can pick the first, or implement more complex logic if needed.
                    # print(f"Warning: Branching path at swap {current_swap_idx} for transaction {p_tx_index}. Taking first branch.")
                    # For now, let's consider this an error if we expect a single chain covering all swaps
                    error_occurred = True
                    break

                next_swap_idx = possible_next_swaps[0]

                route_indices.append(next_swap_idx)
                visited_in_current_path.add(next_swap_idx)
                current_swap_idx = next_swap_idx

            if (
                len(route_indices) != num_swaps and not error_occurred
            ):  # Path didn't cover all swaps
                # print(f"Error: Reconstructed path length {len(route_indices)} does not match num_swaps {num_swaps} for {p_tx_index}")
                error_occurred = True

        # 4. Format Output
        if not error_occurred and len(route_indices) == num_swaps:
            final_ordered_swaps = [sub_swaps_records[i] for i in route_indices]

            route_list_tokens = [s["Source"] for s in final_ordered_swaps] + [
                final_ordered_swaps[-1]["Target"]
            ]
            sum_volume_usd = sum(s["amountUSD"] for s in final_ordered_swaps)
            avg_volume_usd = sum_volume_usd / num_swaps if num_swaps > 0 else 0

            intermediary_tokens = (
                route_list_tokens[1:-1] if len(route_list_tokens) > 2 else []
            )

            processed_routes.append(
                {
                    "id": p_tx_index,
                    "route": route_list_tokens,
                    "ultimate_source": route_list_tokens[0],
                    "ultimate_target": route_list_tokens[-1],
                    "intermediary": intermediary_tokens,
                    "pair": [route_list_tokens[0], route_list_tokens[-1]],
                    "pair_str": str([route_list_tokens[0], route_list_tokens[-1]]),
                    "volume_usd": avg_volume_usd,
                    "chain_length": len(route_list_tokens),
                }
            )
        else:
            # Error occurred or path is incomplete
            processed_routes.append(
                {
                    "id": p_tx_index,
                    "route": "Error",
                    "ultimate_source": "Error",
                    "ultimate_target": "Error",
                    "intermediary": "Error",
                    "pair": "Error",
                    "pair_str": "Error",
                    "volume_usd": 0,
                    "chain_length": 0,
                }
            )

    # Convert list of dicts to DataFrame
    swaps_tx_route_df = pd.DataFrame(processed_routes)

    if swaps_tx_route_df.empty:
        # Ensure columns exist even if no routes were processed, matching original structure
        return pd.DataFrame(
            columns=[
                "id",
                "route",
                "ultimate_source",
                "ultimate_target",
                "intermediary",
                "pair",
                "pair_str",
                "volume_usd",
                "chain_length",
                "label",
                "new_list",
            ]
        )

    # Step: make label (loop, spoon, error)
    swaps_tx_route_df["label"] = 0  # Default label
    swaps_tx_route_df["new_list"] = ""  # Default

    for index, tx_info in swaps_tx_route_df.iterrows():
        route_data = tx_info["route"]

        if route_data == "Error":
            swaps_tx_route_df.loc[index, "label"] = "Error"
            swaps_tx_route_df.loc[index, "new_list"] = "Error"
            continue

        # Label the loop transactions
        if len(route_data) - len(set(route_data)) != 0:  # Duplicate element exists
            swaps_tx_route_df.loc[index, "label"] = "loop"

            # Identify "SPOON"
            duplicate_counter = Counter(route_data)
            # Elements that appear more than once and could form the core of a loop
            loop_core_candidates = {k: v for k, v in duplicate_counter.items() if v > 1}

            parsed_spoon_list = []
            temp_route = list(route_data)  # Make a mutable copy

            # This logic tries to find the first occurring loop and segment it.
            # More complex overlapping loops might need more sophisticated parsing.
            processed_loop_segment = False
            for loop_node_candidate in route_data:  # Iterate in order of appearance
                if loop_node_candidate not in loop_core_candidates:
                    continue

                if (
                    loop_core_candidates[loop_node_candidate] < 2
                ):  # Already processed enough instances
                    continue

                try:
                    first_occurrence = temp_route.index(loop_node_candidate)
                    # Find the next occurrence of this node to form the loop
                    second_occurrence = temp_route.index(
                        loop_node_candidate, first_occurrence + 1
                    )

                    # We found a loop segment
                    # Part before loop
                    if first_occurrence > 0:
                        parsed_spoon_list.append(temp_route[:first_occurrence])

                    # The loop itself
                    loop_segment = temp_route[first_occurrence : second_occurrence + 1]
                    parsed_spoon_list.append(loop_segment)

                    # Part after loop
                    remaining_after_loop = temp_route[second_occurrence + 1 :]
                    if remaining_after_loop:
                        parsed_spoon_list.append(remaining_after_loop)

                    processed_loop_segment = True
                    break  # Processed the first significant loop for spoon structure

                except (
                    ValueError
                ):  # Node not found again, shouldn't happen if count > 1
                    continue

            if processed_loop_segment and len(parsed_spoon_list) > 1:
                # Check if there's content before or after the identified primary loop segment
                is_spoon = False
                if len(parsed_spoon_list[0]) > 0 and isinstance(
                    parsed_spoon_list[0][0], str
                ):  # Content before loop
                    is_spoon = True
                if (
                    len(parsed_spoon_list) > 1
                    and isinstance(parsed_spoon_list[-1], list)
                    and len(parsed_spoon_list[-1]) > 0
                ):  # Content after loop
                    is_spoon = True

                # A simple check: if the parsed list has more than one segment (the loop itself, and something before/after)
                if len(parsed_spoon_list) > 1 and any(
                    isinstance(seg, list) and len(seg) > 0
                    for seg_idx, seg in enumerate(parsed_spoon_list)
                    if seg != loop_segment
                ):
                    is_spoon = True

                if is_spoon:
                    swaps_tx_route_df.loc[index, "label"] = "spoon"
                    swaps_tx_route_df.loc[index, "new_list"] = str(parsed_spoon_list)
                else:  # It's a loop, but not clearly a spoon by this logic
                    swaps_tx_route_df.loc[index, "new_list"] = str(
                        [route_data]
                    )  # Store original loop

            elif (
                swaps_tx_route_df.loc[index, "label"] == "loop"
            ):  # It's a loop, but not parsed as spoon
                swaps_tx_route_df.loc[index, "new_list"] = str([route_data])

    return swaps_tx_route_df


def compute_betweenness_count(swaps_tx_route: pd.DataFrame) -> pd.DataFrame:
    """
    Compute the betweenness centrality (count based) and return the results as dataframe
    """

    # Exclude "LOOP" AND "SPOON"
    count_based_set = swaps_tx_route[swaps_tx_route["label"] == 0].copy()

    # Exclude Error
    count_based_set = count_based_set[count_based_set["intermediary"] != "Error"]

    node_set_count = pd.concat(
        [count_based_set["ultimate_source"], count_based_set["ultimate_target"]],
        ignore_index=True,
    ).unique()

    # Initialize the betweenness centrality dataframe
    betweenness_score_count = pd.DataFrame(
        {"node": node_set_count, "betweenness_centrality_count": 0}
    )

    # Calculate the betweenness centrality
    for node in node_set_count:
        # Calculate the betweenness centrality
        denominator_df = count_based_set.loc[
            (count_based_set["ultimate_source"] != node)
            & (count_based_set["ultimate_target"] != node)
        ]

        denominator = denominator_df.shape[0]
        numerator = denominator_df.loc[
            [node in inter_list for inter_list in denominator_df["intermediary"]]
        ].shape[0]

        betweenness_score_count.loc[
            betweenness_score_count["node"] == node, "betweenness_centrality_count"
        ] = (numerator / denominator)

    return betweenness_score_count


def compute_betweenness_volume(swaps_tx_route: pd.DataFrame) -> pd.DataFrame:
    """
    Compute the betweenness centrality (volume weighted) and return the results as dataframe
    """
    # Exclude "LOOP" AND "SPOON"
    volume_based_set = swaps_tx_route[swaps_tx_route["label"] == 0].copy()

    # Exclude Error
    volume_based_set = volume_based_set[volume_based_set["intermediary"] != "Error"]

    node_set_count = pd.concat(
        [volume_based_set["ultimate_source"], volume_based_set["ultimate_target"]],
        ignore_index=True,
    ).unique()

    # Initialize the betweenness centrality dataframe
    betweenness_score_volume = pd.DataFrame(
        {"node": node_set_count, "betweenness_centrality_volume": 0}
    )

    # Calculate the betweenness centrality
    for node in node_set_count:
        # Calculate the betweenness centrality
        denominator_df = volume_based_set.loc[
            (volume_based_set["ultimate_source"] != node)
            & (volume_based_set["ultimate_target"] != node)
        ]

        denominator = denominator_df["volume_usd"].apply(float).sum()

        numerator = (
            denominator_df.loc[
                [node in inter_list for inter_list in denominator_df["intermediary"]],
                "volume_usd",
            ]
            .apply(float)
            .sum()
        )

        betweenness_score_volume.loc[
            betweenness_score_volume["node"] == node, "betweenness_centrality_volume"
        ] = (numerator / denominator)

    return betweenness_score_volume


def get_betweenness_centrality(
    date_label: str, top_list_label: str, uniswap_version: str
) -> None:
    """
    Merge data, make routes, and compute betweenness centrality
    """

    # Initialize configuration
    config = Config()

    swaps_merge = manipulate_data(date_label, top_list_label, uniswap_version)
    swaps_tx_route = make_routes_DAG(swaps_merge)

    # Store to file
    tx_route_file_name = path.join(
        config["dev"]["config"]["data"]["BETWEENNESS_DATA_PATH"],
        "swap_route/DAG_swaps_tx_route_" + uniswap_version + "_" + date_label + ".csv",
    )
    # Write dataframe to csv
    swaps_tx_route.to_csv(tx_route_file_name)

    betweenness_score_count = compute_betweenness_count(swaps_tx_route)
    betweenness_score_volume = compute_betweenness_volume(swaps_tx_route)

    # compare_table = betweenness_score_count.sort_values(
    #     by="betweenness_centrality_count", ascending=False
    # ).join(betweenness_score_volume)

    compare_table = betweenness_score_count.merge(
        betweenness_score_volume, on="node", how="left", validate="1:1"
    )
    compare_table.sort_values(
        by="betweenness_centrality_count", ascending=False, inplace=True
    )

    # Store to file
    betweenness_file_name = path.join(
        config["dev"]["config"]["data"]["BETWEENNESS_DATA_PATH"],
        "betweenness/betweenness_centrality_"
        + uniswap_version
        + "_"
        + date_label
        + ".csv",
    )
    # Write dataframe to csv
    compare_table.to_csv(betweenness_file_name)


# if __name__ == "__main__":

#     from multiprocessing import Pool
#     from functools import partial

#     involve_version = "v2"  # candidate: v2, v3, v2v3

#     top50_list_label = "2020JUN"
#     # Data output include start_date, exclude end_date
#     start_date = datetime.datetime(2020, 6, 1, 0, 0)
#     end_date = datetime.datetime(2020, 7, 1, 0, 0)

#     # list for multiple dates
#     date_list = []
#     for i in range((end_date - start_date).days):
#         date = start_date + datetime.timedelta(i)
#         date_str = date.strftime("%Y%m%d")
#         date_list.append(date_str)

#     # Multiprocess
#     p = Pool()
#     p.map(
#         partial(
#             get_betweenness_centrality,
#             top_list_label=top50_list_label,
#             uniswap_version=involve_version,
#         ),
#         date_list,
#     )

if __name__ == "__main__":

    from multiprocessing import Pool
    from functools import partial

    involve_version = "subgraph_v3"  # candidate: v2, v3, v2v3

    top50_list_label = "2021MAY"
    # Data output include start_date, exclude end_date
    start_date = datetime.datetime(2021, 5, 4, 0, 0)
    end_date = datetime.datetime(2023, 1, 31, 0, 0)

    # list for multiple dates
    date_list = []
    for i in range((end_date - start_date).days):
        date = start_date + datetime.timedelta(i)
        date_str = date.strftime("%Y-%m-%d")
        date_list.append(date_str)

    # Multiprocess
    p = Pool()
    p.map(
        partial(
            get_betweenness_centrality,
            top_list_label=top50_list_label,
            uniswap_version=involve_version,
        ),
        date_list,
    )
