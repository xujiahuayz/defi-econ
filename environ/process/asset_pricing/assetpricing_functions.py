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

    # Filter for stablecoins
    if is_stablecoin == 1:
        reg_panel = reg_panel[reg_panel["stableshare"] > 0]
    elif is_stablecoin == 0:
        reg_panel = reg_panel[reg_panel["stableshare"] == 0]
    else:
        pass

    ## Filter out tokens that existed for less than 2 months
    # reg_panel = reg_panel[
    #     reg_panel["Token"].map(reg_panel["Token"].value_counts()) >= 60
    # ]

    ## Filter out tokens with low peak market capitalization
    # reg_panel = reg_panel.groupby("Token").filter(
    #     lambda group: group["mcap"].max() >= 50e6
    # )

    # add supply rates
    reg_panel["daily_supply_return"] = reg_panel["supply_rates"] / 365.2425
    reg_panel.sort_values(by=["Token", "Date"], ascending=True, inplace=True)

    # calculate daily returns
    reg_panel["ret"] = reg_panel.groupby("Token")["dollar_exchange_rate"].pct_change(
        fill_method=None
    )
    # np.clip(     ,-0.5,1)

    # compute amihud illiquidity measure
    reg_panel["amihud"] = np.where(
        reg_panel["Volume"] == 0, np.nan, reg_panel["ret"].abs() / reg_panel["Volume"]
    )
    reg_panel["is_stablecoin"] = (
        reg_panel.groupby("Token")["stableshare"].transform("max") > 0
    ).astype(int)
    # winsorize returns
    # reg_panel["ret"] = reg_panel.groupby(["Date"])["ret"].transform(
    #     lambda x: x.clip(lower=x.quantile(0.025), upper=x.quantile(0.975))
    # )
    # Add columns for the week and year
    reg_panel["Week"] = reg_panel["Date"].dt.isocalendar().week.replace(53, 52)
    reg_panel["Year"] = reg_panel["Date"].dt.isocalendar().year
    reg_panel["WeekYear"] = (
        reg_panel["Year"].astype(str) + "-" + reg_panel["Week"].astype(str)
    )

    agg_dict = {
        "ret": ("ret", lambda x: (1 + x).prod() - 1),
        "volatility": ("ret", lambda x: np.std(x, ddof=1) * np.sqrt(365 / 7)),
        "mcap": ("mcap", "mean"),
        "mcap_share": ("mcap_share", "mean"),
        "amihud": ("amihud", "mean"),
        "is_boom": ("is_boom", "last"),
        "is_stablecoin": ("is_stablecoin", "last"),
        "gas_price_usd": ("gas_price_usd", "mean"),
        "stableshare": ("stableshare", "mean"),
        "gas_price_usd_log_return_vol_1_30": (
            "gas_price_usd_log_return_vol_1_30",
            "mean",
        ),
        "ether_price_usd_log_return_1": (
            "ether_price_usd_log_return_1",
            "mean",
        ),
        "ether_price_usd_log_return_vol_1_30": (
            "ether_price_usd_log_return_vol_1_30",
            "mean",
        ),
        "S&P_log_return_vol_1_30": ("S&P_log_return_vol_1_30", "mean"),
        "Supply_share": ("Supply_share", "mean"),
        "supply_rates": ("supply_rates", "mean"),
        "TVL": ("TVL", "mean"),
    }
    for col in DEPENDENT_VARIABLES:
        agg_dict[col] = (col, "mean")

    reg_panel = reg_panel.groupby(["Token", "WeekYear"]).agg(**agg_dict).reset_index()

    # Ensure the DataFrame is sorted by Token and WeekYear
    reg_panel = reg_panel.sort_values(["Token", "WeekYear"])

    # Compute rolling 4-week returns (including current week) for each token.
    # For a given week, ret_rolling_4 = (1 + ret[t-3])*(1 + ret[t-2])*(1 + ret[t-1])*(1 + ret[t]) - 1

    # Winsorize returns to limit extreme values
    reg_panel["ret"] = reg_panel.groupby(["WeekYear"])["ret"].transform(
        lambda x: x.clip(lower=x.quantile(0.01), upper=x.quantile(0.99))
    )
    # Create the lead returns, i.e. returns one week ahead
    reg_panel["ret_lead_1"] = reg_panel.groupby("Token")["ret"].shift(-1)

    reg_panel["ret_rolling_4"] = reg_panel.groupby("Token")["ret"].transform(
        lambda x: (1 + x).rolling(window=4, min_periods=1).apply(np.prod, raw=True) - 1
    )
    # Filter out tokens with low peak market capitalization
    # reg_panel = reg_panel.groupby("Token").filter(
    #     lambda group: group["mcap"].max() >= 100e6
    # )

    # remove observations with low market cap (not the token)
    # reg_panel = reg_panel[reg_panel["mcap"] > 1e6]

    ############################################################
    # Calculate the mean market cap for each token
    # mean_market_cap = reg_panel.groupby("Token")["mcap"].median()

    # # Identify tokens with an average market cap above 1 million
    # tokens_above_1m = mean_market_cap[mean_market_cap > 1e6].index

    # # Filter the original DataFrame to keep only these tokens
    # reg_panel = reg_panel[reg_panel["Token"].isin(tokens_above_1m)]
    ############################################################

    # Boom and bust filtering needs to be done at the end, to prevent wrong shifting in returns
    if is_boom == 1:
        reg_panel = reg_panel[reg_panel["is_boom"] == 1]
    elif is_boom == 0:
        reg_panel = reg_panel[reg_panel["is_boom"] == 0]
    else:
        pass
    return reg_panel


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


