"""
plot moving average of time series
"""

import matplotlib.pyplot as plt
import matplotlib.dates as md
import pandas as pd
from environ.process.market.boom_bust import BOOM_BUST

COLOR_DICT = {
    "WETH": "blue",
    "WBTC": "orange",
    "MATIC": "green",
    "USDC": "red",
    "USDT": "purple",
    "DAI": "brown",
    "FEI": "pink",
}

TOKEN_LIST = ["WETH", "WBTC", "MATIC", "USDC", "USDT", "DAI", "FEI"]


def preprocess_ma(
    df: pd.DataFrame, value_colume: str = "value", ma_window: int = 30
) -> pd.DataFrame:
    """
    preprocess the dataframe for moving average
    """
    # rename the value_colume to "value"
    df = df.rename(columns={value_colume: "value"})
    # select only the tokens in TOKEN_LIST
    df = df[df["token"].isin(TOKEN_LIST)]
    # convert time from timestamp to datetime
    df["Date"] = pd.to_datetime(df["time"], unit="s")
    df["time"] = df["Date"].apply(md.date2num)
    # sort the dataframe by date
    df = df.sort_values(by="time").reset_index(drop=True)

    # calculate moving average for each token
    for token in set(df["token"]):
        df[f"{token}_ma"] = df[df["token"] == token]["value"].rolling(ma_window).mean()

    return df


def plot_time_series(df: pd.DataFrame, boom_bust: list[dict] = BOOM_BUST) -> None:
    """
    plot the time series
    """
    # plot the time series
    for token in set(df["token"]):
        plt.plot(df["time"], df["value"], color=COLOR_DICT[token], label=token)

    # plot boom bust cycles
    for cycle in boom_bust:
        plt.axvspan(
            cycle["start"],
            cycle["end"],
            alpha=0.2,
            color="red" if cycle["main_trend"] == "bust" else "green",
        )

    # convert time to date
    date_format = md.DateFormatter("%Y-%m-%d")
    plt.gca().xaxis.set_major_formatter(date_format)

    plt.legend(loc="upper left")
    plt.show()


if __name__ == "__main__":
    # create dummy dataframe with Date, token, and value, where date is between 2021-01-01 and 2022-01-01
    df = pd.DataFrame(
        {
            "Date": [
                "2021-01-01",
                "2021-01-02",
                "2021-01-03",
                "2021-01-04",
                "2021-01-05",
                "2021-01-06",
                "2021-01-07",
                "2021-01-08",
                "2021-01-09",
                "2021-01-10",
                "2021-01-11",
                "2021-01-12",
                "2021-01-13",
                "2021-01-14",
                "2021-01-15",
                "2021-01-16",
                "2021-01-17",
                "2021-01-18",
                "2021-01-19",
                "2021-01-20",
                "2021-01-21",
                "2021-01-22",
                "2021-01-23",
                "2021-01-24",
                "2021-01-25",
            ],
            "time": [
                1451606400,
                1451692800,
                1451779200,
                1451865600,
                1451952000,
                1452038400,
                1452124800,
                1452211200,
                1452297600,
                1452384000,
                1452470400,
                1452556800,
                1452643200,
                1452729600,
                1452816000,
                1452902400,
                1452988800,
                1453075200,
                1453161600,
                1453248000,
                1453334400,
                1453420800,
                1453507200,
                1453593600,
                1453680000,
            ],
            "token": [
                "WETH",
                "WETH",
                "WETH",
                "WETH",
                "WETH",
                "WETH",
                "WETH",
                "WBTC",
                "WBTC",
                "WBTC",
                "WBTC",
                "WBTC",
                "WBTC",
                "WBTC",
                "WBTC",
                "WBTC",
                "WBTC",
                "WBTC",
                "WBTC",
                "WBTC",
                "WBTC",
                "WBTC",
                "WBTC",
                "WBTC",
                "WBTC",
            ],
            "value": [
                1,
                2,
                3,
                4,
                5,
                6,
                7,
                1,
                2,
                3,
                4,
                5,
                6,
                7,
                8,
                9,
                10,
                11,
                12,
                13,
                14,
                15,
                16,
                17,
                18,
            ],
        }
    )
    # convert date to date
    # df["Date"] = pd.to_datetime(df["Date"])

    # preprocess the dataframe
    df = preprocess_ma(df)
    # plot the time series
    plot_time_series(df)
