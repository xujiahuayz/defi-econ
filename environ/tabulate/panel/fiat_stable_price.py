"""
merge fiat price dataframe with reg_panel
"""

import pandas as pd
from environ.process.market.fiat_price import process_fiat_price
from environ.constants import STABLE_DICT, FIAT_LIST


def price_underlying(
    token_df: pd.DataFrame, new_price_col_name: str = "exchange_to_underlying"
) -> pd.DataFrame:
    """
    merge fiat price dataframe with reg_panel
    """
    token_df[new_price_col_name] = token_df["dollar_exchange_rate"]

    if token_df["Stable"].iloc[0] == 1:
        # stablecoin
        # get the underlying fiat
        underlying = STABLE_DICT[token_df["Token"].iloc[0]]["underlying"]
        if underlying != "USD":
            # calculate exchange rate
            token_df[new_price_col_name] = (
                token_df["dollar_exchange_rate"] / token_df[underlying]
            )
    return token_df


def _merge_fiat_underlying(
    reg_panel: pd.DataFrame, new_price_col_name: str = "exchange_to_underlying"
) -> pd.DataFrame:
    """
    merge fiat price dataframe with reg_panel
    """
    for fiat in FIAT_LIST:
        if fiat != "USD":
            fiat_price_df = process_fiat_price(fiat)
            reg_panel = reg_panel.merge(fiat_price_df, on="Date", how="outer")
    # process each token
    reg_panel = reg_panel.groupby("Token").apply(
        lambda x: price_underlying(x, new_price_col_name=new_price_col_name)
    )
    return reg_panel


if __name__ == "__main__":
    # create some dummy data to test the functions above
    import numpy as np

    reg_panel = pd.DataFrame(
        {
            "Token": ["DAI", "EURS", "XYZ"] * 5,
            "Date": pd.date_range("2020-01-01", "2020-01-05").repeat(3),
            "dollar_exchange_rate": np.random.uniform(0.9, 1.1, 15),
            "Stable": [1, 1, 0] * 5,
        }
    )
    print(_merge_fiat_underlying(reg_panel))
