"""
Function to plot the sankey diagram
"""
import multiprocessing as mp
import warnings
from ast import literal_eval
from glob import glob
from tqdm import tqdm

import pandas as pd
import plotly.graph_objects as go

from environ.constants import BETWEENNESS_DATA_PATH, FIGURE_PATH, KEY_TOKEN_LIST

warnings.filterwarnings("ignore")


def plot_sankey(
    data_path: str,
    save_path: str,
):
    """
    Function to plot the sankey diagram
    """

    # load the data
    data = pd.read_csv(
        data_path,
        index_col=0,
    )

    # exclude the label with error
    data = data[data["label"] != "Error"]

    # convert the voliume_usd columns to float
    data["volume_usd"] = data["volume_usd"].apply(float)

    # convert the intermediary columns to list
    data["intermediary"] = data["intermediary"].apply(literal_eval)

    # convert the route columns to list
    data["route"] = data["route"].apply(literal_eval)

    key_token_list = KEY_TOKEN_LIST + ["Others"]

    # get the unique list of ultimate_source, ultimate_target, and intermediary
    unique_lst = (
        [f"{i}_S" for i in key_token_list]
        + [f"{i}_B" for i in key_token_list]
        + [f"{i}_T" for i in key_token_list]
    )

    # lists to store the source and target
    source_lst = []
    target_lst = []
    value_lst = []

    # iterate through the dataframe
    for _, row in data.iterrows():
        source_idx = (
            unique_lst.index(f"{row['ultimate_source']}_S")
            if row["ultimate_source"] in key_token_list
            else unique_lst.index("Others_S")
        )
        target_idx = (
            unique_lst.index(f"{row['ultimate_target']}_T")
            if row["ultimate_target"] in key_token_list
            else unique_lst.index("Others_T")
        )

        if len(row["intermediary"]) != 0:
            for i in row["intermediary"]:
                # get the source and between index

                between_idx = (
                    unique_lst.index(f"{i}_B")
                    if i in key_token_list
                    else unique_lst.index("Others_B")
                )
                source_lst.append(source_idx)
                target_lst.append(between_idx)
                value_lst.append(row["volume_usd"])
                source_lst.append(between_idx)
                target_lst.append(target_idx)
                value_lst.append(row["volume_usd"])

        else:
            source_lst.append(source_idx)
            target_lst.append(target_idx)
            value_lst.append(row["volume_usd"])

    # create a dataframe
    df_sankey = pd.DataFrame(
        {
            "source": source_lst,
            "target": target_lst,
            "value": value_lst,
        }
    )

    # group by the source and target
    df_sankey = df_sankey.groupby(["source", "target"])["value"].sum().reset_index()

    # remove _S, _B, _T in the unique list
    unique_lst = [i.split("_")[0] for i in unique_lst]

    # color list for the sankey diagram
    color_lst = (
        ["blue" for i in range(len(key_token_list))]
        + ["green" for i in range(len(key_token_list))]
        + ["yellow" for i in range(len(key_token_list))]
    )

    # create the figure
    fig = go.Figure(
        data=[
            go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=unique_lst,
                    color=color_lst,
                ),
                link=dict(
                    source=df_sankey["source"],
                    target=df_sankey["target"],
                    value=df_sankey["value"],
                ),
            )
        ]
    )

    # save the figure into jpg
    fig.write_image(save_path)


