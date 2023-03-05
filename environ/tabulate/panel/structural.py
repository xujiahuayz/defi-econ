"""
Function to construct construal regression 
"""

import pandas as pd
from tqdm import tqdm
from environ.utils.config_parser import Config

# Initialize config
config = Config()

# Initialize data path
GLOBAL_DATA_PATH = config["dev"]["config"]["data"]["GLOBAL_DATA_PATH"]


def _aggreage_token_data() -> pd.DataFrame:
    """
    Function to aggregate the token data
    """

    # read in the token list
    token_list = pd.read_excel(
        rf"{GLOBAL_DATA_PATH}/coingecko/token_list/CoinGecko Token API List.xlsx",
    )

    token_data_dfs = []

    # iterate through the token list using tqdm and iterrows
    for _, row in tqdm(
        token_list.loc[token_list["attempt"] < 0].iterrows(),
        total=token_list.loc[token_list["attempt"] < 0].shape[0],
    ):
        # read in the token data
        token_data = pd.read_csv(
            rf"{GLOBAL_DATA_PATH}/coingecko/token_data/{row['Id']}.csv",
        )

        # add the columns of Id, Symbol, and Name
        token_data["Id"] = row["Id"]
        token_data["Symbol"] = row["symbol"]
        token_data["Name"] = row["name"]

        # append the token data to the list
        token_data_dfs.append(token_data)

    # concatenate the list of dataframes
    token_data = pd.concat(token_data_dfs, ignore_index=True)

    return token_data


def _data_cleaning(token_data: pd.DataFrame) -> pd.DataFrame:
    """
    Function to implement data manipulation and data clearning
    in terms of the market cap and winsorizing
    """

    # correct the anomaly
    token_data["time"] = token_data["time"].dt.round(freq="D")

    # sort the dataframe by the time
    token_data = token_data.sort_values(by=["Id", "time"], ascending=True)

    # calculate the return via groupby
    token_data["ret"] = token_data.groupby("Id")["prices"].pct_change()
    token_data["mv_l1"] = token_data.groupby("Id")["market_caps"].shift(1)

    # drop 0 and nan

    # market cap more than 1,000,000
    token_data = token_data.loc[token_data["market_caps"] > 10**6]

    # winsorize the return by 1% and 99%
    token_data["ret"] = token_data["ret"].clip(lower=token_data["ret"].quantile(0.01))
    token_data["ret"] = token_data["ret"].clip(upper=token_data["ret"].quantile(0.99))

    # calculate the market cap weighted market return
    mret = token_data.copy()
    mret["ret"] = mret["ret"] * mret["mv_l1"]
    mret = mret.groupby(["time"], as_index=False)[["ret", "mv_l1", "market_caps"]].sum()
    mret["mret"] = mret["ret"] / mret["mv_l1"]
    mret["macap"] = mret["market_caps"]
    mret = mret.drop(columns=["ret", "mv_l1", "market_caps"])

    # merge the market return dataframe
    token_data = token_data.merge(mret, on="time", how="left", validate="m:1")

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

    # rename the column 'Date' to 'time'
    rf_df.rename(columns={"Date": "time"}, inplace=True)

    # merge the rf_df with the token_data
    token_data = token_data.merge(rf_df, on="time", how="left", validate="m:1")

    # calculate the excess return for ret and mret
    token_data["eret"] = token_data["ret"] - token_data["RF"]
    token_data["cmkt"] = token_data["mret"] - token_data["RF"]

    return token_data


if __name__ == "__main__":
    print(_aggreage_token_data())
