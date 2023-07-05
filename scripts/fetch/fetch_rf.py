"""
Script to fetch the risk-free rate from the Fama French library
"""

import ssl

import pandas as pd

from environ.constants import DATA_PATH

FAMA_FRENCH_THREE_FACTORS_DAILY = (
    "https://mba.tuck.dartmouth.edu/pages/faculty/"
    + "ken.french/ftp/F-F_Research_Data_Factors_daily_CSV.zip"
)


# Create an SSL context that ignores SSL certificate verification
ssl._create_default_https_context = ssl._create_unverified_context


# read the data and ignore the first and last three rows
df_rf = pd.read_csv(
    FAMA_FRENCH_THREE_FACTORS_DAILY,
    skiprows=3,
    skipfooter=3,
    engine="python",
)

# rename the columns
df_rf.columns = ["Date", "Mkt-RF", "SMB", "HML", "RF"]

# only keep the date and the risk-free rate
df_rf = df_rf[["Date", "RF"]]

# convert the date to datetime
df_rf["Date"] = pd.to_datetime(df_rf["Date"], format="%Y%m%d")

# create a date range from the min to the max date
date_range = pd.date_range(df_rf["Date"].min(), df_rf["Date"].max())

# create a DataFrame with the date range
df_date_range = pd.DataFrame({"Date": date_range})

# merge the two DataFrames
df_rf = pd.merge(df_date_range, df_rf, on="Date", how="left")

# fill the missing values with the previous value
df_rf["RF"].fillna(method="ffill", inplace=True)

# save the DataFrame
df_rf.to_csv(DATA_PATH / "data_global/risk_free_rate/risk_free_rate.csv", index=False)
