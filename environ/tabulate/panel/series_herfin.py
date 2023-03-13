"""
Script to generate the dataframe related to the herfindahl index.
"""

import pandas as pd
import numpy as np
import glob
from tqdm import tqdm
import matplotlib.pyplot as plt
from environ.utils.config_parser import Config
from environ.utils.boom_calculator import boom_bust

# Initialize config
config = Config()

# Initialize data path
NETWORK_DATA_PATH = config["dev"]["config"]["data"]["NETWORK_DATA_PATH"]
BETWEENNESS_DATA_PATH = config["dev"]["config"]["data"]["BETWEENNESS_DATA_PATH"]
GLOBAL_DATA_PATH = config["dev"]["config"]["data"]["GLOBAL_DATA_PATH"]
START_DATE = config["dev"]["config"]["coingecko"]["START_DATE"]
END_DATE = config["dev"]["config"]["coingecko"]["END_DATE"]
TABLE_PATH = config["dev"]["config"]["result"]["TABLE_PATH"]


def _merge_herfindahl_liquidity(herfindahl: pd.DataFrame) -> pd.DataFrame:
    """
    Function to merge the herfindahl index.
    """

    # merge the herfindahl index for liquidity
    # get all csv files in data/data_network/merged/liquidity_share
    path = rf"{NETWORK_DATA_PATH}/merged/tvl_share"  # use your path
    all_files = glob.glob(path + "/*.csv")

    # extract date from file name
    # combine data from all csv files into one dataframe, dropping row number of each csv file
    list_df = []
    for filename in all_files:
        df_in_cent = pd.read_csv(filename, index_col=None, header=0)
        date = filename.split("_")[-1].split(".")[0]
        df_in_cent["total_tvl"] = df_in_cent["total_tvl"].astype(float)
        # convert the "yyyymmdd" date to datetime format
        date = pd.to_datetime(date, format="%Y%m%d")
        list_df.append((date, (df_in_cent["total_tvl"] ** 2).sum()))

    list_df = pd.DataFrame(list_df, columns=["Date", "total_tvl"])

    # sort the dataframe by date
    list_df = list_df.sort_values(by="Date", ascending=True)

    # rename the column "total_tvl" to "herfindahl_inflow_centrality"
    list_df = list_df.rename(columns={"total_tvl": "herfindahl_tvl"})

    # merge the herfindahl index for inflow eigenvector centrality using outer join
    herfindahl = pd.merge(
        herfindahl,
        list_df,
        how="outer",
        on=["Date"],
    )

    return herfindahl


def _merge_herfindahl_volume() -> pd.DataFrame:
    """
    Function to merge the herfindahl index.
    """

    # merge the herfindahl index for volume
    # get all csv files in data/data_network/merged/volume_share
    path = rf"{NETWORK_DATA_PATH}/merged/volume_share"  # use your path
    all_files = glob.glob(path + "/*.csv")

    # extract date from file name
    # calculate the herfindahl index
    # combine data from all csv files into one dataframe, dropping row number of each csv file
    list_df = []
    for filename in all_files:
        df_volume = pd.read_csv(filename, index_col=None, header=0)
        date = filename.split("_")[-1].split(".")[0]
        df_volume["Volume"] = df_volume["Volume"].astype(float)
        # convert the "yyyymmdd" date to datetime format
        date = pd.to_datetime(date, format="%Y%m%d")
        list_df.append((date, (df_volume["Volume"] ** 2).sum()))

    # calculate the herfindahl index that's all
    herfindahl = pd.DataFrame(list_df, columns=["Date", "herfindahl_volume"])

    # sort the dataframe by date
    herfindahl = herfindahl.sort_values(by="Date", ascending=True)

    return herfindahl