def assign_portfolio(x, quantiles, prefix="P", separate_zero_value=True):
    # Create an empty result Series with the same index as x.
    result = pd.Series(index=x.index, dtype=object)

    # combine zero values with bottom portfolio
    # Identify rows where the value is 0.
    zero_mask = x == 0
    if zero_mask.sum() == 0:
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
    df_panel, dom_variable, quantiles=[0, 0.33, 0.67, 1], separate_zero_value=True
) -> pd.DataFrame:
    # Assign portfolio for each WeekYear group.
    df_panel["portfolio"] = df_panel.groupby("WeekYear")[dom_variable].transform(
        lambda x: assign_portfolio(
            x, quantiles=quantiles, prefix="P", separate_zero_value=separate_zero_value
        )
    )
    return df_panel


def weighted_average_return(group):
    """
    Compute the value-weighted return for a group using the token market capitalization.
    The weighted return is defined as: sum(ret * mcap) / sum(mcap)
    """
    return np.average(group["ret_lead_1"], weights=group["mcap"])


def univariate_sort_table(
    df_panel, ret_agg="value_weight", annualized=False
) -> pd.DataFrame:
    """
    Compute the time-series of aggregated portfolio returns for each WeekYear.

    Parameters:
    - ret_agg: choose among "mean", "median", or "value_weight" (for value-weighted returns).
    - annualized: if True, annualize the average return.
    """
    if ret_agg == "mean":
        portfolio_ts = (
            df_panel.groupby(["WeekYear", "portfolio"])["ret_lead_1"].mean().unstack()
        )
    elif ret_agg == "median":
        portfolio_ts = (
            df_panel.groupby(["WeekYear", "portfolio"])["ret_lead_1"].median().unstack()
        )
    elif ret_agg == "value_weight":
        portfolio_ts = (
            df_panel.groupby(["WeekYear", "portfolio"])
            .apply(weighted_average_return)
            .unstack()
        )
    else:
        raise ValueError("ret_agg must be one of 'mean', 'median', or 'value_weight'")

    results = {}

    # Loop through each portfolio's time series and compute overall statistics across time.
    for port in portfolio_ts.columns:
        ret_ts = portfolio_ts[port].dropna()  # drop missing values if any
        mean_return = ret_ts.mean()
        std_return = ret_ts.std(ddof=1)
        t_stat, _ = ttest_1samp(ret_ts, popmean=0)
        sharpe = (
            np.sqrt(365 / 7) * mean_return / std_return if std_return != 0 else np.nan
        )

        results[port] = {
            "E[R]--Rf": mean_return * 52 if annualized else mean_return,
            "t": t_stat,
            "Std": std_return,
            "SR": sharpe,
        }

    # Determine the number of portfolios (assumes portfolios are labeled like P1, P2, ..., Pn)
    n_quantiles = portfolio_ts.shape[1]

    # Compute the spread portfolio as the time series difference: P{n_quantiles} - P1.
    high_port = portfolio_ts[f"P{n_quantiles}"]
    low_port = portfolio_ts["P1"]
    spread_ts = high_port - low_port
    mean_diff = spread_ts.mean()
    std_diff = spread_ts.std(ddof=1)
    t_stat_diff, _ = ttest_1samp(spread_ts.dropna(), popmean=0)
    sharpe_diff = np.sqrt(365 / 7) * mean_diff / std_diff if std_diff != 0 else np.nan

    results[f"P{n_quantiles}-P1"] = {
        "E[R]--Rf": mean_diff,
        "t": t_stat_diff,
        "Std": std_diff,
        "SR": sharpe_diff,
    }

    summary_table = pd.DataFrame(results)
    return summary_table


