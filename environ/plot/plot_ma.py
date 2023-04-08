"""
plot moving average of time series
"""

import glob
from pathlib import Path

import matplotlib.dates as md
import matplotlib.pyplot as plt
import pandas as pd

from environ.constants import (
    ALL_TOKEN_DICT,
    FIGURE_PATH,
    DATA_PATH,
    EVENT_DATE_LIST,
    KEY_TOKEN_LIST,
    SAMPLE_PERIOD,
)
from environ.process.market.boom_bust import BOOM_BUST
from environ.utils.variable_constructer import ma_variable_columns, name_ma_variable


def file_to_df(
    file_folder: str,
) -> pd.DataFrame:
    frame = pd.DataFrame()
    for filename in glob.glob(str(file_folder) + "/*.csv"):
        date = filename.split("_")[-1].split(".")[0]
        df_vol_tvl = pd.read_csv(
            filename,
            header=0,
            #   index_col=0
        )
        df_vol_tvl["Date"] = date
        frame = pd.concat([frame, df_vol_tvl], ignore_index=True)
    return frame


def preprocess_ma(
    df: pd.DataFrame,
    ma_window: int = 30,
    value_colume: str = "value",
    token_col_name: str = "token",
) -> pd.DataFrame:
    """
    preprocess the dataframe for moving average
    """

    # select only the tokens in TOKEN_LIST
    df = df[df[token_col_name].isin(KEY_TOKEN_LIST)][
        [token_col_name, value_colume, "Date"]
    ]
    # convert time from timestamp to datetime
    df["Date"] = pd.to_datetime(df["Date"])
    df = ma_variable_columns(
        data=df,
        variable=value_colume,
        time_variable="Date",
        entity_variable=token_col_name,
        rolling_window_ma=ma_window,
    )

    return df


def plot_time_series(
    df: pd.DataFrame,
    file_name: str,
    boom_bust: list[dict] = BOOM_BUST,
    x_limit: list[str] = SAMPLE_PERIOD,
    token_col_name: str = "token",
    value_colume: str = "value",
    event_date_list: list[str] = [
        "2020-03-12",
    ],
) -> None:
    """
    plot the time series
    """
    df["time"] = df["Date"].apply(md.date2num)

    # plot boom bust cycles
    for cycle in boom_bust:
        plt.axvspan(
            cycle["start"],
            cycle["end"],
            alpha=0.1,
            color="red" if cycle["main_trend"] == "bust" else "green",
        )

    for event_date in event_date_list:
        # Compound attack of 2020
        # Introduction of Uniswap V3
        # Luna crash
        # FTX collapse
        plt.axvline(x=pd.to_datetime(event_date), color="red", linewidth=2, alpha=0.5)

    # plot the time series
    for token in set(df[token_col_name]):
        token_df = df[df[token_col_name] == token]
        # plot with color and line style according to ALL_TOKEN_DICT
        plt.plot(
            token_df["time"],
            token_df[value_colume],
            color=ALL_TOKEN_DICT[token]["color"],
            linestyle=ALL_TOKEN_DICT[token]["line_type"],
            label=token,
        )

    # set x limit
    plt.xlim(md.date2num(x_limit))

    # convert time to date
    date_format = md.DateFormatter("%Y-%m-%d")
    plt.gca().xaxis.set_major_formatter(date_format)

    # rotate x axis label by 45 degree
    plt.xticks(rotation=45)

    # move legend to outside the plot, upper left
    plt.legend(bbox_to_anchor=(1.01, 1), loc="upper left")

    # save the plot to the figure path
    plt.savefig(FIGURE_PATH / f"{file_name}.pdf", bbox_inches="tight")

    plt.show()

    # close the plot
    plt.close()


def plot_ma_time_series(
    file_folder: str,
    ma_window: int = 30,
    value_colume: str = "value",
    token_col_name: str = "token",
    boom_bust: list[dict] = BOOM_BUST,
    x_limit: list[str] = SAMPLE_PERIOD,
    file_name: str = "volume_ma",
    event_date_list: list[str] = ["2020-03-12"],
) -> None:
    df = file_to_df(file_folder)
    df_prepared = preprocess_ma(
        df,
        value_colume=value_colume,
        token_col_name=token_col_name,
        ma_window=ma_window,
    )
    plot_time_series(
        df_prepared,
        file_name=file_name,
        value_colume=name_ma_variable(value_colume, ma_window),
        token_col_name=token_col_name,
        boom_bust=boom_bust,
        x_limit=x_limit,
        event_date_list=event_date_list,
    )


def plot_ma_time_series_panel(
    panel_path: str,
    ma_window: int = 30,
    value_colume: str = "value",
    token_col_name: str = "token",
    boom_bust: list[dict] = BOOM_BUST,
    x_limit: list[str] = SAMPLE_PERIOD,
    file_name: str = "volume_ma",
    event_date_list: list[str] = ["2020-03-12"],
) -> None:
    df = pd.read_pickle(panel_path)
    df.reset_index(inplace=True)
    df_prepared = preprocess_ma(
        df,
        value_colume=value_colume,
        token_col_name=token_col_name,
        ma_window=ma_window,
    )
    plot_time_series(
        df_prepared,
        file_name=file_name,
        value_colume=name_ma_variable(value_colume, ma_window),
        token_col_name=token_col_name,
        boom_bust=boom_bust,
        x_limit=x_limit,
        event_date_list=event_date_list,
    )


if __name__ == "__main__":
    # df = file_to_df()
    # df_prepared = preprocess_ma(
    #     df, value_colume="Volume", token_col_name="Token", ma_window=1
    # )
    # plot_time_series(
    #     df_prepared,
    #     file_name="volume_ma",
    #     value_colume=name_ma_variable("Volume", 1),
    #     token_col_name="Token",
    #     event_date_list=EVENT_DATE_LIST,
    # )

    # plot_ma_time_series(
    #     file_folder=NETWORK_DATA_PATH / "merged" / "volume_share",
    #     ma_window=30,
    #     value_colume="Volume",
    #     token_col_name="Token",
    #     boom_bust=BOOM_BUST,
    #     x_limit=SAMPLE_PERIOD,
    #     file_name="volume_ma",
    #     event_date_list=EVENT_DATE_LIST,
    # )
    plot_ma_time_series_panel(
        panel_path=str(DATA_PATH / "reg_panel_merged.pkl"),
        ma_window=30,
        value_colume="vol_undirected_full_len_share",
        token_col_name="Token",
        boom_bust=BOOM_BUST,
        x_limit=SAMPLE_PERIOD,
        file_name="vol_undirected_full_len_share",
        event_date_list=EVENT_DATE_LIST,
    )