def _merge_herfindahl_inflow_centrality(herfindahl: pd.DataFrame) -> pd.DataFrame:
    """
    Function to merge the herfindahl index for inflow eigenvector centrality.
    """

    # merge the herfindahl index for inflow eigenvector centrality
    # get all csv files in data/data_network/merged/inflow_centrality
    path = rf"{NETWORK_DATA_PATH}/merged/inflow_centrality"  # use your path
    all_files = glob.glob(path + "/*.csv")

    # extract date from file name
    # combine data from all csv files into one dataframe, dropping row number of each csv file
    list_df = []
    for filename in all_files:
        df_in_cent = pd.read_csv(filename, index_col=None, header=0)
        date = filename.split("_")[-1].split(".")[0]
        df_in_cent["eigenvector_centrality"] = df_in_cent[
            "eigenvector_centrality"
        ].astype(float)

        # normalized the eigenvector centrality
        df_in_cent["eigenvector_centrality"] = (
            df_in_cent["eigenvector_centrality"]
            / df_in_cent["eigenvector_centrality"].sum()
        )

        # convert the "yyyymmdd" date to datetime format
        date = pd.to_datetime(date, format="%Y%m%d")
        list_df.append((date, (df_in_cent["eigenvector_centrality"] ** 2).sum()))

    list_df = pd.DataFrame(list_df, columns=["Date", "eigenvector_centrality"])

    # sort the dataframe by date
    list_df = list_df.sort_values(by="Date", ascending=True)

    # rename the column "eigenvector_centrality" to "herfindahl_inflow_centrality"
    list_df = list_df.rename(
        columns={"eigenvector_centrality": "herfindahl_inflow_centrality"}
    )

    # merge the herfindahl index for inflow eigenvector centrality using outer join
    herfindahl = pd.merge(
        herfindahl,
        list_df,
        how="outer",
        on=["Date"],
    )

    return herfindahl


def _merge_herfindahl_outflow_centrality(herfindahl: pd.DataFrame) -> pd.DataFrame:
    """
    Function to merge the herfindahl index for outflow eigenvector centrality.
    """

    # merge the herfindahl index for outflow eigenvector centrality
    # get all csv files in data/data_network/merged/outflow_centrality
    path = rf"{NETWORK_DATA_PATH}/merged/outflow_centrality"  # use your path
    all_files = glob.glob(path + "/*.csv")

    # extract date from file name
    # combine data from all csv files into one dataframe, dropping row number of each csv file
    list_df = []
    for filename in all_files:
        df_out_cent = pd.read_csv(filename, index_col=None, header=0)
        date = filename.split("_")[-1].split(".")[0]
        df_out_cent["eigenvector_centrality"] = df_out_cent[
            "eigenvector_centrality"
        ].astype(float)

        # normalzed the eigenvector centrality
        df_out_cent["eigenvector_centrality"] = (
            df_out_cent["eigenvector_centrality"]
            / df_out_cent["eigenvector_centrality"].sum()
        )

        # convert the "yyyymmdd" date to datetime format
        date = pd.to_datetime(date, format="%Y%m%d")
        list_df.append((date, (df_out_cent["eigenvector_centrality"] ** 2).sum()))

    list_df = pd.DataFrame(list_df, columns=["Date", "eigenvector_centrality"])

    # sort the dataframe by date
    list_df = list_df.sort_values(by="Date", ascending=True)

    # rename the column "eigenvector_centrality" to "herfindahl_outflow_centrality"
    list_df = list_df.rename(
        columns={"eigenvector_centrality": "herfindahl_outflow_centrality"}
    )

    # merge the herfindahl index for outflow eigenvector centrality using outer join
    herfindahl = pd.merge(
        herfindahl,
        list_df,
        how="outer",
        on=["Date"],
    )

    return herfindahl


def _merge_herfindahl_betweenness_centrality(herfindahl: pd.DataFrame) -> pd.DataFrame:
    """
    Function to merge the herfindahl index for betweenness centrality.
    """

    # get all csv files in data/data_betweenness/betweenness
    path = rf"{BETWEENNESS_DATA_PATH}/betweenness"  # use your path
    all_files = glob.glob(path + "/*.csv")

    # extract date from file name
    # combine data from all csv files into one dataframe, dropping row number of each csv file
    list_df = []
    for filename in all_files:
        if filename.split("_")[-2].split(".")[0] == "v2v3":
            df_between = pd.read_csv(filename, index_col=None, header=0)
            date = filename.split("_")[-1].split(".")[0]
            date = pd.to_datetime(date, format="%Y%m%d")
            list_df.append(
                (
                    date,
                    (df_between["betweenness_centrality_count"] ** 2).sum(),
                    (df_between["betweenness_centrality_volume"] ** 2).sum(),
                )
            )

    list_df = pd.DataFrame(
        list_df,
        columns=[
            "Date",
            "betweenness_centrality_count",
            "betweenness_centrality_volume",
        ],
    )

    # sort the dataframe by date
    list_df = list_df.sort_values(by="Date", ascending=True)

    # rename the columns "betweenness_centrality_count" and "betweenness_centrality_volume" to
    # "herfindahl_betweenness_centrality_count" and "herfindahl_betweenness_centrality_volume"
    list_df = list_df.rename(
        columns={
            "betweenness_centrality_count": "herfindahl_betweenness_centrality_count",
            "betweenness_centrality_volume": "herfindahl_betweenness_centrality_volume",
        }
    )

    # merge the herfindahl index for betweenness centrality using outer join
    herfindahl = pd.merge(
        herfindahl,
        list_df,
        how="outer",
        on=["Date"],
    )

    return herfindahl


