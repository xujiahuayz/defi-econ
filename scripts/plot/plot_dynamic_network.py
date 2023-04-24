"""
Script to plot the dynamic network graph
"""

import pandas as pd
from tqdm import tqdm

from environ.constants import SAMPLE_PERIOD
from environ.plot.network.plot_dynamic import plot_dynamic
from environ.plot.plot_network import plot_network

for uni_version in ["v2", "v3", "merged"]:
    # generate the date range
    date_range = (
        pd.date_range(start=SAMPLE_PERIOD[0], end=SAMPLE_PERIOD[1], freq="D")
        if uni_version != "v3"
        else pd.date_range(start="2021-05-05", end=SAMPLE_PERIOD[1], freq="D")
    )

    for date in tqdm(date_range, desc=f"Plotting {uni_version} network"):
        plot_network(date, uni_version)

    # convert the network graphs to video
    plot_dynamic(uni_version)
