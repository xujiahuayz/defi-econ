import pandas as pd
import glob
import matplotlib.pyplot as plt
import seaborn as sns

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
