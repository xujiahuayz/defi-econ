"""
Script to preprocess the betweenness data
"""

import glob
import os
import tqdm
import pandas as pd

from environ import constants

if __name__ == "__main__":
    # check if the processed data folder exists
    for version in ["v2", "v3", "merged"]:
        if not os.path.exists(f"{constants.NETWORK_DATA_PATH}/{version}/betweenness"):
            os.makedirs(f"{constants.NETWORK_DATA_PATH}/{version}/betweenness")

    # get the list of all files in the folder
    file_name_lst = glob.glob(f"{constants.BETWEENNESS_DATA_PATH}/betweenness/*.csv")

    # create a list with "v2", "v3", and "merged" as keys
    file_name_dict = {
        version: [
            file_name
            for file_name in file_name_lst
            if version == file_name.split("_")[-2]
        ]
        for version in ["v2", "v3", "v2v3"]
    }

    # rename the v2v3 as merged
    file_name_dict["merged"] = file_name_dict.pop("v2v3")

    # for each version, load in the data and save them separately
    for version, file_name_lst in tqdm.tqdm(file_name_dict.items()):
        # load in the data day by day
        for file_name in file_name_lst:
            df_bc = pd.read_csv(file_name)

            # save the data
            df_bc.to_csv(
                f"{constants.NETWORK_DATA_PATH}/{version}/betweenness/{file_name.split('/')[-1]}",
                index=False,
            )