def double_sort(
    df_panel,
    dom_variable,
    secondary_variable,
    quantiles=[0, 0.33, 0.67, 1],
    secondary_quantiles=[0, 0.33, 0.67, 1],
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
            x, quantiles=secondary_quantiles, prefix="Q", separate_zero_value=False
        )
    )
    return df_panel


def double_sort_table(
    df_panel, ret_agg="value_weight", annualized=False
) -> pd.DataFrame:
    """
    Create a pivot table of portfolio returns for each combination of secondary and primary portfolios.
    If ret_agg is "value_weight", returns are computed as the value‐weighted average using "mcap".
    """
    if ret_agg == "value_weight":
        # Group by both secondary and primary portfolio and compute weighted average returns.
        mean_returns_table = (
            df_panel.groupby(["secondary_portfolio", "primary_portfolio"])
            .apply(weighted_average_return)
            .unstack()
        )
    else:
        agg_func = "mean" if ret_agg == "mean" else "median"
        mean_returns_table = df_panel.pivot_table(
            index="secondary_portfolio",
            columns="primary_portfolio",
            values="ret_lead_1",
            aggfunc=agg_func,
        )

    if annualized:
        mean_returns_table = mean_returns_table * 52

    return mean_returns_table


def independent_sort(
    df_panel,
    dom_variable,
    secondary_variable,
    quantiles=[0, 0.3, 0.7, 1],
    secondary_quantiles=[0, 0.3, 0.7, 1],
    separate_zero_value=True,
) -> pd.DataFrame:
    """
    Perform an independent double sort on df_panel.

    For each WeekYear:
      1) Sort on 'dom_variable' to create 'primary_portfolio'
      2) Sort (independently) on 'secondary_variable' to create 'secondary_portfolio'.

    Returns the df_panel with two new columns: 'primary_portfolio' and 'secondary_portfolio'.
    """

    # 1) Assign primary portfolios based on dom_variable for each WeekYear.
    df_panel["primary_portfolio"] = df_panel.groupby("WeekYear")[
        dom_variable
    ].transform(
        lambda x: assign_portfolio(
            x, quantiles=quantiles, prefix="P", separate_zero_value=separate_zero_value
        )
    )

    # 2) Independently assign secondary portfolios based on secondary_variable for each WeekYear.
    df_panel["secondary_portfolio"] = df_panel.groupby("WeekYear")[
        secondary_variable
    ].transform(
        lambda x: assign_portfolio(
            x,
            quantiles=secondary_quantiles,
            prefix="Q",
            separate_zero_value=separate_zero_value,
        )
    )

    return df_panel


def get_dominance_portfolios(df_panel, ret_agg="value_weight") -> pd.DataFrame:
    if ret_agg == "mean":
        portfolio_ts = (
            df_panel.groupby(["WeekYear", "portfolio"])["ret_lead_1"].mean().unstack()
        )
    elif ret_agg == "median":
        portfolio_ts = (
            df_panel.groupby(["WeekYear", "portfolio"])["ret_lead_1"].median().unstack()
        )
    elif ret_agg == "value_weight":
        portfolio_ts = (
            df_panel.groupby(["WeekYear", "portfolio"])
            .apply(weighted_average_return)
            .unstack()
        )
    else:
        raise ValueError("ret_agg must be one of 'mean', 'median', or 'value_weight'")

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
