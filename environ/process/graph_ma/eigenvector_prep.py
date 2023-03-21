"""
Script to preprocess the data for the moving average plot
"""

import glob
from pathlib import Path
from typing import Literal

import pandas as pd

from environ.constants import NETWORK_DATA_PATH, KEY_TOKEN_LIST, PLOT_DATA_PATH


def eigenvector_prep(
    graph_type: Literal["eigen_in", "eigen_out"],
    source: Literal["v2", "v3", "merged"],
) -> None:
    """
    Function to prepare the data for the eigenvector centrality graph
    """

    if graph_type == "eigen_in":
        path = rf"{NETWORK_DATA_PATH}/{source}/inflow_centrality"  # use your path
        all_files = glob.glob(path + "/*.csv")
    else:
        path = rf"{NETWORK_DATA_PATH}/{source}/outflow_centrality"
        all_files = glob.glob(path + "/*.csv")

    # extract date from file name
    # combine data from all csv files into one dataframe, dropping row number of each csv file
    list_df = []
    for filename in all_files:
        if filename.split("_")[-2].split(".")[0] == source:
            df_betweenness = pd.read_csv(filename, index_col=None, header=0)
            date = filename.split("_")[-1].split(".")[0]
            df_betweenness["Date"] = date
            list_df.append(df_betweenness)

    # combine all csv files into one dataframe
    frame = pd.concat(list_df, axis=0, ignore_index=True)

    # only keep WETH, WBTC, MATIC, USDC, USDT, DAI, FEI
    frame = frame[frame["token"].isin(KEY_TOKEN_LIST)]

    # plot the 30-day moving average of betweenness centrality of each token
    # the x-axis is date, the y-axis is betweenness centrality
    # the plot is saved in data/data_betweenness/betweenness/betweenness.png
    frame[graph_type] = frame["eigenvector_centrality"].astype(float)
    frame["Date"] = pd.to_datetime(frame["Date"])
    frame = frame.sort_values(by=["token", "Date"])

    # rename the node column to Token and Date to time
    frame = frame.rename(columns={"token": "Token"})

    # save the dataframe to csv in table path
    frame.to_csv(Path(PLOT_DATA_PATH) / f"{graph_type}_{source}.csv", index=False)


if __name__ == "__main__":
    for graph_type in ["eigen_in", "eigen_out"]:
        for source in ["v2", "v3", "merged"]:
            eigenvector_prep(graph_type, source)
