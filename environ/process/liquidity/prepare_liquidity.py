"""
Function to prepare the liquidity data.
"""
# Import the necessary library
import os
import warnings
import pandas as pd
import matplotlib.pyplot as plt
from glob import glob
from tqdm import tqdm
from environ.utils.config_parser import Config

# ignore the warning
warnings.filterwarnings("ignore")

# initialize the config
config = Config()
UNISWAP_V2_DATA_PATH = config["dev"]["config"]["data"]["UNISWAP_V2_DATA_PATH"]
UNISWAP_V3_DATA_PATH = config["dev"]["config"]["data"]["UNISWAP_V3_DATA_PATH"]
NETWORK_DATA_PATH = config["dev"]["config"]["data"]["NETWORK_DATA_PATH"]
GLOBAL_DATA_PATH = config["dev"]["config"]["data"]["GLOBAL_DATA_PATH"]
HTTP_V2 = config["dev"]["config"]["subgraph"]["HTTP_V2"]
HTTP_V3 = config["dev"]["config"]["subgraph"]["HTTP_V3"]


def tvl_prep() -> None:
    """
    Function to prepare the TVL data.
    """

    # check whether the data tvl folder exists in data/data_network/merged
    if not os.path.exists(rf"{NETWORK_DATA_PATH}/merged/tvl"):
        # if not, create the folder
        os.makedirs(rf"{NETWORK_DATA_PATH}/merged/tvl")

    # check whether the data tvl folder exists in data/data_network/v2
    if not os.path.exists(rf"{NETWORK_DATA_PATH}/v2/tvl"):
        # if not, create the folder
        os.makedirs(rf"{NETWORK_DATA_PATH}/v2/tvl")

    # check whether the data tvl folder exists in data/data_network/v3
    if not os.path.exists(rf"{NETWORK_DATA_PATH}/v3/tvl"):
        # if not, create the folder
        os.makedirs(rf"{NETWORK_DATA_PATH}/v3/tvl")

    data_path = rf"{UNISWAP_V2_DATA_PATH}/tvl/csv"

    # load in all csv in data/data_uniswap_v
    file_list = glob(data_path + "/*.csv")

    # initialize the dataframe
    df_tvl = pd.DataFrame()

    # loop through all csv files
    for file in tqdm(file_list):
        # load in the csv
        df_temp = pd.read_csv(file)

        # only keep the date and totalLiquidityUSD
        df_temp = df_temp[["date", "totalLiquidityUSD", "token_symbol"]]

        # rename the column totalLiquidityUSD to total_tvl
        df_temp = df_temp.rename(
            columns={"totalLiquidityUSD": "total_tvl", "token_symbol": "token"}
        )

        # append the dataframe
        df_tvl = df_tvl.append(df_temp)

    # convert the date column to datetime
    df_tvl["date"] = pd.to_datetime(df_tvl["date"])

    # sort the dataframe by date
    df_tvl = df_tvl.sort_values(by="date", ascending=True)

    # iterate through all the date from 2020-06-01 to 2023-01-31
    for date in tqdm(pd.date_range("2020-06-01", "2023-01-31")):

        # subset the dataframe by date
        df_temp = df_tvl[df_tvl["date"] == date]

        # drop nan
        df_temp = df_temp.dropna()

        # save the dataframe in the format of tvl_v2_YYYYDDMM.csv
        df_temp.to_csv(
            f"{NETWORK_DATA_PATH}/v2/tvl/tvl_v2_{pd.to_datetime(date).strftime('%Y%m%d')}.csv",
            index=False,
        )

    data_path = rf"{UNISWAP_V3_DATA_PATH}/tvl/csv"

    # load in all csv in data/data_uniswap_v
    file_list = glob(data_path + "/*.csv")

    # initialize the dataframe
    df_tvl = pd.DataFrame()

    # loop through all csv files
    for file in tqdm(file_list):
        # # check point: if the file is USDT
        # if file == rf"{UNISWAP_V3_DATA_PATH}/tvl/csv/USDT.csv":
        #     # load in the csv
        #     df_temp = pd.read_csv(file)

        #     # convert the date column to datetime
        #     df_temp["date"] = pd.to_datetime(df_temp["date"])

        #     # plot the totalValueLockedUSD
        #     plt.plot(df_temp["date"], df_temp["totalValueLockedUSD"])
        #     plt.show()

        # load in the csv
        df_temp = pd.read_csv(file)

        # only keep the date and totalLiquidityUSD
        df_temp = df_temp[["date", "totalValueLockedUSD", "token_symbol"]]

        # rename the column totalLiquidityUSD to total_tvl
        df_temp = df_temp.rename(
            columns={"totalValueLockedUSD": "total_tvl", "token_symbol": "token"}
        )

        # append the dataframe
        df_tvl = df_tvl.append(df_temp)

    # convert the date column to datetime
    df_tvl["date"] = pd.to_datetime(df_tvl["date"])

    # sort the dataframe by date
    df_tvl = df_tvl.sort_values(by="date", ascending=True)

    # iterate through all the date from 2020-06-01 to 2023-01-31
    for date in tqdm(pd.date_range("2020-06-01", "2023-01-31")):

        # subset the dataframe by date
        df_temp = df_tvl[df_tvl["date"] == date]

        # drop nan
        df_temp = df_temp.dropna()

        # save the dataframe in the format of tvl_v3_YYYYDDMM.csv
        df_temp.to_csv(
            f"{NETWORK_DATA_PATH}/v3/tvl/tvl_v3_{pd.to_datetime(date).strftime('%Y%m%d')}.csv",
            index=False,
        )

    # load in all csv in data/data_network/v2/tvl
    file_list = glob(rf"{NETWORK_DATA_PATH}/v2/tvl/*.csv")

    # initialize the dataframe
    df_tvl = pd.DataFrame()

    # loop through all csv files
    for file in tqdm(file_list):
        # load in the csv of v2
        df_temp_v2 = pd.read_csv(file)

        # try to load in the csv of v3
        try:
            # load in the csv of v3
            df_temp_v3 = pd.read_csv(
                rf"{NETWORK_DATA_PATH}/v3/tvl/tvl_v3_{file.split('_')[-1]}"
            )

            # append the dataframe
            df_temp_v2 = df_temp_v2.append(df_temp_v3)

        except:
            pass

        # group by token
        df_temp_v2 = df_temp_v2.groupby("token").sum().reset_index()

        # save the dataframe in the format of tvl_merged_YYYYDDMM.csv
        df_temp_v2.to_csv(
            f"{NETWORK_DATA_PATH}/merged/tvl/tvl_merged_{file.split('_')[-1]}",
            index=False,
        )


