"""
process s&p data
"""

from os import path
import pandas as pd
from environ.settings import PROJECT_ROOT
from environ.utils.config_parser import Config

config = Config()


sp_df = pd.read_excel(
    path.join(
        PROJECT_ROOT,
        config["dev"]["config"]["data"]["GLOBAL_DATA_PATH"],
        "token_market",
        "PerformanceGraphExport.xls",
    ),
    index_col=None,
    skiprows=6,
    skipfooter=4,
    # usecols="A:B:C",
)

# # convert Effective date to datetime
# sp_df["Date"] = pd.to_datetime(sp_df["Date"])

# sort the dataframe by date
sp_df = sp_df.sort_values(by="Date", ascending=True)
