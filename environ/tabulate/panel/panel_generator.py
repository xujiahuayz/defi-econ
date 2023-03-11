"""

University College London
Project : defi_econ
Topic   : panel_generator.py
Author  : Yichen Luo
Date    : 2023-02-06
Desc    : Generate the panel for regression.

"""

import glob
import pandas as pd
import numpy as np
from environ.process.market.boom_bust import BOOM_BUST
from environ.utils.config_parser import Config
from environ.utils.boom_calculator import is_boom
import matplotlib.dates as md

# Initialize config
config = Config()

# Initialize data path
NETWORK_DATA_PATH = config["dev"]["config"]["data"]["NETWORK_DATA_PATH"]
COMPOUND_DATA_PATH = config["dev"]["config"]["data"]["COMPOUND_DATA_PATH"]
GLOBAL_DATA_PATH = config["dev"]["config"]["data"]["GLOBAL_DATA_PATH"]
BETWEENNESS_DATA_PATH = config["dev"]["config"]["data"]["BETWEENNESS_DATA_PATH"]
TOKEN_LIB_V2_TOKEN = config["dev"]["config"]["token_library"]["v2"]["token"]
TOKEN_LIB_V2_STABLE = config["dev"]["config"]["token_library"]["v2"]["stable"]
TOKEN_LIB_V3_TOKEN = config["dev"]["config"]["token_library"]["v3"]["token"]
TOKEN_LIB_V3_STABLE = config["dev"]["config"]["token_library"]["v3"]["stable"]


def _merge_volume_share() -> pd.DataFrame:
    """
    Merge volume share data.
    """
    reg_panel = []

    # combine all csv files in data/data_network/merged/volume_share.
    # each csv file's title contains the date, and has columes: Token, Volume, and has row number
    # the new combined dataframe has colume: Date, Token, Volume

    # get all csv files in data/data_network/merged/volume_share
    path = rf"{NETWORK_DATA_PATH}/merged/volume_share"  # use your path
    all_files = glob.glob(path + "/*.csv")

    # extract date from file name
    # combine data from all csv files into one dataframe, dropping row number of each csv file
    list_df = []
    for filename in all_files:
        df_vol_share = pd.read_csv(filename, index_col=None, header=0)
        date = filename.split("_")[-1].split(".")[0]
        df_vol_share["Date"] = date
        list_df.append(df_vol_share)

    # combine all csv files into one dataframe
    reg_panel = pd.concat(list_df, axis=0, ignore_index=True)

    # convert date to datetime
    reg_panel["Date"] = pd.to_datetime(reg_panel["Date"], format="%Y%m%d")

    # drop the column "Unnamed: 0"
    reg_panel = reg_panel.drop(columns=["Unnamed: 0"])

    # rename the Volume column to Volume_share
    reg_panel = reg_panel.rename(columns={"Volume": "Volume_share"})

    return reg_panel


def _merge_volume_in_share(reg_panel: pd.DataFrame) -> pd.DataFrame:
    """
    Merge volume in share data.
    """

    # combine all csv files in data/data_network/merged/volume_in_share.
    # each csv file's title contains the date, and has columes: Token, Volume, and has row number
    # the new combined dataframe has colume: Date, Token, Volume

    # get all csv files in data/data_network/merged/volume_in_share
    path = rf"{NETWORK_DATA_PATH}/merged/volume_in_share"  # use your path
    all_files = glob.glob(path + "/*.csv")

    # extract date from file name
    # combine data from all csv files into one dataframe, dropping row number of each csv file
    list_df = []
    for filename in all_files:
        df_vol_in_share = pd.read_csv(filename, index_col=None, header=0)
        date = filename.split("_")[-1].split(".")[0]
        df_vol_in_share["Date"] = date
        list_df.append(df_vol_in_share)

    # combine all csv files into one dataframe
    frame = pd.concat(list_df, axis=0, ignore_index=True)

    # convert date to datetime
    frame["Date"] = pd.to_datetime(frame["Date"], format="%Y%m%d")

    # drop the column "Unnamed: 0"
    frame = frame.drop(columns=["Unnamed: 0"])

    # rename the Volume column to volume_in_share
    frame = frame.rename(columns={"Volume": "volume_in_share"})

    # merge the two dataframe into one panel dataset via outer join
    reg_panel = pd.merge(
        reg_panel, frame, how="outer", on=["Date", "Token"], sort=False
    )

    return reg_panel


