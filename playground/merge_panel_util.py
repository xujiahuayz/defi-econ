"""
Script to merge the eigen swap files into the main panel
"""

from glob import glob
from pathlib import Path
from typing import Optional, Literal

import pandas as pd
from tqdm import tqdm

from environ.constants import NETWORK_DATA_PATH, DATA_PATH, DATA_PATH


def merge_util(
    reg_panel_path: Path = DATA_PATH / "reg_panel.pkl",
    merge_path: Path = NETWORK_DATA_PATH / "merged" / "eigen_centrality_swap",
    save_path: Path = DATA_PATH / "reg_panel_new.pkl",
    merge_key: list[str] = ["Token", "Date"],
    time_key: str = "Date",
    rename_dict: Optional[dict[str, str]] = None,
    how: Literal["left", "right", "inner", "outer"] = "left",
) -> None:
    """
    Function to merge the data into main panel
    """

    # load the pickle file in tables/reg_panel.pkl
    reg_panel = pd.read_pickle(reg_panel_path)

    # convert the Date index to datetime
    reg_panel[time_key] = pd.to_datetime(reg_panel[time_key])

    # load in all files in data/data_network/merged/eigen_centrality_swap
    eigen_swap_files = glob(str(merge_path / "*.csv"))

    # list to store the dataframes
    df_list = []

    # load in all files and generate a panel
    for file in tqdm(eigen_swap_files):
        # load the file
        df_merge = pd.read_csv(file)

        # isolate the date
        date = file.split("_")[-1].split(".")[0]

        # convert the date to datetime
        df_merge["Date"] = pd.to_datetime(date)

        if rename_dict is not None:
            # renanme the column
            df_merge.rename(
                columns=rename_dict,
                inplace=True,
            )

        # append to the list
        df_list.append(df_merge)

    # concatenate the list
    df_merge = pd.concat(df_list)

    # merge the dataframes
    reg_panel = pd.merge(reg_panel, df_merge, how=how, on=merge_key)

    # save the reg_panel
    reg_panel.to_pickle(save_path)


if __name__ == "__main__":
    merge_util(
        reg_panel_path=DATA_PATH / "reg_panel_new.pkl",
        merge_path=NETWORK_DATA_PATH / "merged" / "clustering_ind",
        save_path=DATA_PATH / "reg_panel_merged.pkl",
        merge_key=["Token", "Date"],
        time_key="Date",
    )

    merge_util(
        reg_panel_path=DATA_PATH / "reg_panel_merged.pkl",
        merge_path=NETWORK_DATA_PATH / "merged" / "eigen_centrality_undirected",
        save_path=DATA_PATH / "reg_panel_merged.pkl",
        merge_key=["Token", "Date"],
        time_key="Date",
        rename_dict={"eigenvector_centrality": "eigen_centrality_undirected"},
    )

    merge_util(
        reg_panel_path=DATA_PATH / "reg_panel_merged.pkl",
        merge_path=NETWORK_DATA_PATH / "merged" / "eigen_centrality_undirected_multi",
        save_path=DATA_PATH / "reg_panel_merged.pkl",
        merge_key=["Token", "Date"],
        time_key="Date",
        rename_dict={"eigenvector_centrality": "eigen_centrality_undirected_multi"},
    )

    merge_util(
        reg_panel_path=DATA_PATH / "reg_panel_merged.pkl",
        merge_path=NETWORK_DATA_PATH / "merged" / "vol_in_full_len",
        save_path=DATA_PATH / "reg_panel_merged.pkl",
        merge_key=["Token", "Date"],
        time_key="Date",
        rename_dict={
            "volume": "vol_in_full_len",
            "volume_share": "vol_in_full_len_share",
        },
    )

    merge_util(
        reg_panel_path=DATA_PATH / "reg_panel_merged.pkl",
        merge_path=NETWORK_DATA_PATH / "merged" / "vol_out_full_len",
        save_path=DATA_PATH / "reg_panel_merged.pkl",
        merge_key=["Token", "Date"],
        time_key="Date",
        rename_dict={
            "volume": "vol_out_full_len",
            "volume_share": "vol_out_full_len_share",
        },
    )

    merge_util(
        reg_panel_path=DATA_PATH / "reg_panel_merged.pkl",
        merge_path=NETWORK_DATA_PATH / "merged" / "vol_inter_full_len",
        save_path=DATA_PATH / "reg_panel_merged.pkl",
        merge_key=["Token", "Date"],
        time_key="Date",
        rename_dict={
            "volume": "vol_inter_full_len",
            "volume_share": "vol_inter_full_len_share",
        },
    )
