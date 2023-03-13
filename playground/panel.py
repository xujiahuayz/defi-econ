import pandas as pd
import glob
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib.colors as colors
import statsmodels.api as sm
from stargazer.stargazer import Stargazer
from environ.constants import NAMING_DICT_OLD


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

    # combine all csv files in data/data_network/merged/volume_in_share
    # each csv file's title contains the date, and has columes: Token, Volume, and has row number
    # the new combined dataframe has colume: Date, Token, Volume

    # get all csv files in data/data_network/merged/volume_in_share
    path = rf"data/data_network/merged/volume_in_share"  # use your path
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

    # combine all csv files in data/data_network/merged/volume_out_share
    # each csv file's title contains the date, and has columes: Token, Volume, and has row number
    # the new combined dataframe has colume: Date, Token, Volume

    # get all csv files in data/data_network/merged/volume_out_share
    path = rf"data/data_network/merged/volume_out_share"  # use your path
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

    # get all csv files in data/data_betweenness/betweenness
    path = rf"data/data_betweenness/betweenness"  # use your path
    all_files = glob.glob(path + "/*.csv")

    # extract date from file name
    # combine data from all csv files into one dataframe, dropping row number of each csv file
    li = []
    for filename in all_files:
        if filename.split("_")[-2].split(".")[0] == "v2v3":
            df = pd.read_csv(filename, index_col=None, header=0)
            date = filename.split("_")[-1].split(".")[0]
            df["Date"] = date
            li.append(df)

    # combine all csv files into one dataframe
    frame = pd.concat(li, axis=0, ignore_index=True)

    # convert date in "YYYYMMDD" to datetime
    frame["Date"] = pd.to_datetime(frame["Date"], format="%Y%m%d")

    # rename the column "node" to "Token"
    frame = frame.rename(columns={"node": "Token"})

    # merge the two dataframe into one panel dataset via outer join
    reg_panel = pd.merge(reg_panel, frame, how="outer", on=["Date", "Token"])

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
        skiprows=6,
        skipfooter=4,
        usecols="A:B",
    )

    # convert Effective date to datetime
    idx["Date"] = pd.to_datetime(idx["Date"])

    # merge the prc and idx dataframe into one panel dataset via outer join on "Date"
    prc = pd.merge(prc, idx, how="left", on=["Date"])

    # drop the unnecessary column "Unnamed: 0"
    prc = prc.drop(columns=["Unnamed: 0"])

    # sort the dataframe by ascending Date and Token
    prc = prc.sort_values(by=["Date"], ascending=True)

    # calculate the log prcurn of price for each token (column) and save them in new columns _log_prcurn

    ret = prc.set_index("Date").copy()
    ret = ret.apply(lambda x: np.log(x) - np.log(x.shift(1)))

    # copy the ret as a new dataframe named cov
    cov_gas = ret.copy()
    cov_eth = ret.copy()
    cov_sp = ret.copy()
    std = ret.copy()

    # sort the dataframe by ascending Date for cov_gas, cov_eth and cov_sp
    ret = ret.sort_values(by="Date", ascending=True)
    cov_gas = cov_gas.sort_values(by="Date", ascending=True)
    cov_eth = cov_eth.sort_values(by="Date", ascending=True)
    cov_sp = cov_sp.sort_values(by="Date", ascending=True)
    std = std.sort_values(by="Date", ascending=True)

    # calcuate the covariance between past 30 days log return of each column in col and that of Gas_fee
    for i in col:
        cov_gas[i] = ret[i].rolling(30).cov(ret["Gas_fee"])

    # calcuate the covariance between past 30 days log return of each column in col and that of ETH_price
    for i in col:
        cov_eth[i] = ret[i].rolling(30).cov(ret["ETH_price"])

    # caculate the covariance between past 30 days log return of each column in col and that of S&P
    for i in col:
        cov_sp[i] = ret[i].rolling(30).cov(ret["S&P"])

    # calculate the standard deviation of each column in col
    for i in col:
        std[i] = ret[i].rolling(30).std()

    # drop the Gas_fee and ETH_price and S&P500 columns for ret and cov
    ret = ret.drop(columns=["Gas_fee", "ETH_price", "S&P"])
    cov_gas = cov_gas.drop(columns=["Gas_fee", "ETH_price", "S&P"])
    cov_eth = cov_eth.drop(columns=["Gas_fee", "ETH_price", "S&P"])
    cov_sp = cov_sp.drop(columns=["Gas_fee", "ETH_price", "S&P"])
    std = std.drop(columns=["Gas_fee", "ETH_price", "S&P"])

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
    cov_gas = cov_gas.rename(columns={0: "cov_gas"})
    cov_eth = cov_eth.rename(columns={0: "cov_eth"})
    cov_sp = cov_sp.rename(columns={0: "cov_sp"})
    std = std.rename(columns={0: "std"})

    # merge the ret, cov_gas, cov_eth, cov_sp dataframe into one panel dataset via outer join on "Date" and "Token
    # reg_panel = pd.merge(reg_panel, ret, how="outer", on=["Date", "Token"])
    # reg_panel = pd.merge(reg_panel, cov_gas, how="outer", on=["Date", "Token"])
    # reg_panel = pd.merge(reg_panel, cov_eth, how="outer", on=["Date", "Token"])
    # reg_panel = pd.merge(reg_panel, cov_sp, how="outer", on=["Date", "Token"])
    reg_panel = pd.merge(reg_panel, std, how="outer", on=["Date", "Token"])

    # drop the unnecessary column "Unnamed: 0"
    # TODO: check how it is generated
    reg_panel = reg_panel.drop(columns=["Unnamed: 0"])

    # create the correlation matrix and set the decimal places to 2 and keep the digits
    corr = reg_panel.corr().round(2)

    # change the column names to be more readable
    corr = corr.rename(columns=NAMING_DICT_OLD)

    # set the borrow_rate, borrow_rate to 1
    # TODO: check why
    corr.loc["borrow_rate", "${\it BorrowAPY}^{USD}$"] = 1

    # This dictionary defines the colormap
    cdict3 = {
        "red": (
            (0.0, 0.0, 0.0),
            (0.25, 0.0, 0.0),
            (0.5, 0.8, 1.0),
            (0.75, 1.0, 1.0),
            (1.0, 0.4, 1.0),
        ),
        "green": (
            (0.0, 0.0, 0.0),
            (0.25, 0.0, 0.0),
            (0.5, 0.9, 0.9),
            (0.75, 0.0, 0.0),
            (1.0, 0.0, 0.0),
        ),
        "blue": (
            (0.0, 0.0, 0.4),
            (0.25, 1.0, 1.0),
            (0.5, 1.0, 0.8),
            (0.75, 0.0, 0.0),
            (1.0, 0.0, 0.0),
        ),
        "alpha": ((0.0, 1.0, 1.0), (0.5, 0.3, 0.3), (1.0, 1.0, 1.0)),
    }

    # Create the colormap using the dictionary with the range of -1 to 1
    # make sure the range of the ledgend is -1 to 1
    GnRd = colors.LinearSegmentedColormap("GnRd", cdict3)

    # plot the heatmap
    sns.heatmap(
        corr,
        xticklabels=corr.columns,
        yticklabels=corr.columns,
        annot=True,
        cmap=GnRd,
        vmin=-1,
        vmax=1,
        annot_kws={"size": 7},
    )

    # tight layout
    plt.tight_layout()

    # save the figure
    plt.savefig(rf"figures/correlation_matrix.pdf")

    # save the correlation matrix as a csv file
    corr.to_csv(rf"tables/correlation_matrix.csv")

    # rename the panel column names to be more readable
    reg_panel = reg_panel.rename(columns=NAMING_DICT_OLD)

    # calculate the summary statistics of the panel dataset
    summary = reg_panel.describe()

    # take the transpose of the summary statistics
    summary = summary.T

    # save the summary statistics as a csv file
    summary.to_csv(rf"tables/summary_statistics.csv")

    # save the summary statistics as a latex file
    with open(rf"tables/summary_statistics.tex", "w") as tf:
        tf.write(summary.to_latex())

    # # create the dummy variable for the Date
    # time_dummies = pd.get_dummies(reg_panel["Date"])

    # # reg_panel['year'] = reg_panel['date'].dt.year
    # reg_panel["year_month"] = reg_panel["Date"].dt.to_period("M")
    # # time_dummies = pd.get_dummies(reg_panel['year'], prefix='year')
    # time_dummies = pd.get_dummies(reg_panel["year_month"], prefix="month")

    # reg_panel = pd.concat([reg_panel, time_dummies], axis=1)

    # # panel regression with time fixed effects of Date between the Inflow_centrality with Volume_share
    # # create the dependent variable
    Y = reg_panel["${\it VShare}$"]

    X = reg_panel[
        ["${\it EigenCent}^{In}$", "${\it BetwCent}^C$", "${\it SupplyShare}$"]
    ]

    X = sm.add_constant(X)

    model_1 = sm.OLS(Y, X, missing="drop")

    # fit the model_1
    results_1 = model_1.fit()

    X_2 = reg_panel[
        ["${\it EigenCent}^{Out}$", "${\it BetwCent}^V$", "${\it SupplyShare}$"]
    ]

    X_2 = sm.add_constant(X_2)

    model_2 = sm.OLS(Y, X_2, missing="drop")

    # fit the model_1
    results_2 = model_2.fit()

    # use stargazer to create the regression table
    stargazer = Stargazer([results_1, results_2])

    # set the title of the table
    stargazer.title("Simple Linear Regression")

    # customize the column name
    stargazer.custom_columns(["${\it VShare}$", "${\it VShare}$"], [1, 1])

    # save the table to a latex file
    with open(rf"tables/regression_table.tex", "w") as tf:
        tf.write(stargazer.render_latex())

    # save the panel dataset as a csv file
    reg_panel.to_csv(rf"tables/regression_panel.csv")


if __name__ == "__main__":
    reg_panel()