def _merge_volume_out_share(reg_panel: pd.DataFrame) -> pd.DataFrame:
    """
    Merge volume out share data.
    """

    # combine all csv files in data/data_network/merged/volume_out_share.
    # each csv file's title contains the date, and has columes: Token, Volume, and has row number
    # the new combined dataframe has colume: Date, Token, Volume

    # get all csv files in data/data_network/merged/volume_out_share
    path = rf"{NETWORK_DATA_PATH}/merged/volume_out_share"  # use your path
    all_files = glob.glob(path + "/*.csv")

    # extract date from file name
    # combine data from all csv files into one dataframe, dropping row number of each csv file
    list_df = []
    for filename in all_files:
        df_vol_out_share = pd.read_csv(filename, index_col=None, header=0)
        date = filename.split("_")[-1].split(".")[0]
        df_vol_out_share["Date"] = date
        list_df.append(df_vol_out_share)

    # combine all csv files into one dataframe
    frame = pd.concat(list_df, axis=0, ignore_index=True)

    # convert date to datetime
    frame["Date"] = pd.to_datetime(frame["Date"], format="%Y%m%d")

    # drop the column "Unnamed: 0"
    frame = frame.drop(columns=["Unnamed: 0"])

    # rename the Volume column to volume_out_share
    frame = frame.rename(columns={"Volume": "volume_out_share"})

    # merge the two dataframe into one panel dataset via outer join
    reg_panel = pd.merge(
        reg_panel, frame, how="outer", on=["Date", "Token"], sort=False
    )

    return reg_panel


def _merge_compound_rate(reg_panel: pd.DataFrame) -> pd.DataFrame:
    """
    Merge compound rate data.
    """

    path = rf"{COMPOUND_DATA_PATH}"  # use your path
    all_files = glob.glob(path + "/*_processed.csv")

    # merge all csv files into one dataframe with token name in the file name as the primary key
    list_df = []
    for filename in all_files:
        df_comp_rate = pd.read_csv(filename, index_col=None, header=0)
        token = filename.split("_")[-2]
        # skip the file with token name "WBTC2"
        if token == "WBTC2":
            continue

        if token == "ETH":
            df_comp_rate["token"] = "WETH"
        else:
            df_comp_rate["token"] = token

        list_df.append(df_comp_rate)

    # combine all csv files into one dataframe
    frame = pd.concat(list_df, axis=0, ignore_index=True)

    # convert date in "YYYY-MM-DD" to datetime
    frame["block_timestamp"] = pd.to_datetime(
        frame["block_timestamp"], format="%Y-%m-%d"
    )

    # rename the column "block_timestamp" to "Date"
    frame = frame.rename(columns={"block_timestamp": "Date"})
    frame = frame.rename(columns={"token": "Token"})

    # only keep the columne "borrow_rate" and "supply_rates" and block_timestamp and token
    frame = frame[["Date", "Token", "borrow_rate", "supply_rates"]]

    # merge the two dataframe into one panel dataset via outer join
    reg_panel = pd.merge(reg_panel, frame, how="outer", on=["Date", "Token"])

    return reg_panel