def _merge_total_market_trading_volume(herfindahl: pd.DataFrame) -> pd.DataFrame:
    """
    Function to merge the total market trading volume.
    """

    # create a dataframe with column Date from START_DATE to END_DATE
    # and a column named "total_market_trading_volume" with value 0
    date_range = pd.date_range(START_DATE, END_DATE)
    df_total = pd.DataFrame(date_range, columns=["Date"])
    df_total["total_volumes"] = 0

    # load in the data in data/data_global/coingecko/token_data
    # sum the total_volumnes of the token to the df
    path = rf"{GLOBAL_DATA_PATH}/coingecko/token_data"  # use your path
    all_files = glob.glob(path + "/*.csv")
    for filename in tqdm(all_files):
        # expand the date range to START_DATE to END_DATE
        df_temp = pd.read_csv(filename, index_col=None, header=0)
        df_temp["time"] = pd.to_datetime(df_temp["time"], format="%Y-%m-%d")
        # rename the column "time" to "Date"
        df_temp = df_temp.rename(columns={"time": "Date"})
        df_temp = df_temp.set_index("Date")
        df_temp = df_temp.reindex(date_range, fill_value=0)
        df_temp = df_temp.reset_index()
        df_temp = df_temp.rename(columns={"index": "Date"})
        df_total["total_volumes"] = df_total["total_volumes"] + df_temp["total_volumes"]
    # # plot the total market trading volume
    # plt.plot(df_total["Date"], df_total["total_volumes"])
    # plt.xlabel("Date")
    # plt.ylabel("Total Market Trading Volume")
    # plt.title("Total Market Trading Volume")
    # plt.show()

    # remove inf and -inf
    df_total = df_total.replace([np.inf, -np.inf], np.nan)

    # remove nan
    df_total = df_total.dropna()

    # take the log of the total market trading volume
    df_total["total_volumes"] = np.log(df_total["total_volumes"])

    # save the dataframe to data/data_global/token_market/total_market_trading_volume.csv
    df_total.to_csv(
        rf"{GLOBAL_DATA_PATH}/token_market/total_market_trading_volume.csv",
        index=False,
    )

    # merge the total market trading volume using outer join
    herfindahl = pd.merge(
        herfindahl,
        df_total,
        how="outer",
        on=["Date"],
    )

    return herfindahl


def _merge_sp(herfindahl: pd.DataFrame) -> pd.DataFrame:
    """
    Function to merge the crypto mraket index.
    """

    # read in the csv file and ignore the first six rows
    idx = pd.read_excel(
        rf"{GLOBAL_DATA_PATH}/token_market/PerformanceGraphExport.xls",
        index_col=None,
        skiprows=6,
        skipfooter=4,
        usecols="A:B",
    )

    # convert Effective date to datetime
    idx["Date"] = pd.to_datetime(idx["Date"])

    # sort the dataframe by date
    idx = idx.sort_values(by="Date", ascending=True)

    # merge the crypto market index using outer join
    herfindahl = pd.merge(
        herfindahl,
        idx,
        how="outer",
        on=["Date"],
    )

    # sort the dataframe by date
    herfindahl = herfindahl.sort_values(by="Date", ascending=True)

    # interpolate the S&P column
    herfindahl["price"] = herfindahl["S&P"].interpolate()

    # # plot the S&P column
    # plt.plot(herfindahl["Date"], herfindahl["price"])
    # plt.xlabel("Date")
    # plt.ylabel("S&P")
    # plt.title("S&P")
    # plt.show()

    # calculate the log return of the S&P column
    herfindahl["S&P"] = np.log(herfindahl["price"] / herfindahl["price"].shift(1))

    # calculate the 30-day rolling volatility of the S&P column
    herfindahl["S&P_volatility"] = herfindahl["S&P"].rolling(30).std()

    return herfindahl


