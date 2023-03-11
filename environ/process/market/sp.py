"""
process s&p data
"""

from os import path
import pandas as pd
from environ.constants import GLOBAL_DATA_PATH


sp_df = pd.read_excel(
    path.join(
        GLOBAL_DATA_PATH,
        "token_market",
        "PerformanceGraphExport.xls",
    ),
    index_col=None,
    skiprows=6,
    skipfooter=4,
    # usecols="A:B:C",
)


# sort the dataframe by date
sp_df = sp_df.sort_values(by="Date", ascending=True)