def worker(data_path, queue):
    """
    Multiprocessing workers
    """

    # load the data
    data = pd.read_csv(
        data_path,
        index_col=0,
    )

    # exclude the label with error
    data = data[data["label"] != "Error"]

    # convert the voliume_usd columns to float
    data["volume_usd"] = data["volume_usd"].apply(float)

    # convert the intermediary columns to list
    data["intermediary"] = data["intermediary"].apply(literal_eval)

    # convert the route columns to list
    data["route"] = data["route"].apply(literal_eval)

    key_token_list = KEY_TOKEN_LIST + ["Others"]

    # get the unique list of ultimate_source, ultimate_target, and intermediary
    unique_lst = (
        [f"{i}_S" for i in key_token_list]
        + [f"{i}_B" for i in key_token_list]
        + [f"{i}_T" for i in key_token_list]
    )

    # lists to store the source and target
    source_lst = []
    target_lst = []
    value_lst = []

    # iterate through the dataframe
    for _, row in data.iterrows():
        source_idx = (
            unique_lst.index(f"{row['ultimate_source']}_S")
            if row["ultimate_source"] in key_token_list
            else unique_lst.index("Others_S")
        )
        target_idx = (
            unique_lst.index(f"{row['ultimate_target']}_T")
            if row["ultimate_target"] in key_token_list
            else unique_lst.index("Others_T")
        )

        if len(row["intermediary"]) != 0:
            for i in row["intermediary"]:
                # get the source and between index

                between_idx = (
                    unique_lst.index(f"{i}_B")
                    if i in key_token_list
                    else unique_lst.index("Others_B")
                )
                source_lst.append(source_idx)
                target_lst.append(between_idx)
                value_lst.append(row["volume_usd"])
                source_lst.append(between_idx)
                target_lst.append(target_idx)
                value_lst.append(row["volume_usd"])

        else:
            source_lst.append(source_idx)
            target_lst.append(target_idx)
            value_lst.append(row["volume_usd"])

    # append the data to the queue
    queue.put((source_lst, target_lst, value_lst))


def generate_sankey_plot():
    """
    Function to generate the sankey plot
    """

    # iterate through the uni_version
    for uni_version in tqdm(["v2", "v3", "merged"]):
        # load the data in the betweenness data path
        data_lst = glob(f"{BETWEENNESS_DATA_PATH}/swap_route/*.csv")

        # filter the data_lst
        data_lst = (
            [i for i in data_lst if i.split("/")[-1].split("_")[-2] == uni_version]
            if uni_version != "merged"
            else [i for i in data_lst if i.split("/")[-1].split("_")[-2] == "v2v3"]
        )

        # create a list for clique number and date
        manager = mp.Manager()
        queue = manager.Queue()

        # create a pool of workers
        pool = mp.Pool(processes=mp.cpu_count())

        # iterate through the data_lst
        for data_path in data_lst:
            # apply the worker
            pool.apply_async(worker, args=(data_path, queue))

        # close the pool
        pool.close()
        pool.join()

        # create a list to store the data
        data_lst = []

        # iterate through the queue
        while not queue.empty():
            data_lst.append(queue.get())

        # create a list to store the source, target, and value
        source_lst = []
        target_lst = []
        value_lst = []

        # iterate through the data_lst
        for i in data_lst:
            source_lst += i[0]
            target_lst += i[1]
            value_lst += i[2]

        # create a dataframe
        df_sankey = pd.DataFrame(
            {
                "source": source_lst,
                "target": target_lst,
                "value": value_lst,
            }
        )
        # group by the source and target
        df_sankey = df_sankey.groupby(["source", "target"])["value"].sum().reset_index()

        key_token_list = KEY_TOKEN_LIST + ["Others"]

        # get the unique list of ultimate_source, ultimate_target, and intermediary
        unique_lst = (
            [f"{i}_S" for i in key_token_list]
            + [f"{i}_B" for i in key_token_list]
            + [f"{i}_T" for i in key_token_list]
        )

        # remove _S, _B, _T in the unique list
        unique_lst = [i.split("_")[0] for i in unique_lst]

        # color list for the sankey diagram
        color_lst = (
            ["blue" for _ in range(len(key_token_list))]
            + ["green" for _ in range(len(key_token_list))]
            + ["yellow" for _ in range(len(key_token_list))]
        )

        # create the figure
        fig = go.Figure(
            data=[
                go.Sankey(
                    node=dict(
                        pad=15,
                        thickness=20,
                        line=dict(color="black", width=0.5),
                        label=unique_lst,
                        color=color_lst,
                    ),
                    link=dict(
                        source=df_sankey["source"],
                        target=df_sankey["target"],
                        value=df_sankey["value"],
                    ),
                )
            ]
        )

        # save the figure into jpg
        fig.write_image(f"{FIGURE_PATH}/{uni_version}_sankey_total.pdf")