def _merge_compound_supply_share(reg_panel: pd.DataFrame) -> pd.DataFrame:
    """
    Merge compound supply share data.
    """

    # combine all csv files with "_processed" at the end
    # of the name in data/data_compound into a panel dataset.
    # each csv file's title contains the date, and has columes: Token, Borrow, and has row number
    # the new combined dataframe has colume: Date, Token, Borrow
    # get all csv files in data/data_compound
    path = rf"{COMPOUND_DATA_PATH}"  # use your path
    all_files = glob.glob(path + "/*_processed.csv")

    # merge all csv files into one dataframe with token name in the file name as the primary key
    list_df = []
    for filename in all_files:
        df_comp_share = pd.read_csv(filename, index_col=None, header=0)
        token = filename.split("_")[-2]
        # skip the file with token name "WBTC2"
        if token == "WBTC2":
            continue

        if token == "ETH":
            df_comp_share["token"] = "WETH"
        else:
            df_comp_share["token"] = token

        list_df.append(df_comp_share)

    # combine all csv files into one dataframe
    frame = pd.concat(list_df, axis=0, ignore_index=True)

    # calculate the supply share of each token each day
    frame["total_supply_usd"] = frame["total_supply_usd"].astype(float)
    frame["total_supply"] = frame.groupby("block_timestamp")[
        "total_supply_usd"
    ].transform("sum")
    frame["total_supply_usd"] = frame["total_supply_usd"] / frame["total_supply"]
    frame = frame.drop(columns=["total_supply"])

    # convert date in "YYYY-MM-DD" to datetime
    frame["block_timestamp"] = pd.to_datetime(
        frame["block_timestamp"], format="%Y-%m-%d"
    )

    # rename the column "block_timestamp" to "Date"
    frame = frame.rename(columns={"block_timestamp": "Date"})
    frame = frame.rename(columns={"token": "Token"})
    frame = frame.rename(columns={"total_supply_usd": "Supply_share"})

    # only keep columnes of "Date", "Token", "Borrow_share"
    frame = frame[["Date", "Token", "Supply_share"]]

    # merge the two dataframe into one panel dataset via outer join
    reg_panel = pd.merge(reg_panel, frame, how="outer", on=["Date", "Token"])

    return reg_panel


def _merge_compound_borrow_share(reg_panel: pd.DataFrame) -> pd.DataFrame:
    """
    Merge compound borrow share data.
    """

    # combine all csv files with "_processed" at the end
    # of the name in data/data_compound into a panel dataset.
    # each csv file's title contains the date, and has columes: Token, Borrow, and has row number
    # the new combined dataframe has colume: Date, Token, Borrow
    # get all csv files in data/data_compound
    path = rf"{COMPOUND_DATA_PATH}"  # use your path
    all_files = glob.glob(path + "/*_processed.csv")

    # merge all csv files into one dataframe with token name in the file name as the primary key
    list_df = []
    for filename in all_files:
        df_comp_share = pd.read_csv(filename, index_col=None, header=0)
        token = filename.split("_")[-2]
        # skip the file with token name "WBTC2"
        if token == "WBTC2":
            continue

        if token == "ETH":
            df_comp_share["token"] = "WETH"
        else:
            df_comp_share["token"] = token

        list_df.append(df_comp_share)

    # combine all csv files into one dataframe
    frame = pd.concat(list_df, axis=0, ignore_index=True)

    # calculate the supply share of each token each day
    frame["total_borrow_usd"] = frame["total_borrow_usd"].astype(float)
    frame["total_borrow"] = frame.groupby("block_timestamp")[
        "total_borrow_usd"
    ].transform("sum")
    frame["total_borrow_usd"] = frame["total_borrow_usd"] / frame["total_borrow"]
    frame = frame.drop(columns=["total_borrow"])

    # convert date in "YYYY-MM-DD" to datetime
    frame["block_timestamp"] = pd.to_datetime(
        frame["block_timestamp"], format="%Y-%m-%d"
    )

    # rename the column "block_timestamp" to "Date"
    frame = frame.rename(columns={"block_timestamp": "Date"})
    frame = frame.rename(columns={"token": "Token"})
    frame = frame.rename(columns={"total_borrow_usd": "Borrow_share"})

    # only keep columnes of "Date", "Token", "Borrow_share"
    frame = frame[["Date", "Token", "Borrow_share"]]

    # merge the two dataframe into one panel dataset via outer join
    reg_panel = pd.merge(reg_panel, frame, how="outer", on=["Date", "Token"])

    return reg_panel


