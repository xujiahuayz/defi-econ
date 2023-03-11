"""
construct fiat price dateframe
"""

from os import path

import pandas as pd
from environ.constants import GLOBAL_DATA_PATH

DATE_DF = pd.DataFrame(
    pd.date_range(start="2019-03-01", end="2023-01-31"),
    columns=["Date"],
)


def process_fiat_price(fiat: str) -> pd.DataFrame:
    """
    construct fiat price dataframe
    """
    # read fiat price csv from GLOBAL_DATA_PATH
    fiat_price_df = pd.read_csv(
        path.join(GLOBAL_DATA_PATH, f"{fiat}_price.csv"),
        index_col=None,
        parse_dates=["Date"],
    )[["Date", "Close"]]
    # merge fiat price with date_df
    fiat_price_df = DATE_DF.merge(fiat_price_df, on="Date", how="outer")
    # fill na with previous value
    fiat_price_df[fiat] = fiat_price_df["Close"].fillna(method="ffill")
    return fiat_price_df[["Date", fiat]]


if __name__ == "__main__":
    fiat = "SGD"
    fiat_price_df = process_fiat_price(fiat)
    print(fiat_price_df)
