"""
Functions for Fama Macbeth regression
"""

import numpy as np
import pandas as pd
import scipy.stats as stats
import statsmodels.formula.api as smf
import statsmodels.api as sm
from scipy.stats import ttest_1samp

# from environ.process.market.risk_free_rate import df_rf
from environ.utils.variable_constructer import lag_variable_columns, name_lag_variable
from environ.process.asset_pricing.double_sorting import (
    calculate_period_return,
    _sorting,
)
from environ.constants import (
    DEPENDENT_VARIABLES,
    PROCESSED_DATA_PATH,
    STABLE_DICT,
    TABLE_PATH,
)

REFERENCE_DOM = "betweenness_centrality_count"


def reg_fama_macbeth(
    data_fama_macbeth, formula: str = "dollar_ret ~ DOM"
) -> pd.DataFrame:
    risk_premia = (
        data_fama_macbeth.groupby(["WeekYear"])
        .apply(lambda x: smf.ols(formula=formula, data=x).fit().params)
        .reset_index()
    )

    price_of_risk = (
        risk_premia.melt(id_vars=["WeekYear"], var_name="factor", value_name="estimate")
        .groupby("factor")["estimate"]
        .apply(
            lambda x: pd.Series(
                {
                    "risk_premium": x.mean(),
                    "t_stat": x.mean() / x.std() * np.sqrt(len(x)),
                }
            )
        )
        .reset_index()
        .pivot(index="factor", columns="level_1", values="estimate")
        .reset_index()
    )

    price_of_risk_NW = (
        risk_premia.melt(id_vars=["WeekYear"], var_name="factor", value_name="estimate")
        .groupby("factor")
        .apply(
            lambda x: (
                x["estimate"].mean()
                / smf.ols("estimate ~ 1", x)
                .fit(cov_type="HAC", cov_kwds={"maxlags": 4})
                .bse
            )
        )
        .reset_index()
        .rename(columns={"Intercept": "t_stat_NW"})
    )
    # express risk premium in percentage
    price_of_risk["risk_premium"] = price_of_risk["risk_premium"] * 100
    return price_of_risk.merge(price_of_risk_NW, on="factor").round(3)


def clean_weekly_panel(reg_panel, is_stablecoin=0, is_boom=-1):
    # add supply rates
    reg_panel["daily_supply_return"] = reg_panel["supply_rates"] / 365.2425
    # add daily returns
    df_panel = calculate_period_return(
        df_panel=reg_panel, freq=1, simple_dollar_ret=True
    )

    # winsorize returns
    df_panel["ret"] = df_panel.groupby(["Date"])["ret"].transform(
        lambda x: x.clip(lower=x.quantile(0.025), upper=x.quantile(0.975))
    )

    df_panel["amihud"] = np.where(
        df_panel["Volume"] == 0, np.nan, df_panel["ret"].abs() / df_panel["Volume"]
    )

    # Add columns for the week and year
    df_panel["Week"] = df_panel["Date"].dt.isocalendar().week.replace(53, 52)
    df_panel["Year"] = df_panel["Date"].dt.isocalendar().year
    df_panel["WeekYear"] = (
        df_panel["Year"].astype(str) + "-" + df_panel["Week"].astype(str)
    )

    agg_dict = {"ret": ("ret", lambda x: (1 + x).prod() - 1)}
    for col in DEPENDENT_VARIABLES + ["mcap", "amihud"]:
        agg_dict[col] = (col, "mean")

    df_panel = df_panel.groupby(["Token", "WeekYear"]).agg(**agg_dict).reset_index()

    # Ensure the DataFrame is sorted by Token and WeekYear
    df_panel = df_panel.sort_values(["Token", "WeekYear"])

    # Create the lead returns, i.e. returns one week ahead
    df_panel["ret_lead_1"] = df_panel.groupby("Token")["ret"].shift(-1)
    df_panel = df_panel.dropna(subset=["ret_lead_1"])

    # Data filtering needs to be done at the end, to prevent wrong shifting in returns
    if is_stablecoin == 1:
        reg_panel = reg_panel[reg_panel["stableshare"] > 0]
    elif is_stablecoin == 0:
        reg_panel = reg_panel[reg_panel["stableshare"] == 0]
    else:
        pass

    if is_boom == 1:
        reg_panel = reg_panel[reg_panel["is_boom"] == 1]
    elif is_boom == 0:
        reg_panel = reg_panel[reg_panel["is_boom"] == 0]
    else:
        pass

    # Filter out tokens without enough data
    # reg_panel = reg_panel[reg_panel['Token'].map(reg_panel['Token'].value_counts()) >= 50]

    ## Filter out tokens with low market capitalization
    df_panel = df_panel.groupby("Token").filter(
        lambda group: group["mcap"].max() >= 5e6
    )
    # df_panel = df_panel[df_panel["mcap"] > 1e6]

    return df_panel