def _merge_tvl_share(reg_panel: pd.DataFrame) -> pd.DataFrame:
    """
    Merge tvl share data.
    """

    # get all csv files in data/data_network/merged/volume_share
    path = rf"{NETWORK_DATA_PATH}/merged/tvl_share"  # use your path
    all_files = glob.glob(path + "/*.csv")

    # extract date from file name
    # combine data from all csv files into one dataframe, dropping row number of each csv file
    list_df = []
    for filename in all_files:
        df_tvl_share = pd.read_csv(filename, index_col=None, header=0)
        date = filename.split("_")[-1].split(".")[0]
        df_tvl_share["Date"] = date
        list_df.append(df_tvl_share)

    # combine all csv files into one dataframe
    frame = pd.concat(list_df, axis=0, ignore_index=True)

    # convert date in "YYYYMMDD" to datetime
    frame["Date"] = pd.to_datetime(frame["Date"], format="%Y%m%d")

    # rename the column "token" to "Token"
    frame = frame.rename(columns={"token": "Token"})
    frame = frame.rename(columns={"total_tvl": "TVL_share"})

    # merge the two dataframe into one panel dataset via outer join
    reg_panel = pd.merge(reg_panel, frame, how="outer", on=["Date", "Token"])

    return reg_panel


def _merge_in_centrality(reg_panel: pd.DataFrame) -> pd.DataFrame:
    """
    Merge inflow eigenvector centrality data.
    """

    # get all csv files in data/data_network/merged/inflow_centrality
    path = rf"{NETWORK_DATA_PATH}/merged/inflow_centrality"  # use your path
    all_files = glob.glob(path + "/*.csv")

    # extract date from file name
    # combine data from all csv files into one dataframe, dropping row number of each csv file
    list_df = []
    for filename in all_files:
        df_in_cent = pd.read_csv(filename, index_col=None, header=0)
        date = filename.split("_")[-1].split(".")[0]
        df_in_cent["Date"] = date
        list_df.append(df_in_cent)

    # combine all csv files into one dataframe
    frame = pd.concat(list_df, axis=0, ignore_index=True)

    # convert date in "YYYYMMDD" to datetime
    frame["Date"] = pd.to_datetime(frame["Date"], format="%Y%m%d")

    # rename the column "token" to "Token"
    frame = frame.rename(columns={"token": "Token"})
    frame = frame.rename(columns={"eigenvector_centrality": "Inflow_centrality"})

    # only keep columnes of "Date", "Token", "Inflow_centrality"
    frame = frame[["Date", "Token", "Inflow_centrality"]]

    # merge the two dataframe into one panel dataset via outer join
    reg_panel = pd.merge(reg_panel, frame, how="outer", on=["Date", "Token"])

    return reg_panel


def _merge_out_centrality(reg_panel: pd.DataFrame) -> pd.DataFrame:
    """
    Merge outflow eigenvector centrality data.
    """

    # get all csv files in data/data_network/merged/outflow_centrality
    path = rf"{NETWORK_DATA_PATH}/merged/outflow_centrality"  # use your path
    all_files = glob.glob(path + "/*.csv")

    # extract date from file name
    # combine data from all csv files into one dataframe, dropping row number of each csv file
    list_df = []
    for filename in all_files:
        df_out_cent = pd.read_csv(filename, index_col=None, header=0)
        date = filename.split("_")[-1].split(".")[0]
        df_out_cent["Date"] = date
        list_df.append(df_out_cent)

    # combine all csv files into one dataframe
    frame = pd.concat(list_df, axis=0, ignore_index=True)

    # convert date in "YYYYMMDD" to datetime
    frame["Date"] = pd.to_datetime(frame["Date"], format="%Y%m%d")

    # rename the column "token" to "Token"
    frame = frame.rename(columns={"token": "Token"})
    frame = frame.rename(columns={"eigenvector_centrality": "Outflow_centrality"})

    # only keep columnes of "Date", "Token", "Outflow_centrality"
    frame = frame[["Date", "Token", "Outflow_centrality"]]

    # merge the two dataframe into one panel dataset via outer join
    reg_panel = pd.merge(reg_panel, frame, how="outer", on=["Date", "Token"])

    # rename the column "token" to "Token"
    reg_panel = reg_panel.rename(columns={"token": "Token"})

    return reg_panel


