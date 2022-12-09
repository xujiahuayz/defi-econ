# -*- coding: utf-8 -*-
"""
Compute the betweenness centrality
"""

from os import path
from defi_econ.constants import UNISWAP_V3_DATA_PATH
from defi_econ.constants import UNISWAP_V2_DATA_PATH
from defi_econ.constants import BETWEENNESS_DATA_PATH
from collections import Counter

import pandas as pd
import numpy as np
import datetime


def manipulate_data(
    date_label: str, top_list_label: str, uniswap_version: str
) -> pd.DataFrame:
    """
    Read and load the raw data and return the merged (if exists) dataset after filtering txs out of top 50 pools
    """

    # Step 1: Read File
    if uniswap_version == "v2" or uniswap_version == "v2v3":
        # Path
        data_file_v2 = path.join(
            UNISWAP_V2_DATA_PATH, str("swap/uniswap_swaps_v2_" + date_label + ".csv")
        )
        pool_file_v2 = path.join(
            UNISWAP_V2_DATA_PATH,
            str("pool_list/top50_pairs_list_v2_" + top_list_label + ".csv"),
        )
        # Load
        data_v2 = pd.read_csv(data_file_v2, index_col=0)
        top_pools_v2 = pd.read_csv(pool_file_v2, index_col=0)

        # Add attribute as "Source" and "Target" for the trading direction
        data_v2["amount0"] = data_v2.apply(lambda x: x.amount0In - x.amount0Out, axis=1)
        data_v2["amount1"] = data_v2.apply(lambda x: x.amount1In - x.amount1Out, axis=1)
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
        data_file_v3 = path.join(
            UNISWAP_V3_DATA_PATH, str("swap/uniswap_swaps_v3_" + date_label + ".csv")
        )
        pool_file_v3 = path.join(
            UNISWAP_V3_DATA_PATH, str("top50_pairs_list_v3_" + top_list_label + ".csv")
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

    elif uniswap_version == "v3":
        data_merge = data_v3
        drop_tx_id_list_merge = drop_tx_id_list_v3

    # group by parent transactions
    swaps_merge = data_merge.set_index(["transaction", "pool"])

    # Filter transactions within top 50 pools
    swaps_merge.drop(drop_tx_id_list_merge, level=0, axis=0, inplace=True)

    # Add the attribute as "Distance" to present the number of sub-transactions
    swaps_merge["Distance"] = swaps_merge.apply(
        lambda x: len(swaps_merge.loc[x.name[0]]), axis=1
    )

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

        iter = 0  # control the max loop limatation for the parent transactions which can not be sorted like the chain

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
        # Label the loop transactions (contain loop) like: [A, B, C, A] "LOOP", [A, B, C, A, D] "SPOON"
        # Note: "Spoon" is a special case belonging to "LOOP", so label "LOOP" first then change it to "SPOON"
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


def compute_betweenness_count(swaps_tx_route: pd.DataFrame) -> pd.DataFrame:
    """
    Compute the betweenness centrality (count based) and return the results as dataframe
    """

    # Exclude "LOOP" AND "SPOON"
    count_based_set = swaps_tx_route[swaps_tx_route["label"] == 0]
    # Get all involving tokens as nodes
    node_set_count = (
        count_based_set["ultimate_source"]
        .append(count_based_set["ultimate_target"])
        .unique()
    )

    # Step 1: sigma
    # Dataframe for the sigma of count based set
    sigma_count_value = count_based_set["pair"].value_counts()
    sigma_count = pd.DataFrame(
        {"pair": sigma_count_value.index, "sigma_count": sigma_count_value.values}
    )

    sigma_count["pair_index"] = sigma_count["pair"].apply(
        lambda x: str(x)
    )  # use str-format as index (list-format can not be indexed)
    sigma_count = sigma_count.set_index("pair_index")

    # Step 2: conditional sigma
    # Dataframe for the conditional sigma of count based set
    sigma_con_count = pd.DataFrame(
        columns=["pair_index", "node", "sigma_conditional_count"]
    )
    sigma_con_count = sigma_con_count.set_index(["pair_index", "node"])

    # Initialize
    for index, row in sigma_count.iterrows():
        for node in node_set_count:
            sigma_con_count.loc[(str(row["pair"]), node), "sigma_conditional_count"] = 0

    # Compute
    for index, row in count_based_set.iterrows():
        if len(row["intermediary"]) > 0:
            for inter_node in row["intermediary"]:
                sigma_con_count.loc[
                    (str(row["pair"]), inter_node), "sigma_conditional_count"
                ] += 1

    # Step 3: betweenness centrality of each node
    # Dataframe for the scores of betweenness centrality (by nodes) of count based set
    # Initialize
    betweenness_score_count = pd.DataFrame(
        {"node": node_set_count, "betweenness_centrality_count": 0}
    )
    betweenness_score_count = betweenness_score_count.set_index("node")

    # Compute for node n
    for node in node_set_count:
        sigma_sum = 0
        sigma_con_sum = 0

        # for each pair<s,t>
        for pair_index, row in sigma_count.iterrows():
            sigma_st = sigma_count.loc[str(pair_index), "sigma_count"]
            sigma_con_stn = sigma_con_count.loc[
                (str(pair_index), str(node)), "sigma_conditional_count"
            ]

            sigma_sum += sigma_st
            sigma_con_sum += sigma_con_stn

        betweenness_score_n_count = sigma_con_sum / sigma_sum
        # store the value
        betweenness_score_count.loc[
            str(node), "betweenness_centrality_count"
        ] = betweenness_score_n_count

    return betweenness_score_count


def compute_betweenness_volume(swaps_tx_route: pd.DataFrame) -> pd.DataFrame:
    """
    Compute the betweenness centrality (volume weighted) and return the results as dataframe
    """

    # Exclude "LOOP" AND "SPOON"
    volume_based_set = swaps_tx_route[swaps_tx_route["label"] == 0]
    # Get all involving tokens as nodes
    node_set_volume = (
        volume_based_set["ultimate_source"]
        .append(volume_based_set["ultimate_target"])
        .unique()
    )

    # Step 1: sigma
    # Dataframe for the sigma of count based set
    sigma_volume = (
        volume_based_set[["pair_str", "volume_usd"]].groupby("pair_str").agg("sum")
    )
    sigma_volume.index = sigma_volume.index.set_names(["pair_index"])
    sigma_volume.rename(columns={"volume_usd": "sigma_volume"}, inplace=True)

    # Step 2: conditional sigma
    # Dataframe for the conditional sigma of count based set
    sigma_con_volume = pd.DataFrame(
        columns=["pair_index", "node", "sigma_conditional_volume"]
    )
    sigma_con_volume = sigma_con_volume.set_index(["pair_index", "node"])

    # Initialize
    for index, row in sigma_volume.iterrows():
        for node in node_set_volume:
            sigma_con_volume.loc[(str(index), node), :] = 0

    # Compute
    for index, row in volume_based_set.iterrows():
        if len(row["intermediary"]) > 0:
            for inter_node in row["intermediary"]:
                sigma_con_volume.loc[
                    (str(row["pair"]), inter_node), "sigma_conditional_volume"
                ] += row["volume_usd"]

    # Step 3: betweenness centrality of each node
    # Dataframe for the scores of betweenness centrality (by nodes) of count based set

    # Initialize
    betweenness_score_volume = pd.DataFrame(
        {"node": node_set_volume, "betweenness_centrality_volume": 0}
    )
    betweenness_score_volume = betweenness_score_volume.set_index("node")

    # Compute for node n
    for node in node_set_volume:
        sigma_sum = 0
        sigma_con_sum = 0

        # for each pair<s,t>
        for pair_index, row in sigma_volume.iterrows():
            sigma_st = sigma_volume.loc[str(pair_index), "sigma_volume"]
            sigma_con_stn = sigma_con_volume.loc[
                (str(pair_index), str(node)), "sigma_conditional_volume"
            ]

            sigma_sum += sigma_st
            sigma_con_sum += sigma_con_stn

        betweenness_score_n_volume = sigma_con_sum / sigma_sum
        # store the value
        betweenness_score_volume.loc[
            str(node), "betweenness_centrality_volume"
        ] = betweenness_score_n_volume

    return betweenness_score_volume


def get_betweenness_centrality(
    date_label: str, top_list_label: str, uniswap_version: str
) -> None:
    """
    Merge data, make routes, and compute betweenness centrality
    """
    swaps_merge = manipulate_data(date_label, top_list_label, uniswap_version)
    swaps_tx_route = make_routes(swaps_merge)

    # Store to file
    tx_route_file_name = path.join(
        BETWEENNESS_DATA_PATH,
        "swap_route/swaps_tx_route_" + uniswap_version + "_" + "date_label" + ".csv",
    )
    # Write dataframe to csv
    swaps_tx_route.to_csv(tx_route_file_name)

    betweenness_score_count = compute_betweenness_count(swaps_tx_route)
    betweenness_score_volume = compute_betweenness_volume(swaps_tx_route)

    compare_table = betweenness_score_count.sort_values(
        by="betweenness_centrality_count", ascending=False
    ).join(betweenness_score_volume)

    # Store to file
    betweenness_file_name = path.join(
        BETWEENNESS_DATA_PATH,
        "betweenness/betweenness_centrality_"
        + uniswap_version
        + "_"
        + date_label
        + ".csv",
    )
    # Write dataframe to csv
    compare_table.to_csv(betweenness_file_name)


if __name__ == "__main__":
    # involve_version = "v2v3"  # candidate: v2, v3, v2v3
    # target_date = datetime.datetime(2022, 7, 31, 0, 0)
    # date = "2022TEST"
    # get_betweenness_centrality(
    #     date_label=date,
    #     top_list_label=top50_list_label,
    #     uniswap_version=involve_version,
    # )

    involve_version = "v2v3"  # candidate: v2, v3, v2v3

    top50_list_label = "2022JUL"
    # Data output include start_date, exclude end_date
    start_date = datetime.datetime(2022, 7, 1, 0, 0)
    end_date = datetime.datetime(2022, 8, 1, 0, 0)

    # list for multiple dates
    date_list = []
    for i in range((end_date - start_date).days):
        date = start_date + datetime.timedelta(i)
        date_list.append(date)

    # for each day
    for date in date_list:
        date_str = date.strftime("%Y%m%d")
        get_betweenness_centrality(
            date_label=date_str,
            top_list_label=top50_list_label,
            uniswap_version=involve_version,
        )
        print("-----Complete betweenness centrality in " + date_str + "-----")