def tvl_share_prep() -> None:
    """
    Function to prepare the tvl share data
    """

    # check if the folder exists
    if not os.path.exists(rf"{NETWORK_DATA_PATH}/merged/tvl_share"):
        # create the folder
        os.makedirs(rf"{NETWORK_DATA_PATH}/merged/tvl_share")

    # check if the folder exists
    if not os.path.exists(rf"{NETWORK_DATA_PATH}/v2/tvl_share"):
        # create the folder
        os.makedirs(rf"{NETWORK_DATA_PATH}/v2/tvl_share")

    # check if the folder exists
    if not os.path.exists(rf"{NETWORK_DATA_PATH}/v3/tvl_share"):
        # create the folder
        os.makedirs(rf"{NETWORK_DATA_PATH}/v3/tvl_share")

    # load in the csv of total tvl of v2, ignore the row of 0, 1, 2, 3, 4
    # only keep the second column and fourth column
    # set the column name to date and total_tvl
    df_tvl_v2 = pd.read_csv(
        rf"{UNISWAP_V2_DATA_PATH}/tvl/total/uniswap-v2.csv",
        skiprows=[0, 1, 2, 3, 4],
        usecols=[1, 3],
        names=["date", "total_tvl"],
    )

    # convert the date column from DD/MM/YYYY to YYYY-MM-DD
    df_tvl_v2["date"] = pd.to_datetime(df_tvl_v2["date"], format="%d/%m/%Y").dt.date

    # load in the tvl data from data/data_network/v2/tvl in the format of tvl_v2_YYYYDDMM.csv
    file_list = glob(rf"{NETWORK_DATA_PATH}/v2/tvl/*.csv")

    # loop through all csv files
    for file in tqdm(file_list):
        try:
            # get the date from the file name
            date = file.split("_")[-1].split(".")[0]

            # load in the csv
            df_temp = pd.read_csv(file)

            # get the total tvl of the date
            total_tvl = df_tvl_v2[df_tvl_v2["date"] == pd.to_datetime(date)][
                "total_tvl"
            ].values[0]

            # calculate the share
            total_tvl_series = df_temp["total_tvl"] / total_tvl

            if total_tvl_series.sum() > 1:
                df_temp["total_tvl"] = df_temp["total_tvl"] / df_temp["total_tvl"].sum()
            else:
                df_temp["total_tvl"] = total_tvl_series

            # save the dataframe in the format of tvl_share_v2_YYYYDDMM.csv
            df_temp.to_csv(
                f"{NETWORK_DATA_PATH}/v2/tvl_share/tvl_share_v2_{date}.csv", index=False
            )
        except:
            pass

    # load in the csv of total tvl of v3, ignore the row of 0, 1, 2, 3, 4
    # only keep the second column and fourth column
    # set the column name to date and total_tvl
    df_tvl_v3 = pd.read_csv(
        rf"{UNISWAP_V3_DATA_PATH}/tvl/total/uniswap-v3.csv",
        skiprows=[0, 1, 2, 3, 4],
        usecols=[1, 4],
        names=["date", "total_tvl"],
    )

    # convert the date column from DD/MM/YYYY to YYYY-MM-DD
    df_tvl_v3["date"] = pd.to_datetime(df_tvl_v3["date"], format="%d/%m/%Y").dt.date

    # load in the tvl data from data/data_network/v3/tvl in the format of tvl_v3_YYYYDDMM.csv
    file_list = glob(rf"{NETWORK_DATA_PATH}/v3/tvl/*.csv")

    # loop through all csv files
    for file in tqdm(file_list):
        try:
            # get the date from the file name
            date = file.split("_")[-1].split(".")[0]

            # load in the csv
            df_temp = pd.read_csv(file)

            # get the total tvl of the date
            total_tvl = df_tvl_v3[df_tvl_v3["date"] == pd.to_datetime(date)][
                "total_tvl"
            ].values[0]

            # calculate the share
            total_tvl_series = df_temp["total_tvl"] / total_tvl

            if total_tvl_series.sum() > 1:
                df_temp["total_tvl"] = df_temp["total_tvl"] / df_temp["total_tvl"].sum()
            else:
                df_temp["total_tvl"] = total_tvl_series

            # save the dataframe in the format of tvl_share_v3_YYYYDDMM.csv
            df_temp.to_csv(
                f"{NETWORK_DATA_PATH}/v3/tvl_share/tvl_share_v3_{date}.csv", index=False
            )
        except:
            pass

    # load in the tvl share data from data/data_network/merged/tvl
    # in the format of tvl_merged_YYYYDDMM.csv
    file_list = glob(rf"{NETWORK_DATA_PATH}/merged/tvl/*.csv")

    # loop through all csv files
    for file in tqdm(file_list):
        try:
            # get the date from the file name
            date = file.split("_")[-1].split(".")[0]

            # load in the csv
            df_temp = pd.read_csv(file)

            # get the total tvl of the date
            total_tvl = df_tvl_v2[df_tvl_v2["date"] == pd.to_datetime(date)][
                "total_tvl"
            ].values[0]

            # try to get the total tvl of v3
            try:
                total_tvl += df_tvl_v3[df_tvl_v3["date"] == pd.to_datetime(date)][
                    "total_tvl"
                ].values[0]
            except:
                pass

            # calculate the share
            total_tvl_series = df_temp["total_tvl"] / total_tvl

            if total_tvl_series.sum() > 1:
                df_temp["total_tvl"] = df_temp["total_tvl"] / df_temp["total_tvl"].sum()
            else:
                df_temp["total_tvl"] = total_tvl_series

            # save the dataframe in the format of tvl_share_merged_YYYYDDMM.csv
            df_temp.to_csv(
                f"{NETWORK_DATA_PATH}/merged/tvl_share/tvl_share_merged_{date}.csv",
                index=False,
            )
        except:
            pass


if __name__ == "__main__":
    tvl_prep()
    tvl_share_prep()