def calculate_weekly_returns(
    df_panel: pd.DataFrame, other_variables=True
) -> pd.DataFrame:
    agg_dict = {
        "weekly_dollar_ret": ("dollar_ret", lambda x: (1 + x).prod() - 1),
        "weekly_ret": ("ret", lambda x: (1 + x).prod() - 1),
    }
    if other_variables:
        for col in DEPENDENT_VARIABLES + ["mcap"]:
            agg_dict[col] = (col, "mean")

    return df_panel.groupby(["Token", "Year", "Week"]).agg(**agg_dict).reset_index()


def get_weekly_panel(reg_panel, other_variables=False) -> pd.DataFrame:
    # add daily simple returns and convenience yield
    # reg_panel = calculate_period_return(df_panel=reg_panel, freq=1, simple_dollar_ret=False)

    # Change into weekly returns
    reg_panel = calculate_weekly_returns(
        df_panel=reg_panel, other_variables=other_variables
    )

    reg_panel["weekly_dollar_ret"] = reg_panel.groupby(["Year", "Week"])[
        "weekly_dollar_ret"
    ].transform(lambda x: x.clip(lower=x.quantile(0.01), upper=x.quantile(0.99)))
    return reg_panel


def create_portfolios(
    df_panel: pd.DataFrame,
    brk_pt_lst: list[float],
    dominance_var: str = "volume_ultimate_share",
    zero_value_portfolio: bool = True,
    simple_dollar_ret: bool = False,
) -> pd.DataFrame:
    """
    Aggregate function to create portfolios
    """

    n_port = len(brk_pt_lst) + 2 if zero_value_portfolio else len(brk_pt_lst) + 1

    # Prepare a list of week/year pairs sorted in time
    weekyear_list = (
        df_panel[["WeekYear"]].drop_duplicates().sort_values(by=["WeekYear"])
    )

    # dict to store portfolio return
    ret_dict = {f"P{port}": [] for port in range(1, n_port + 1)}
    ret_dict["WeekYear"] = []

    df_panel = lag_variable_columns(
        data=df_panel,
        variable=[dominance_var, REFERENCE_DOM],
        time_variable="WeekYear",
        entity_variable="Token",
    )

    # loop through the week and year
    for weekyear in weekyear_list:
        # Select data for the current week
        df_panel_period = df_panel[(df_panel["WeekYear"] == weekyear)].copy()
        ret_dict = _sorting(
            df_panel_period=df_panel_period,
            risk_factor=dominance_var,
            zero_value_portfolio=zero_value_portfolio,
            ret_dict=ret_dict,
            brk_pt_lst=brk_pt_lst,
        )
        ret_dict["WeekYear"].append(f"{weekyear}")

    return pd.DataFrame(ret_dict)


