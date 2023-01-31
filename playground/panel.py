import pandas as pd
import glob
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

naming_dict = {
    "TVL_share": "${\it LiquidityShare}$",
    "Inflow_centrality": "${\it InEigenCent}$",
    "Outflow_centrality": "${\it OutEigenCent}$",
    "Volume_share": "${\it VShare}$",
    "Borrow_share": "${\it BorrowShare}$",
    "Supply_share": "${\it SupplyShare}$",
}


def reg_panel():

    reg_panel = []

    # combine all csv files in data/data_network/merged/volume_share.
    # each csv file's title contains the date, and has columes: Token, Volume, and has row number
    # the new combined dataframe has colume: Date, Token, Volume

    # get all csv files in data/data_network/merged/volume_share
    path = rf"data/data_network/merged/volume_share"  # use your path
    all_files = glob.glob(path + "/*.csv")

    # extract date from file name
    # combine data from all csv files into one dataframe, dropping row number of each csv file
    li = []
    for filename in all_files:
        df = pd.read_csv(filename, index_col=None, header=0)
        date = filename.split("_")[-1].split(".")[0]
        df["Date"] = date
        li.append(df)

    # combine all csv files into one dataframe
    reg_panel = pd.concat(li, axis=0, ignore_index=True)

    # convert date to datetime
    reg_panel["Date"] = pd.to_datetime(reg_panel["Date"], format="%Y%m%d")

    # drop the column "Unnamed: 0"
    reg_panel = reg_panel.drop(columns=["Unnamed: 0"])

    # rename the Volume column to Volume_share
    reg_panel = reg_panel.rename(columns={"Volume": "Volume_share"})

    # combine all csv files with "_processed" at the end of the name in data/data_compound into a panel dataset.
    # each csv file's title contains the date, and has columes: Token, Borrow, and has row number
    # the new combined dataframe has colume: Date, Token, Borrow
    # get all csv files in data/data_compound
    path = rf"data/data_compound"  # use your path
    all_files = glob.glob(path + "/*_processed.csv")

    # merge all csv files into one dataframe with token name in the file name as the primary key
    li = []
    for filename in all_files:
        df = pd.read_csv(filename, index_col=None, header=0)
        token = filename.split("_")[-2]
        # skip the file with token name "WBTC2"
        if token == "WBTC2":
            continue

        if token == "ETH":
            df["token"] = "WETH"
        else:
            df["token"] = token

        li.append(df)

    # combine all csv files into one dataframe
    frame = pd.concat(li, axis=0, ignore_index=True)

    # calculate the borrow share of each token each day
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

    # combine all csv files with "_processed" at the end of the name in data/data_compound into a panel dataset.
    # each csv file's title contains the date, and has columes: Token, Borrow, and has row number
    # the new combined dataframe has colume: Date, Token, Borrow
    # get all csv files in data/data_compound
    path = rf"data/data_compound"  # use your path
    all_files = glob.glob(path + "/*_processed.csv")

    # merge all csv files into one dataframe with token name in the file name as the primary key
    li = []
    for filename in all_files:
        df = pd.read_csv(filename, index_col=None, header=0)
        token = filename.split("_")[-2]
        # skip the file with token name "WBTC2"
        if token == "WBTC2":
            continue

        if token == "ETH":
            df["token"] = "WETH"
        else:
            df["token"] = token

        li.append(df)

    # combine all csv files into one dataframe
    frame = pd.concat(li, axis=0, ignore_index=True)

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
    # combine all csv files in data/data_network/merged/volume_share.
    # each csv file's title contains the date, and has columes: Token, Volume, and has row number
    # the new combined dataframe has colume: Date, Token, Volume

    # get all csv files in data/data_network/merged/volume_share
    path = rf"data/data_network/merged/tvl_share"  # use your path
    all_files = glob.glob(path + "/*.csv")

    # extract date from file name
    # combine data from all csv files into one dataframe, dropping row number of each csv file
    li = []
    for filename in all_files:
        df = pd.read_csv(filename, index_col=None, header=0)
        date = filename.split("_")[-1].split(".")[0]
        df["Date"] = date
        li.append(df)

    # combine all csv files into one dataframe
    frame = pd.concat(li, axis=0, ignore_index=True)

    # convert date in "YYYYMMDD" to datetime
    frame["Date"] = pd.to_datetime(frame["Date"], format="%Y%m%d")

    # rename the column "token" to "Token"
    frame = frame.rename(columns={"token": "Token"})
    frame = frame.rename(columns={"total_tvl": "TVL_share"})

    # merge the two dataframe into one panel dataset via outer join
    reg_panel = pd.merge(reg_panel, frame, how="outer", on=["Date", "Token"])

    # combine all csv files in data/data_network/merged/inflow_centrality
    # each csv file's title contains the date, and has columes: Token, eigenvector_centrality, and has row number
    # the new combined dataframe has colume: Date, Token, eigenvector_centrality

    # get all csv files in data/data_network/merged/inflow_centrality
    path = rf"data/data_network/merged/inflow_centrality"  # use your path
    all_files = glob.glob(path + "/*.csv")

    # extract date from file name
    # combine data from all csv files into one dataframe, dropping row number of each csv file
    li = []
    for filename in all_files:
        df = pd.read_csv(filename, index_col=None, header=0)
        date = filename.split("_")[-1].split(".")[0]
        df["Date"] = date
        li.append(df)

    # combine all csv files into one dataframe
    frame = pd.concat(li, axis=0, ignore_index=True)

    # convert date in "YYYYMMDD" to datetime
    frame["Date"] = pd.to_datetime(frame["Date"], format="%Y%m%d")

    # rename the column "token" to "Token"
    frame = frame.rename(columns={"token": "Token"})
    frame = frame.rename(columns={"eigenvector_centrality": "Inflow_centrality"})

    # only keep columnes of "Date", "Token", "Inflow_centrality"
    frame = frame[["Date", "Token", "Inflow_centrality"]]

    # merge the two dataframe into one panel dataset via outer join
    reg_panel = pd.merge(reg_panel, frame, how="outer", on=["Date", "Token"])

    # combine all csv files in data/data_network/merged/outflow_centrality
    # each csv file's title contains the date, and has columes: Token, eigenvector_centrality, and has row number
    # the new combined dataframe has colume: Date, Token, eigenvector_centrality

    # get all csv files in data/data_network/merged/outflow_centrality
    path = rf"data/data_network/merged/outflow_centrality"  # use your path
    all_files = glob.glob(path + "/*.csv")

    # extract date from file name
    # combine data from all csv files into one dataframe, dropping row number of each csv file
    li = []
    for filename in all_files:
        df = pd.read_csv(filename, index_col=None, header=0)
        date = filename.split("_")[-1].split(".")[0]
        df["Date"] = date
        li.append(df)

    # combine all csv files into one dataframe
    frame = pd.concat(li, axis=0, ignore_index=True)

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

    # load in the data in data/data_global/token_market/primary_token_price_2.csv
    # the dataframe has colume: Date, Token, Price
    # the dataframe has row number
    # the dataframe is sorted by Date and Token

    # read in the csv file
    prc = pd.read_csv(
        rf"data/data_global/token_market/primary_token_price_2.csv",
        index_col=None,
        header=0,
    )

    # convert date in "YYYY-MM-DD" to datetime
    prc["Date"] = pd.to_datetime(prc["Date"], format="%Y-%m-%d")
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
        rf"data/data_global/gas_fee/avg_gas_fee.csv", index_col=None, header=0
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
    prc = pd.merge(prc, gas, how="left", on=["Date"])

    # load in the data in data/data_global/token_market/PerformanceGraphExport.xls
    # the dataframe has colume: Date, Token, Price
    # the dataframe has row number
    # the dataframe is sorted by Date and Token

    # read in the csv file and ignore the first six rows
    idx = pd.read_excel(
        rf"data/data_global/token_market/PerformanceGraphExport.xls",
        index_col=None,
        header=6,
    )

    # convert Effective date to datetime
    idx["Date"] = pd.to_datetime(idx["Date"])

    # merge the prc and idx dataframe into one panel dataset via outer join on "Date"
    prc = pd.merge(prc, idx, how="left", on=["Date"])

    # drop the unnecessary column "Unnamed: 0"
    prc = prc.drop(columns=["Unnamed: 0"])

    # calculate the log prcurn of price for each token (column) and save them in new columns _log_prcurn

    ret = prc.set_index("Date").copy()
    ret = ret.apply(lambda x: np.log(x) - np.log(x.shift(1)))

    # copy the ret as a new dataframe named cov
    cov_gas = ret.copy()
    cov_eth = ret.copy()
    cov_sp = ret.copy()

    # sort the dataframe by ascending Date for cov_gas, cov_eth and cov_sp
    cov_gas = cov_gas.sort_values(by="Date", ascending=True)
    cov_eth = cov_eth.sort_values(by="Date", ascending=True)
    cov_sp = cov_sp.sort_values(by="Date", ascending=True)

    # calcuate the covariance between past 30 days log return of each column in col and that of Gas_fee
    for i in col:
        cov_gas[i] = ret[i].rolling(30).cov(ret["Gas_fee"])

    # calcuate the covariance between past 30 days log return of each column in col and that of ETH_price
    for i in col:
        cov_eth[i] = ret[i].rolling(30).cov(ret["ETH_price"])

    # caculate the covariance between past 30 days log return of each column in col and that of S&P
    for i in col:
        cov_sp[i] = ret[i].rolling(30).cov(ret["S&P"])

    print(ret["S&P"])

    # drop the Gas_fee and ETH_price and S&P500 columns for ret and cov
    ret = ret.drop(columns=["Gas_fee", "ETH_price", "S&P"])
    cov_gas = cov_gas.drop(columns=["Gas_fee", "ETH_price", "S&P"])
    cov_eth = cov_eth.drop(columns=["Gas_fee", "ETH_price", "S&P"])
    cov_sp = cov_sp.drop(columns=["Gas_fee", "ETH_price", "S&P"])

    # ret and cov to panel dataset, column: Date, Token, log return and covariance
    ret = ret.stack().reset_index()
    cov_gas = cov_gas.stack().reset_index()
    cov_eth = cov_eth.stack().reset_index()
    cov_sp = cov_sp.stack().reset_index()

    # rename the column "level_1" to "Token"
    ret = ret.rename(columns={"level_1": "Token"})
    cov_gas = cov_gas.rename(columns={"level_1": "Token"})
    cov_eth = cov_eth.rename(columns={"level_1": "Token"})
    cov_sp = cov_sp.rename(columns={"level_1": "Token"})

    # rename the column "0" to "log_return" and "0" to "covariance"
    ret = ret.rename(columns={0: "log_return"})
    cov_gas = cov_gas.rename(columns={0: "cov_gas"})
    cov_eth = cov_eth.rename(columns={0: "cov_eth"})
    cov_sp = cov_sp.rename(columns={0: "cov_sp"})

    # # merge the reg_panel and cov dataframe into one panel dataset via outer join on "Date" and "Token"
    # reg_panel = pd.merge(ret, cov, how="left", on=["Date", "Token"])

    # # merge the reg_panel and ret dataframe into one panel dataset via outer join on "Date" and "Token"
    # reg_panel = pd.merge(reg_panel, ret, how="left", on=["Date", "Token"])

    # create the correlation matrix
    corr = reg_panel.corr()

    # change the column names to be more readable
    corr = corr.rename(columns=naming_dict)

    # plot the heatmap
    sns.heatmap(
        corr,
        xticklabels=corr.columns,
        yticklabels=corr.columns,
        annot=True,
        cmap="Greens",
    )

    # tight layout
    plt.tight_layout()

    # save the figure
    plt.savefig(rf"figures/correlation_matrix.pdf")

    plt.show()

    # save the correlation matrix as a csv file
    corr.to_csv(rf"tables/correlation_matrix.csv")


if __name__ == "__main__":
    reg_panel()
