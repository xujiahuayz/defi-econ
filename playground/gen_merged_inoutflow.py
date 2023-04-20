"""
Script to generate the merged in/outflow data
"""

import glob

import pandas as pd
import tqdm

from environ.constants import NETWORK_DATA_PATH

# check whether there is inout_flow folder in merged
if not (NETWORK_DATA_PATH / "merged" / "inout_flow").exists():
    (NETWORK_DATA_PATH / "merged" / "inout_flow").mkdir(parents=True)

# get a list of all files in NETWORK_DATA_PATH / "v2" / "inout_flow"
file_list = glob.glob(str(NETWORK_DATA_PATH / "v2" / "inout_flow" / "*.csv"))

# iterate through the file list
for file in tqdm.tqdm(file_list):
    # read the file
    df = pd.read_csv(file, index_col=0)

    # get the date from the file name
    date = file.split("/")[-1].split("_")[-1].split(".")[0]

    # parse the dictionary for column Source and Target
    df["Source"] = df["Source"].apply(lambda x: eval(x)['symbol'])
    df["Target"] = df["Target"].apply(lambda x: eval(x)['symbol'])

    try:
        # read the v3 file
        df_v3 = pd.read_csv(NETWORK_DATA_PATH / "v3" / "inout_flow" / f"inout_flow_tokens_v3_{date}.csv", index_col=0)

        # append the v3 file to the v2 file
        df_merged = pd.concat([df, df_v3])

        # sum the Volume column for the same Source and Target
        df_merged = df_merged.groupby(["Source", "Target"]).sum().reset_index()
    except:
        df_merged = df

    # save the merged file
    df_merged.to_csv(NETWORK_DATA_PATH / "merged" / "inout_flow" / f"inout_flow_tokens_merged_{date}.csv", index=False)