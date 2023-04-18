"""
Process the dollar exchange rate.
"""

from pathlib import Path

import numpy as np
import pandas as pd

from environ.constants import GLOBAL_DATA_PATH

# read the data
dollar_df = pd.read_csv(
    Path(GLOBAL_DATA_PATH) / "token_market" / "primary_token_price_2.csv",
    index_col=0,
    header=0,
)

# convert the date to datetime
dollar_df["Date"] = pd.to_datetime(
    dollar_df["Date"], format="%Y-%m-%d"
) + pd.DateOffset(days=-1)

# sort the time series
dollar_df = dollar_df.sort_values(by="Date", ascending=True).set_index("Date")

# convert the dataframe to panel
dollar_df = (
    dollar_df.stack()
    .reset_index()
    .rename(columns={"level_1": "Token", 0: "dollar_exchange_rate"})
)

# remove inf and -inf
dollar_df = dollar_df.replace([np.inf, -np.inf], np.nan).dropna()
