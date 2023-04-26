"""
Script to plot the sankey diagram
"""

import os
from glob import glob
import warnings

import pandas as pd
from tqdm import tqdm

from environ.constants import BETWEENNESS_DATA_PATH, NETWORK_DATA_PATH
from environ.plot.plot_sankey import plot_sankey

warnings.filterwarnings("ignore")

for uni_version in ["v2", "v3", "merged"]:
    # load the data in the betweenness data path
    data_lst = glob(f"{BETWEENNESS_DATA_PATH}/swap_route/*.csv")

    # check whether the folder exists
    if not os.path.exists(f"{NETWORK_DATA_PATH}/{uni_version}/sankey"):
        os.makedirs(f"{NETWORK_DATA_PATH}/{uni_version}/sankey")

    # filter the data_lst
    data_lst = (
        [i for i in data_lst if i.split("/")[-1].split("_")[-2] == uni_version]
        if uni_version != "merged"
        else [i for i in data_lst if i.split("/")[-1].split("_")[-2] == "v2v3"]
    )

    for data_path in tqdm(data_lst):
        # load the data
        data = pd.read_csv(
            data_path,
            index_col=0,
        )

        # isolate the date
        date = data_path.split("/")[-1].split("_")[-1].split(".")[0]

        # plot the sankey diagram
        plot_sankey(
            data_path=data_path,
            save_path=f"{NETWORK_DATA_PATH}/{uni_version}/sankey/sankey_{date}.png",
        )