def assign_portfolio(x, quantiles, prefix="P", separate_zero_value=True):
    # Create an empty result Series with the same index as x.
    result = pd.Series(index=x.index, dtype=object)

    # combine zero values with bottom portfolio

    # Identify rows where the value is 0.
    zero_mask = x == 0
    if (zero_mask).sum() == 0:
        result = pd.qcut(
            x,
            q=quantiles,
            labels=[f"{prefix}{i}" for i in range(1, len(quantiles))],
        )
    else:
        if separate_zero_value:
            result[zero_mask] = f"{prefix}1"
            result[~zero_mask] = pd.qcut(
                x[~zero_mask],
                q=quantiles,
                labels=[f"{prefix}{i}" for i in range(2, len(quantiles) + 1)],
            )
        else:
            result[zero_mask] = f"{prefix}1"
            result[~zero_mask] = pd.qcut(
                x[~zero_mask],
                q=quantiles,
                labels=[f"{prefix}{i}" for i in range(1, len(quantiles))],
            )

    return result


def univariate_sort(
    df_panel, dom_variable, quantiles=[0, 0.3, 0.7, 1], separate_zero_value=True
) -> pd.DataFrame:
    # Assign portfolio for each WeekYear group.
    df_panel["portfolio"] = df_panel.groupby("WeekYear")[dom_variable].transform(
        lambda x: assign_portfolio(
            x, quantiles=quantiles, prefix="P", separate_zero_value=separate_zero_value
        )
    )
    return df_panel


def univariate_sort_table(df_panel, ret_agg="mean") -> pd.DataFrame:
    # First, compute the time-series of aggregated returns for each portfolio by WeekYear.
    # This calculates the mean (or median) for each portfolio in each time period.
    if ret_agg == "mean":
        portfolio_ts = (
            df_panel.groupby(["WeekYear", "portfolio"])["ret_lead_1"].mean().unstack()
        )
    else:
        portfolio_ts = (
            df_panel.groupby(["WeekYear", "portfolio"])["ret_lead_1"].median().unstack()
        )

    results = {}

    # Loop through each portfolio's time series and compute overall statistics across time.
    for port in portfolio_ts.columns:
        ret_ts = portfolio_ts[port].dropna()  # drop missing values if any
        mean_return = ret_ts.mean()
        std_return = ret_ts.std(ddof=1)
        t_stat, p_val = ttest_1samp(ret_ts, popmean=0)
        sharpe = (
            np.sqrt(365 / 7) * mean_return / std_return if std_return != 0 else np.nan
        )

        results[port] = {
            "Mean": mean_return,
            "t-Stat": t_stat,
            "StdDev": std_return,
            "Sharpe": sharpe,
        }

    # Determine the number of portfolios (assumes portfolios are labeled like P1, P2, ..., Pn)
    n_quantiles = portfolio_ts.shape[1]

    # Compute the spread portfolio as the time series difference: P{n_quantiles} - P1.
    # This means for each WeekYear, we subtract the mean of portfolio P1 from P{n_quantiles}.
    high_port = portfolio_ts[f"P{n_quantiles}"]
    low_port = portfolio_ts["P1"]
    spread_ts = high_port - low_port
    mean_diff = spread_ts.mean()
    std_diff = spread_ts.std(ddof=1)
    t_stat_diff, _ = ttest_1samp(spread_ts.dropna(), popmean=0)
    sharpe_diff = np.sqrt(365 / 7) * mean_diff / std_diff if std_diff != 0 else np.nan

    results[f"P{n_quantiles}-P1"] = {
        "Mean": mean_diff,
        "t-Stat": t_stat_diff,
        "StdDev": std_diff,
        "Sharpe": sharpe_diff,
    }

    summary_table = pd.DataFrame(results)
    return summary_table