def _merge_betweenness(reg_panel: pd.DataFrame) -> pd.DataFrame:
    """
    Merge betweenness centrality data.
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
            df_between["Date"] = date
            list_df.append(df_between)

    # combine all csv files into one dataframe
    frame = pd.concat(list_df, axis=0, ignore_index=True)

    # convert date in "YYYYMMDD" to datetime
    frame["Date"] = pd.to_datetime(frame["Date"], format="%Y%m%d")

    # rename the column "node" to "Token"
    frame = frame.rename(columns={"node": "Token"})

    # merge the two dataframe into one panel dataset via outer join
    reg_panel = pd.merge(reg_panel, frame, how="outer", on=["Date", "Token"])

    return reg_panel


def _merge_prc_gas(reg_panel: pd.DataFrame) -> pd.DataFrame:
    """
    Merge price and gas data.
    """

    # read in the csv file
    prc = pd.read_csv(
        rf"{GLOBAL_DATA_PATH}/token_market/primary_token_price_2.csv",
        index_col=None,
        header=0,
    )

    # convert date in "YYYY-MM-DD" to datetime
    prc["Date"] = pd.to_datetime(prc["Date"], format="%Y-%m-%d")

    # shift the date by one day
    prc["Date"] = prc["Date"] + pd.DateOffset(days=-1)

    # load in the data in data/data_global/gas_fee/avg_gas_fee.csv
    # the dataframe has colume: Date, Gas_fee
    # the dataframe has row number
    # the dataframe is sorted by Date

    # save the column name into a list except for the Date and unnamed column
    col = list(prc.columns)
    col.remove("Date")
    col.remove("Unnamed: 0")

    # read in the csv file
    gas = pd.read_csv(
        rf"{GLOBAL_DATA_PATH}/gas_fee/avg_gas_fee.csv", index_col=None, header=0
    )

    # convert date to datetime
    gas["Date(UTC)"] = pd.to_datetime(gas["Date(UTC)"])

    # rename the column "Date(UTC)" to "Date"
    gas = gas.rename(columns={"Date(UTC)": "Date"})
    gas = gas.rename(columns={"Gas Fee USD": "Gas_fee"})
    gas = gas.rename(columns={"ETH Price (USD)": "ETH_price"})

    # only keep columnes of "Date", "Gas_fee" and "ETH_price"
    gas = gas[["Date", "Gas_fee", "ETH_price"]]

    # merge the prc and gas dataframe into one panel dataset via outer join on "Date"
    prc = pd.merge(prc, gas, how="outer", on=["Date"])

    # load in the data in data/data_global/token_market/PerformanceGraphExport.xls
    # the dataframe has colume: Date, Token, Price
    # the dataframe has row number
    # the dataframe is sorted by Date and Token

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

    # merge the prc and idx dataframe into one panel dataset via outer join on "Date"
    prc = pd.merge(prc, idx, how="outer", on=["Date"])

    # imputation for S&P via forward fill
    prc = prc.sort_values(by=["Date"], ascending=True)
    prc["S&P"] = prc["S&P"].interpolate()

    # drop the unnecessary column "Unnamed: 0"
    prc = prc.drop(columns=["Unnamed: 0"])

    # save the prc to test folder
    prc.to_csv(rf"test/prc.csv", index=False)

    # calculate the log prcurn of price for each token (column)
    # and save them in new columns _log_prcurn
    # reminder: np.log(0) = -inf
    ret = prc.set_index("Date").copy()
    ret = ret.apply(lambda x: (np.log(x) - np.log(x.shift(1))))

    # # reset the index of ret
    # ret = ret.reset_index()

    # copy the ret as a new dataframe named cov
    cov_gas = ret.copy()
    cov_eth = ret.copy()
    cov_sp = ret.copy()
    std = ret.copy()

    # # set the Date column as index
    # ret = ret.set_index("Date")
    # std = std.set_index("Date")

    # sort the dataframe by ascending Date for cov_gas, cov_eth and cov_sp
    ret = ret.sort_values(by="Date", ascending=True)
    cov_gas = cov_gas.sort_values(by="Date", ascending=True)
    cov_eth = cov_eth.sort_values(by="Date", ascending=True)
    cov_sp = cov_sp.sort_values(by="Date", ascending=True)
    std = std.sort_values(by="Date", ascending=True)

    # calcuate the covariance between past 30 days log
    # return of each column in col and that of Gas_fee
    for i in col:
        cov_gas[i] = cov_gas[i].rolling(30).corr(cov_gas["Gas_fee"])

    # calcuate the covariance between past 30 days log
    # return of each column in col and that of ETH_price
    for i in col:
        cov_eth[i] = cov_eth[i].rolling(30).corr(cov_eth["ETH_price"])

    # caculate the covariance between past 30 days log
    # return of each column in col and that of S&P
    for i in col:
        cov_sp[i] = cov_sp[i].rolling(30).corr(cov_sp["S&P"])

    # calculate the standard deviation of each column in col
    for i in col:
        std[i] = std[i].rolling(30).std()

    # drop the Gas_fee and ETH_price and S&P500 columns for ret and cov
    ret = ret.drop(columns=["Gas_fee", "ETH_price", "S&P"])
    cov_gas = cov_gas.drop(columns=["Gas_fee", "ETH_price", "S&P"])
    cov_eth = cov_eth.drop(columns=["Gas_fee", "ETH_price", "S&P"])
    cov_sp = cov_sp.drop(columns=["Gas_fee", "ETH_price", "S&P"])
    std = std.drop(columns=["Gas_fee", "ETH_price", "S&P"])
    gas = gas.drop(columns=["ETH_price"])

    # ret and cov to panel dataset, column: Date, Token, log return and covariance
    ret = ret.stack().reset_index()
    cov_gas = cov_gas.stack().reset_index()
    cov_eth = cov_eth.stack().reset_index()
    cov_sp = cov_sp.stack().reset_index()
    std = std.stack().reset_index()

    # rename the column "level_1" to "Token"
    ret = ret.rename(columns={"level_1": "Token"})
    cov_gas = cov_gas.rename(columns={"level_1": "Token"})
    cov_eth = cov_eth.rename(columns={"level_1": "Token"})
    cov_sp = cov_sp.rename(columns={"level_1": "Token"})
    std = std.rename(columns={"level_1": "Token"})

    # rename the column "0" to "log_return" and "0" to "covariance"
    ret = ret.rename(columns={0: "log_return"})
    cov_gas = cov_gas.rename(columns={0: "corr_gas"})
    cov_eth = cov_eth.rename(columns={0: "corr_eth"})
    cov_sp = cov_sp.rename(columns={0: "corr_sp"})
    std = std.rename(columns={0: "std"})

    # merge the ret, cov_gas, cov_eth, cov_sp dataframe into
    # one panel dataset via outer join on "Date" and "Token
    reg_panel = pd.merge(reg_panel, ret, how="outer", on=["Date", "Token"])
    reg_panel = pd.merge(reg_panel, cov_gas, how="outer", on=["Date", "Token"])
    reg_panel = pd.merge(reg_panel, cov_eth, how="outer", on=["Date", "Token"])
    reg_panel = pd.merge(reg_panel, cov_sp, how="outer", on=["Date", "Token"])
    reg_panel = pd.merge(reg_panel, std, how="outer", on=["Date", "Token"])
    reg_panel = pd.merge(reg_panel, gas, how="outer", on=["Date"])

    # drop the unnecessary column "Unnamed: 0"
    reg_panel = reg_panel.drop(columns=["Unnamed: 0"])

    return reg_panel


def _merge_nonstable(reg_panel: pd.DataFrame) -> pd.DataFrame:
    """
    Merge the dummy variable for non-stablecoin
    """

    # load in the token library for v2 and v3
    token_lib_v2 = pd.DataFrame(
        {"Token": TOKEN_LIB_V2_TOKEN, "Stable": TOKEN_LIB_V2_STABLE}
    )
    token_lib_v3 = pd.DataFrame(
        {"Token": TOKEN_LIB_V3_TOKEN, "Stable": TOKEN_LIB_V3_STABLE}
    )

    # change the Stable to Nonstable
    token_lib_v2["Nonstable"] = 1 - token_lib_v2["Stable"]
    token_lib_v3["Nonstable"] = 1 - token_lib_v3["Stable"]

    # # drop the Stable column
    # token_lib_v2 = token_lib_v2.drop(columns=["Stable"])
    # token_lib_v3 = token_lib_v3.drop(columns=["Stable"])

    # merge the token library for v2 and v3
    token_lib = pd.concat([token_lib_v2, token_lib_v3], ignore_index=True)

    # drop the duplicate token
    token_lib = token_lib.drop_duplicates(subset=["Token"])

    # merge the token library with the panel dataset
    reg_panel = pd.merge(reg_panel, token_lib, how="left", on=["Token"])

    return reg_panel


def _merge_isweth(reg_panel: pd.DataFrame) -> pd.DataFrame:
    """
    Merge the dummy variable for weth
    """

    reg_panel["IsWETH"] = reg_panel["Token"].apply(lambda x: 1 if x == "WETH" else 0)

    return reg_panel


def _merge_exceedance(reg_panel: pd.DataFrame) -> pd.DataFrame:
    """
    Merge the exceedance correlation
    """

    # read in the csv file
    prc = pd.read_csv(
        rf"{GLOBAL_DATA_PATH}/token_market/primary_token_price_2.csv",
        index_col=None,
        header=0,
    )

    # convert date in "YYYY-MM-DD" to datetime
    prc["Date"] = pd.to_datetime(prc["Date"], format="%Y-%m-%d")

    # shift the date by one day
    prc["Date"] = prc["Date"] + pd.DateOffset(days=-1)

    # load in the data in data/data_global/gas_fee/avg_gas_fee.csv
    # the dataframe has colume: Date, Gas_fee
    # the dataframe has row number
    # the dataframe is sorted by Date

    # save the column name into a list except for the Date and unnamed column
    col = list(prc.columns)
    col.remove("Date")
    col.remove("Unnamed: 0")

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

    # merge the prc and idx dataframe into one panel dataset via outer join on "Date"
    prc = pd.merge(prc, idx, how="outer", on=["Date"])

    # imputation for S&P via forward fill
    prc = prc.sort_values(by=["Date"], ascending=True)
    prc["S&P"] = prc["S&P"].interpolate()

    # drop the unnecessary column "Unnamed: 0"
    prc = prc.drop(columns=["Unnamed: 0"])

    # calculate the log prcurn of price for each token (column)
    # and save them in new columns _log_prcurn
    # reminder: np.log(0) = -inf
    ret = prc.set_index("Date").copy()
    ret = ret.apply(lambda x: (np.log(x) - np.log(x.shift(1))))

    # reset the index
    ret = ret.reset_index()

    # remove inf and -inf
    ret = ret.replace([np.inf, -np.inf], np.nan)

    # drop the nan
    ret = ret.dropna()

    # create a new column "exceedance" for the market return
    # if the market return is lower than the historical mean value minus
    # 1.5 times of the historical standard deviation of the market return
    # then the exceedance is 1, otherwise (includes np.nan) np.nan
    # using iterrows() to iterate over the rows of the dataframe
    # TODO: Check the error here
    for index, row in ret.iterrows():
        if (
            row["S&P"]
            < ret.loc[ret["Date"] <= row["Date"], "S&P"].mean()
            - 1.5 * ret.loc[ret["Date"] <= row["Date"], "S&P"].std()
        ):
            ret.at[index, "exceedance"] = 1
        else:
            ret.at[index, "exceedance"] = np.nan

    # set the index to Date
    ret = ret.set_index("Date")

    # sort the dataframe by ascending Date for cov_gas, cov_eth and cov_sp
    ret = ret.sort_values(by=["Date"], ascending=True)

    # caculate the covariance between past 30 days log
    # return of each column in col and that of S&P
    for i in col:
        ret[i] = ret[i].rolling(30).cov(ret["S&P"]) / ret["S&P"].rolling(30).var()

    # each column in col times the exceedance
    for i in col:
        ret[i] = ret[i] * ret["exceedance"]

    # drop the Gas_fee and ETH_price and S&P500 columns for ret and cov
    ret = ret.drop(columns=["S&P", "exceedance"])

    # ret and cov to panel dataset, column: Date, Token, log return and covariance
    ret = ret.stack().reset_index()

    # rename the column "level_1" to "Token"
    ret = ret.rename(columns={"level_1": "Token"})

    # rename the column "0" to "log_return" and "0" to "covariance"
    ret = ret.rename(columns={0: "exceedance"})

    # merge the ret, cov_gas, cov_eth, cov_sp dataframe into
    # one panel dataset via outer join on "Date" and "Token
    reg_panel = pd.merge(reg_panel, ret, how="outer", on=["Date", "Token"])

    return reg_panel


def _merge_gas_volatility(reg_panel: pd.DataFrame) -> pd.DataFrame:
    """
    Function to merge the gas price volatility.
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

    # drop the column "Gas_fee_log_return" and "Gas_fee"
    gas = gas.drop(columns=["Gas_fee_log_return", "Gas_fee"])

    # merge the gas price using outer join
    reg_panel = pd.merge(
        reg_panel,
        gas,
        how="outer",
        on=["Date"],
    )

    return reg_panel


