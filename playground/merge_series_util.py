"""
Script to merge the series to herfindahl dataframe
"""

import ast

import pandas as pd
from tqdm import tqdm

from environ.constants import BETWEENNESS_DATA_PATH, DATA_PATH, NETWORK_DATA_PATH
from environ.utils.data_loarder import _load_in_data_lst


def _preprocess_avg_node(
    df_route: pd.DataFrame,
) -> float:
    """
    Internal function to preprocess the avg_node from full-length txn
    """

    # exclude special routes
    df_route = df_route[
        (df_route["label"] == "0") & (df_route["intermediary"] != "Error")
    ].copy()

    # convert the route to list
    df_route["route"] = df_route["route"].map(ast.literal_eval)

    # get the unique number of nodes in the list of routes
    df_route["avg_node"] = df_route["route"].map(lambda x: len(set(x)))

    # return the average number of nodes
    return df_route["avg_node"].mean()


def merge_series(
    herf_path: str = str(DATA_PATH / "herf_panel.pkl"),
    save_path: str = str(DATA_PATH / "herf_panel_merged_20230405.pkl"),
    load_path: str = str(NETWORK_DATA_PATH / "merged" / "series"),
    filter_name: str = "v2",
) -> None:
    """
    Function to merge the series to herfindahl dataframe
    """

    # load the pickle file of herfindahl panel
    herf_panel = pd.read_pickle(herf_path)

    # convert the Date index to datetime
    herf_panel["Date"] = pd.to_datetime(herf_panel["Date"])

    # get a list of all files in a specific directory
    series_files = _load_in_data_lst(
        file_root=load_path,
        filter_name=filter_name,
    )

    # list to store the date and avg_node
    date_lst = []
    avg_node_lst = []

    # load in all files and generate a panel
    for file in tqdm(series_files, desc="Loading files"):
        # load the file
        df_merge = pd.read_csv(file)

        # isolate the date
        date = file.split("_")[-1].split(".")[0]

        # append to the list
        date_lst.append(date)
        avg_node_lst.append(_preprocess_avg_node(df_merge))

    # generate a dataframe
    df_avg_node = pd.DataFrame(
        {
            "Date": date_lst,
            "avg_node": avg_node_lst,
        }
    )

    # convert the Date index to datetime
    df_avg_node["Date"] = pd.to_datetime(df_avg_node["Date"])

    # plot the avg_node
    df_avg_node.plot(x="Date", y="avg_node")

    # merge the avg_node to the herfindahl panel
    herf_panel = pd.merge(
        herf_panel,
        df_avg_node,
        on="Date",
        how="left",
    )

    # save the merged panel
    herf_panel.to_pickle(save_path)


if __name__ == "__main__":
    merge_series(
        herf_path=str(DATA_PATH / "herf_panel_merged.pkl"),
        save_path=str(DATA_PATH / "herf_panel_merged_20230405.pkl"),
        load_path=str(BETWEENNESS_DATA_PATH / "swap_route"),
        filter_name="v2v3",
    )