def _merge_gas(herfindahl: pd.DataFrame) -> pd.DataFrame:
    """
    Function to merge the gas price.
    """

    # read in the csv file
    gas = pd.read_csv(
        rf"{GLOBAL_DATA_PATH}/gas_fee/avg_gas_fee.csv", index_col=None, header=0
    )

    # convert date to datetime
    gas["Date(UTC)"] = pd.to_datetime(gas["Date(UTC)"])

    # rename the column "Date(UTC)" to "Date"
    gas = gas.rename(columns={"Date(UTC)": "Date"})
    gas = gas.rename(columns={"Gas Fee USD": "Gas_fee"})

    # only keep columnes of "Date", "Gas_fee" and "ETH_price"
    gas = gas[["Date", "Gas_fee"]]

    # calculate the log return of the gas price
    gas["Gas_fee_log_return"] = np.log(gas["Gas_fee"] / gas["Gas_fee"].shift(1))

    # calculate the 30-day rolling volatility for column "Gas_fee"
    gas["Gas_fee_volatility"] = gas["Gas_fee_log_return"].rolling(30).std()

    # drop the column "Gas_fee_log_return"
    gas = gas.drop(columns=["Gas_fee_log_return"])

    # merge the gas price using outer join
    herfindahl = pd.merge(
        herfindahl,
        gas,
        how="outer",
        on=["Date"],
    )

    return herfindahl


def _merge_boom_bust(herfindahl: pd.DataFrame) -> pd.DataFrame:
    """
    Function to merge the boom and bust dummy.
    """

    # sort the dataframe by date
    herfindahl = herfindahl.sort_values(by="Date", ascending=True)

    # convert the date column to unix
    herfindahl["time"] = herfindahl["Date"].apply(lambda x: x.timestamp())

    # create a copy of the herfindahl dataframe
    boom_bust_df = herfindahl.copy()

    # only keep the column of S&P and time
    boom_bust_df = boom_bust_df[["time", "price"]]

    # dropna
    boom_bust_df = boom_bust_df.dropna()

    # computation
    BOOM_BUST = boom_bust(boom_bust_df)

    herfindahl["boom"] = 0
    herfindahl["bust"] = 0

    for boom in BOOM_BUST["boom"]:
        herfindahl.loc[
            (herfindahl["time"] >= boom[0]) & (herfindahl["time"] <= boom[1]),
            "boom",
        ] = 1

    for bust in BOOM_BUST["bust"]:
        herfindahl.loc[
            (herfindahl["time"] >= bust[0]) & (herfindahl["time"] <= bust[1]),
            "bust",
        ] = 1

    # drop the column of time and price and index
    herfindahl = herfindahl.drop(columns=["time", "price"])

    return herfindahl


def generate_series_herfin() -> pd.DataFrame:
    """
    Function to generate the series of herfindahl index.
    """

    herfindahl = _merge_herfindahl_volume()
    herfindahl = _merge_herfindahl_inflow_centrality(herfindahl)
    herfindahl = _merge_herfindahl_outflow_centrality(herfindahl)
    herfindahl = _merge_herfindahl_betweenness_centrality(herfindahl)
    herfindahl = _merge_herfindahl_liquidity(herfindahl)
    herfindahl = _merge_total_market_trading_volume(herfindahl)
    herfindahl = _merge_sp(herfindahl)
    herfindahl = _merge_gas(herfindahl)
    herfindahl = _merge_boom_bust(herfindahl)

    # # plot the all kinds of herfindahl index
    # plt.plot(herfindahl["Date"], herfindahl["herfindahl_volume"])
    # # plt.plot(herfindahl["Date"], herfindahl["herfindahl_inflow_centrality"])
    # # plt.plot(herfindahl["Date"], herfindahl["herfindahl_outflow_centrality"])
    # plt.plot(herfindahl["Date"], herfindahl["herfindahl_betweenness_centrality_count"])
    # plt.plot(herfindahl["Date"], herfindahl["herfindahl_betweenness_centrality_volume"])
    # plt.plot(herfindahl["Date"], herfindahl["herfindahl_tvl"])
    # plt.xlabel("Date")
    # plt.ylabel("Herfindahl Index")
    # plt.title("Herfindahl Index")
    # plt.legend(
    #     [
    #         "herfindahl_volume",
    #         # "herfindahl_inflow_centrality",
    #         # "herfindahl_outflow_centrality",
    #         "herfindahl_betweenness_centrality_count",
    #         "herfindahl_betweenness_centrality_volume",
    #         "herfindahl_tvl",
    #     ]
    # )
    # plt.show()

    # save the dataframe to table
    herfindahl.to_csv(rf"{TABLE_PATH}/series_herfindahl.csv", index=False)

    return herfindahl


if __name__ == "__main__":
    # test the function
    print(generate_series_herfin())
