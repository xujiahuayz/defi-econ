"""
plot market with boom bust cycles
"""

from environ.process.spindex.sp import sp_df
from environ.utils.computations import boom_bust_periods


sp_df["time"] = sp_df["Date"]

# replace s&p colume with price
sp_df = sp_df.rename(columns={"S&P": "price"})

BOOM_BUST = boom_bust_periods(sp_df)
