"""
Get factors data: FF3, LTW3
"""
import ssl
import pandas as pd
from environ.constants import DATA_PATH, PROCESSED_DATA_PATH

# Fama-French 3 factors
FAMA_FRENCH_THREE_FACTORS_DAILY = (
    "https://mba.tuck.dartmouth.edu/pages/faculty/"
    + "ken.french/ftp/F-F_Research_Data_Factors_weekly_CSV.zip"
)

# Create an SSL context that ignores SSL certificate verification
ssl._create_default_https_context = ssl._create_unverified_context

# read the data and ignore the first and last three rows
df_ff3 = pd.read_csv(
    FAMA_FRENCH_THREE_FACTORS_DAILY,
    skiprows=3,
    skipfooter=3,
    engine="python",
)

# rename the columns
df_ff3.columns = ["Date", "Mkt-RF", "SMB", "HML", "RF"]
df_ff3.rename(columns={"Mkt-RF": "MKT"}, 
              inplace=True)
# convert the date to datetime
df_ff3["Date"] = pd.to_datetime(df_ff3["Date"], format="%Y%m%d")
df_ff3['Week'] = df_ff3['Date'].dt.isocalendar().week
df_ff3['Year'] = df_ff3['Date'].dt.isocalendar().year
df_ff3[["MKT", "SMB", "HML", "RF"]] = df_ff3[["MKT", "SMB", "HML", "RF"]] / 100
# save the DataFrame
df_ff3.to_csv(PROCESSED_DATA_PATH / "FF3.csv", index=False)

# LTW 3 factors
ltw3 = pd.read_excel(PROCESSED_DATA_PATH/'LTW3_original.xlsx',
    skiprows=5,
    engine="openpyxl",
    )
ltw3.rename(columns={'cmkt':'CMKT', 'csize':'CSIZE', 'cmom':'CMOM'}, inplace=True)
ltw3['yyww'] = ltw3['yyww'].astype(str)
ltw3['Year'] = ltw3['yyww'].str[:4].astype(int)
ltw3['Week'] = ltw3['yyww'].str[4:].astype(int) # 0x 2-digit number is converted into single digit x
ltw3.drop(['yyww'], axis=1, inplace=True)
ltw3.to_csv(PROCESSED_DATA_PATH/'LTW3.csv', index=False)