def _merge_stableshare(reg_panel: pd.DataFrame) -> pd.DataFrame:
    """
    Function to merge the stableshare.
    """

    # load in the data/data_global/stablecoin/stablecoin_share.csv
    stable = pd.read_csv(
        rf"{GLOBAL_DATA_PATH}/stablecoin/stablecoin_share.csv", index_col=None, header=0
    )

    # convert date to datetime
    stable["Date"] = pd.to_datetime(stable["Date"])

    # merge the stablecoin share using outer join
    reg_panel = pd.merge(
        reg_panel,
        stable,
        how="outer",
        on=["Date", "Token"],
    )

    return reg_panel


def _merge_avg_eigenvec(reg_panel: pd.DataFrame) -> pd.DataFrame:
    """
    Function to calculate the average eigenvector centrality.
    """

    # calculate the average eigenvector centrality from Inflow_centrality Outflow_centrality
    reg_panel["avg_eigenvector_centrality"] = (
        reg_panel["Inflow_centrality"] + reg_panel["Outflow_centrality"]
    ) / 2

    return reg_panel


def _merge_boom_bust(
    reg_panel: pd.DataFrame, boom_bust: list = BOOM_BUST
) -> pd.DataFrame:
    """
    Function to merge the boom and bust dummy.
    """

    reg_panel["is_boom"] = reg_panel["Date"].apply(
        lambda x: is_boom(boom_bust_list=boom_bust, time=x)
    )

    return reg_panel


