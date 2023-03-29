"""
Script to merge the eigen swap files into the main panel
"""

from glob import glob

import pandas as pd
from tqdm import tqdm

from environ.constants import NETWORK_DATA_PATH, TABLE_PATH

# load the pickle file in tables/reg_panel.pkl
reg_panel = pd.read_pickle(TABLE_PATH / "reg_panel.pkl")

# convert the Date index to datetime
reg_panel["Date"] = pd.to_datetime(reg_panel["Date"])

# load in all files in data/data_network/merged/eigen_centrality_swap
eigen_swap_files = glob(
    str(NETWORK_DATA_PATH / "merged" / "eigen_centrality_swap" / "*.csv")
)

# list to store the dataframes
df_list = []

# load in all files and generate a panel
for file in tqdm(eigen_swap_files):
    # load the file
    df = pd.read_csv(file)

    # isolate the date
    date = file.split("_")[-1].split(".")[0]

    # convert the date to datetime
    df["Date"] = pd.to_datetime(date)

    # renanme the column
    df.rename(
        columns={
            "Inflow_centrality": "Inflow_centrality_swap",
            "Outflow_centrality": "Outflow_centrality_swap",
        },
        inplace=True,
    )

    # append to the list
    df_list.append(df)

# concatenate the list
df = pd.concat(df_list)

# merge the dataframes
reg_panel = pd.merge(reg_panel, df, how="left", on=["Token", "Date"])

# save the reg_panel
reg_panel.to_pickle(TABLE_PATH / "reg_panel_new.pkl")