def double_sort(
    df_panel,
    dom_variable,
    secondary_variable,
    quantiles=[0, 0.3, 0.7, 1],
    separate_zero_value=True,
) -> pd.DataFrame:
    # For the primary sort, assign portfolio labels with prefix "P".
    df_panel["primary_portfolio"] = df_panel.groupby("WeekYear")[
        dom_variable
    ].transform(
        lambda x: assign_portfolio(
            x, quantiles=quantiles, prefix="P", separate_zero_value=separate_zero_value
        )
    )

    # Within each primary portfolio, assign secondary portfolios with prefix "Q".
    df_panel["secondary_portfolio"] = df_panel.groupby(
        ["WeekYear", "primary_portfolio"]
    )[secondary_variable].transform(
        lambda x: assign_portfolio(
            x, quantiles=quantiles, prefix="Q", separate_zero_value=False
        )
    )
    return df_panel


def double_sort_table(df_panel, ret_agg="mean") -> pd.DataFrame:
    # Pivot the table to show average (or median) returns for each combination
    # of secondary and primary portfolios.
    mean_returns_table = df_panel.pivot_table(
        index="secondary_portfolio",
        columns="primary_portfolio",
        values="ret_lead_1",
        aggfunc="mean" if ret_agg == "mean" else "median",
    )
    return mean_returns_table


def vw_univariate_sort(
    df_panel, dom_variable, quantiles=[0, 0.3, 0.7, 1], ret_agg="mean"
) -> pd.DataFrame:
    df_panel["portfolio"] = df_panel.groupby("WeekYear")[dom_variable].transform(
        lambda x: pd.qcut(
            x, q=quantiles, labels=[f"P{i}" for i in range(1, len(quantiles) - 1)]
        )
    )

    weekly_weighted = (
        df_panel.groupby(["WeekYear", "portfolio"])
        .apply(lambda x: (x["ret"] * x["mcap"]).sum() / x["mcap"].sum())
        .reset_index(name="vw_ret")
    )

    # Step 2: Compute the average of these weekly weighted returns for each portfolio
    df_panel = weekly_weighted.groupby("portfolio")["vw_ret"].mean().reset_index()

    # Create a dictionary to store the results for each portfolio
    results = {}

    # Group by portfolio and compute statistics
    for port, group in df_panel.groupby("portfolio"):
        returns = group["vw_ret"]
        mean_return = returns.mean() if ret_agg == "mean" else returns.median()
        std_return = returns.std(ddof=1, skipna=True)  # Sample standard deviation
        # Compute t-statistic using ttest_1samp with population mean = 0
        t_stat, p_val = ttest_1samp(returns, popmean=0)

        # Save the results in the dictionary
        results[f"{port}"] = {
            "Mean": mean_return,
            "t-Stat": t_stat,
            # 'p-value': p_val,
            "StdDev": std_return,
            "Sharpe": np.sqrt(365 / 7) * mean_return / std_return,
        }

    # Create the summary table DataFrame with portfolio names as columns
    summary_table = pd.DataFrame(results)

    return summary_table


def get_dominance_portfolios(df_panel, ret_agg="mean") -> pd.DataFrame:
    if ret_agg == "mean":
        portfolio_ts = (
            df_panel.groupby(["WeekYear", "portfolio"])["ret_lead_1"].mean().unstack()
        )
    else:
        portfolio_ts = (
            df_panel.groupby(["WeekYear", "portfolio"])["ret_lead_1"].median().unstack()
        )

    # Compute the spread portfolio as the time series difference: P{n_quantiles} - P1.
    n_quantiles = portfolio_ts.shape[1]
    high_port = portfolio_ts[f"P{n_quantiles}"]
    low_port = portfolio_ts["P1"]
    spread_ts = high_port - low_port
    portfolio_ts[f"P{n_quantiles}-P1"] = spread_ts
    return portfolio_ts


def significance_stars(pval):
    """
    Return significance stars based on p-value:
        *** if p < 0.01
        **  if p < 0.05
        *   if p < 0.10
    """
    if pval < 0.01:
        return "***"
    elif pval < 0.05:
        return "**"
    elif pval < 0.1:
        return "*"
    else:
        return ""
