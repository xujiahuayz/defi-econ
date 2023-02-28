"""
Functions to construct value stores proxies for Panel.
"""

import warnings
import pandas as pd
import numpy as np
import datetime
from tqdm import tqdm
import statsmodels.api as sm
from environ.utils.config_parser import Config
from environ.utils.info_logger import print_info_log

# ignore the warnings
warnings.filterwarnings("ignore")

# Initialize config
config = Config()

# Initialize data path
GLOBAL_DATA_PATH = config["dev"]["config"]["data"]["GLOBAL_DATA_PATH"]


def _beta(reg_panel: pd.DataFrame) -> pd.DataFrame:
    """
    Construct a value store proxy for the beta-hedge value store.
    """

    # information log
    print_info_log("Constructing the beta-hedge value store proxy.", "process")

    # Load in the token price data
    prc = pd.read_csv(
        rf"{GLOBAL_DATA_PATH}/token_market/primary_token_price_2.csv",
        index_col=None,
        header=0,
    )

    # convert date in "YYYY-MM-DD" to datetime
    prc["Date"] = pd.to_datetime(prc["Date"], format="%Y-%m-%d")

    # shift the date by one day
    prc["Date"] = prc["Date"] + pd.DateOffset(days=-1)

    # save the column name into a list except for the Date and unnamed column
    col = list(prc.columns)
    col.remove("Date")
    col.remove("Unnamed: 0")

    # load in the data in data/data_global/token_market/PerformanceGraphExport.xls
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

    # merge the prc and idx dataframe into one panel dataset via left join on "Date"
    prc = pd.merge(prc, idx, how="left", on=["Date"])

    # imputation for S&P via forward fill
    prc = prc.sort_values(by=["Date"], ascending=True)
    prc["S&P"] = prc["S&P"].interpolate()

    # drop the unnecessary column "Unnamed: 0"
    prc = prc.drop(columns=["Unnamed: 0"])

    # calculate the simple return of price for each token (column)
    # and save them in new columns _ret
    ret = prc.set_index("Date").copy()
    ret = ret.apply(lambda x: (x - x.shift(1)) / x.shift(1))

    # drop the infinities
    ret = ret.replace([np.inf, -np.inf], np.nan)

    # load in the data in data/data_global/risk_free_rate/F-F_Research_Data_Factors_daily.CSV
    # read in the csv file and ignore the first six rows
    rf_df = pd.read_csv(
        rf"{GLOBAL_DATA_PATH}/risk_free_rate/F-F_Research_Data_Factors_daily.CSV",
        skiprows=[0, 1, 2, 3, 4],
        skipfooter=2,
        engine="python",
        names=["Date", "Mkt-RF", "SMB", "HML", "RF"],
    )

    # convert date in "YYYYMMDD" to datetime
    rf_df["Date"] = pd.to_datetime(rf_df["Date"], format="%Y%m%d")

    # only keep the Date and RF columns
    rf_df = rf_df[["Date", "RF"]]

    # Unit conversion
    rf_df["RF"] = rf_df["RF"].map(float) / 100

    # expand the time range of the rf_df to every day
    rf_df = rf_df.set_index("Date").copy()
    rf_df = rf_df.resample("D").interpolate()
    rf_df.reset_index(inplace=True)

    # merge the ret and rf_df dataframe into one panel dataset via outer join on "Date"
    ret = pd.merge(ret, rf_df, how="left", on=["Date"])

    # subtract the risk free rate from the return
    for i in col:
        ret[i] = ret[i] - ret["RF"]

    # subtract the risk free rate from the S&P return
    ret["S&P"] = ret["S&P"] - ret["RF"]

    # sort the dataframe by date
    ret = ret.sort_values(by=["Date"], ascending=True)

    # # get the 30-day rolling beta of each token via rolling linear regression using statsmodels
    # for col_name in tqdm(col):
    #     for _, row in ret.iterrows():

    #         # skip the sample with missing values
    #         if (
    #             ret.loc[
    #                 (ret["Date"] > row["Date"] - datetime.timedelta(days=30))
    #                 & (ret["Date"] <= row["Date"]),
    #                 [col_name, "S&P"],
    #             ]
    #             .isnull()
    #             .values.any()
    #         ):
    #             continue

    #         # calculate the beta
    #         ret.loc[ret["Date"] == row["Date"], f"{col_name}_beta"] = (
    #             sm.OLS(
    #                 endog=ret.loc[
    #                     (ret["Date"] > row["Date"] - datetime.timedelta(days=30))
    #                     & (ret["Date"] <= row["Date"]),
    #                     col_name,
    #                 ],
    #                 exog=sm.add_constant(
    #                     ret.loc[
    #                         (ret["Date"] > row["Date"] - datetime.timedelta(days=30))
    #                         & (ret["Date"] <= row["Date"]),
    #                         "S&P",
    #                     ]
    #                 ),
    #             )
    #             .fit()
    #             .params[1]
    #         )

    for i in col:
        rolling_cov = ret[i].rolling(30).cov(ret["S&P"])
        rolling_var = ret["S&P"].rolling(30).var()
        rolling_beta = rolling_cov / rolling_var
        ret[f"{i}_beta"] = rolling_beta

    # set the date as index
    ret = ret.set_index("Date")

    # drop the columns in col and "S&P" and "RF"
    ret = ret.drop(columns=col + ["S&P", "RF"])

    # rename the columns to the original token name
    ret = ret.rename(columns={f"{col_name}_beta": col_name for col_name in col})

    # convert the dataframe to panel dataset
    ret = ret.stack().reset_index()

    # rename the columns
    ret = ret.rename(columns={"level_1": "Token"})

    # beta row
    ret = ret.rename(columns={0: "beta"})

    # merge the ret into reg_panel
    reg_panel = pd.merge(reg_panel, ret, how="outer", on=["Date", "Token"])

    return reg_panel