def generate_panel() -> pd.DataFrame:
    """
    generate the panel dataset
    """

    # Merge the panel dataset with the volume, share, centrality and betweenness
    reg_panel = _merge_volume_share()
    reg_panel = _merge_volume_in_share(reg_panel)
    reg_panel = _merge_volume_out_share(reg_panel)
    reg_panel = _merge_compound_rate(reg_panel)
    reg_panel = _merge_compound_supply_share(reg_panel)
    reg_panel = _merge_compound_borrow_share(reg_panel)
    reg_panel = _merge_tvl_share(reg_panel)
    reg_panel = _merge_in_centrality(reg_panel)
    reg_panel = _merge_out_centrality(reg_panel)
    reg_panel = _merge_betweenness(reg_panel)
    reg_panel = _merge_prc_gas(reg_panel)
    reg_panel = _merge_nonstable(reg_panel)
    reg_panel = _merge_isweth(reg_panel)
    # reg_panel = _merge_exceedance(reg_panel)
    reg_panel = _merge_gas_volatility(reg_panel)
    reg_panel = _merge_stableshare(reg_panel)
    reg_panel = _merge_avg_eigenvec(reg_panel)
    reg_panel = _merge_boom_bust(reg_panel)

    return reg_panel


if __name__ == "__main__":
    # test the function
    # _merge_boom_bust()
    pass
