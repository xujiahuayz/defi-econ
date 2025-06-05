import pandas as pd
import numpy as np
from scipy.stats import skew, kurtosis
from environ.process.asset_pricing.double_sorting import calculate_period_return
from environ.constants import (
    DEPENDENT_VARIABLES,
    DEPENDENT_VARIABLES_ASSETPRICING,
    PROCESSED_DATA_PATH,
    TABLE_PATH,
)

# load the regression panel dataset
reg_panel = pd.read_pickle(
    PROCESSED_DATA_PATH / "panel_main.pickle.zip", compression="zip"
)
# add supply rates
reg_panel["daily_supply_return"] = reg_panel["supply_rates"] / 365.2425
# add daily returns
df_panel = calculate_period_return(df_panel=reg_panel, freq=1, simple_dollar_ret=True)

# winsorize returns
df_panel["ret"] = df_panel.groupby(["Date"])["ret"].transform(
    lambda x: x.clip(lower=x.quantile(0.01), upper=x.quantile(0.99))
)

# Add columns for the week and year
df_panel["Week"] = df_panel["Date"].dt.isocalendar().week.replace(53, 52)
df_panel["Year"] = df_panel["Date"].dt.isocalendar().year
df_panel["WeekYear"] = df_panel["Year"].astype(str) + "-" + df_panel["Week"].astype(str)

panelA = df_panel.groupby("Year", as_index=False).agg(
    Number_of_Tokens=("Token", "nunique"),
    MarketCap_Mean=("mcap", "mean"),
    MarketCap_Median=("mcap", "median"),
    Volume_Mean=("Volume", "mean"),
    Volume_Median=("Volume", "median"),
    GasPrice_Mean=("gas_price_usd", "mean"),
    GasPrice_Median=("gas_price_usd", "median"),
)

# Add an overall row labeled "Full"
full_row = pd.DataFrame(
    {
        "Year": ["Full"],
        "Number_of_Tokens": [df_panel["Token"].nunique()],
        "MarketCap_Mean": [df_panel["mcap"].mean()],
        "MarketCap_Median": [df_panel["mcap"].median()],
        "Volume_Mean": [df_panel["Volume"].mean()],
        "Volume_Median": [df_panel["Volume"].median()],
        "GasPrice_Mean": [df_panel["gas_price_usd"].mean()],
        "GasPrice_Median": [df_panel["gas_price_usd"].median()],
    }
)
panelA = pd.concat([panelA, full_row], ignore_index=True)

# To replicate a multi-level header for "Market Cap" and "Volume":
panelA.columns = pd.MultiIndex.from_tuples(
    [
        ("", "Year"),
        ("", "Number of Tokens"),
        ("Market Cap", "Mean"),
        ("Market Cap", "Median"),
        ("Volume", "Mean"),
        ("Volume", "Median"),
        ("GasPrice", "Mean"),
        ("GasPrice", "Median"),
    ]
)

# Convert to LaTeX
latex_panelA = panelA.to_latex(
    index=False,
    multirow=True,
    multicolumn=True,
    float_format="%.2f",
    caption="Panel A: Summary Statistics by Year",
    label="tab:panelA",
)
print(latex_panelA)