def _sentiment(reg_panel: pd.DataFrame) -> pd.DataFrame:
    """
    Merge the sentiment score with the regression panel dataset
    """

    # information log
    print_info_log("Constructing the sentiment value store proxy.", "process")

    # load in the sentiment score
    sentiment = pd.read_csv(rf"{GLOBAL_DATA_PATH}/sentiment/sentiment.csv")

    # convert date in "YYYY-MM-DD" to datetime
    sentiment["Date"] = pd.to_datetime(sentiment["Date"], format="%Y-%m-%d")

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

    # save the column name into a list except for the Date and unnamed column
    col = list(prc.columns)
    col.remove("Date")
    col.remove("Unnamed: 0")

    # merge the prc and sentiment dataframe into one panel dataset via outer join on "Date"
    prc = pd.merge(prc, sentiment, how="outer", on=["Date"])

    # sort the dataframe by date
    prc = prc.sort_values(by=["Date"], ascending=True)

    # drop the unnecessary column "Unnamed: 0"
    prc = prc.drop(columns=["Unnamed: 0"])

    # calculate the log prcurn of price for each token (column)
    # and save them in new columns _log_prcurn
    # reminder: np.log(0) = -inf
    ret = prc.set_index("Date").copy()
    ret = ret.apply(lambda x: (np.log(x) - np.log(x.shift(1))))

    # caculate the covariance between past 30 days
    for col_name in col:
        ret[col_name] = ret[col_name].rolling(30).corr(ret["sentiment"])

    # drop the column "sentiment"
    cov_stm = ret.drop(columns=["sentiment"])

    # conver the dataframe to panel dataset
    cov_stm = cov_stm.stack().reset_index()

    # rename the columns
    cov_stm = cov_stm.rename(columns={"level_1": "Token"})
    cov_stm = cov_stm.rename(columns={0: "corr_sentiment"})

    # merge the sentiment into reg_panel
    reg_panel = pd.merge(reg_panel, cov_stm, how="outer", on=["Date", "Token"])

    return reg_panel


def _rolling_average_return(reg_panel: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the last 30 day average return of each token
    """

    # information log
    print_info_log(
        "Constructing the 30-day average return value store proxy.", "process"
    )

    # Load in the token price data
    prc = pd.read_csv(
        rf"{GLOBAL_DATA_PATH}/token_market/primary_token_price_2.csv",
        index_col=None,
        header=0,
    )

    # convert date in "YYYY-MM-DD" to datetime
    prc["Date"] = pd.to_datetime(prc["Date"], format="%Y-%m-%d")

    # shift the date by one day
    prc["Date"] = prc["Date"] + pd.DateOffset(days=-1)

    # Sort the dataframe by date
    prc = prc.sort_values(by=["Date"], ascending=True)

    # save the column name into a list except for the Date and unnamed column
    col = list(prc.columns)
    col.remove("Date")
    col.remove("Unnamed: 0")

    # calculate the simple return of price for each token (column)
    # and save them in new columns _ret
    ret = prc.set_index("Date").copy()
    ret = ret.apply(lambda x: (np.log(x) - np.log(x.shift(1))))

    # drop the infinities
    ret = ret.replace([np.inf, -np.inf], np.nan)

    # get the 30-day rolling average return of each token
    for col_name in tqdm(col):
        ret[col_name] = ret[col_name].rolling(30).mean()

    # drop Unnamed: 0 column
    ret = ret.drop(columns=["Unnamed: 0"])

    # convert the dataframe to panel dataset
    ret = ret.stack().reset_index()

    # rename the columns
    ret = ret.rename(columns={"level_1": "Token"})

    # average return row
    ret = ret.rename(columns={0: "average_return"})

    # merge the ret into reg_panel
    reg_panel = pd.merge(reg_panel, ret, how="outer", on=["Date", "Token"])

    return reg_panel


def merge_safeness_measurement(reg_panel: pd.DataFrame) -> pd.DataFrame:
    """
    Merge the proxy variables with the regression panel dataset
    """

    # merge the price
    reg_panel = _beta(reg_panel)

    # merge the sentiment
    reg_panel = _sentiment(reg_panel)

    # merge the rolling average return
    reg_panel = _rolling_average_return(reg_panel)

    return reg_panel


if __name__ == "__main__":
    # example usage
    pass
