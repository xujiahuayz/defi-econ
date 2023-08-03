"""
Functions to help with asset pricing
"""

import warnings

import pandas as pd
import scipy.stats as stats

# import statsmodels.api as sm

from environ.process.market.risk_free_rate import df_rf
from environ.utils.variable_constructer import lag_variable_columns, name_lag_variable

warnings.filterwarnings("ignore")

REFERENCE_DOM = "betweenness_centrality_count"


def calculate_period_return(
    df_panel: pd.DataFrame,
    freq: int,
    date_col: str = "Date",
    daily_supply_rate_col: str = "daily_supply_return",
) -> pd.DataFrame:
    """
    Function to calculate the period return, where the period length is specified by freq
    """

    df_panel["timestamp"] = df_panel[date_col].apply(lambda x: int(x.timestamp()))
    df_panel.sort_values(by=["Token", "Date"], ascending=True, inplace=True)

    # caculate rolling freq-day sum of supply rates for each token
    df_panel["cum_supply_rates"] = (
        df_panel.groupby("Token")[daily_supply_rate_col]
        .rolling(freq)
        .sum()
        .reset_index(0)[daily_supply_rate_col]
    )

    df_panel = df_panel[
        ((df_panel["timestamp"] - df_panel["timestamp"].min()) % (freq * 24 * 60 * 60))
        == 0
    ]

    # calculate simple dollar return
    df_panel["dollar_ret"] = df_panel.groupby("Token")[
        "dollar_exchange_rate"
    ].pct_change()

    # calculate only the convenience yield
    df_panel["ret"] = (
        (1 + df_panel["cum_supply_rates"]) * (df_panel["dollar_ret"] + 1)
        - 1
        - df_panel["dollar_ret"]
    )

    return df_panel


def _sort_zero_value_port(
    df_panel_period: pd.DataFrame, risk_factor: str
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Function to isolate zero-value dominance portfolio
    """

    df_zero_dom = df_panel_period[
        df_panel_period[name_lag_variable(risk_factor)] == 0
    ].copy()
    df_panel_period = df_panel_period[
        df_panel_period[name_lag_variable(risk_factor)] != 0
    ].copy()

    # if the length of df_zero_dom is 0, using the REFERENCE_DOM as a reference
    if len(df_zero_dom) == 0:
        n_treashold_zero = df_panel_period.loc[
            df_panel_period[name_lag_variable(REFERENCE_DOM)] == 0
        ].shape[0]
        df_zero_dom = df_panel_period.iloc[:n_treashold_zero].copy()
        df_panel_period = df_panel_period.iloc[n_treashold_zero:].copy()

    df_zero_dom["portfolio"] = "P1"

    return df_panel_period, df_zero_dom


def _sorting(
    df_panel_period: pd.DataFrame,
    risk_factor: str,
    zero_value_portfolio: bool,
    ret_dict: dict,
    brk_pt_lst: list[float],
) -> dict:
    """
    Function to implement the asset pricing for one period
    """

    df_panel_period = df_panel_period.sort_values(
        by=name_lag_variable(risk_factor), ascending=True
    ).reset_index(drop=True)

    if zero_value_portfolio:
        df_panel_period, df_zero_dom = _sort_zero_value_port(
            df_panel_period=df_panel_period, risk_factor=risk_factor
        )

        ret_dict = _mcap_weight(
            df_portfolio=df_zero_dom,
            ret_dict=ret_dict,
            port_idx=1,
        )

    brk_pt_lst = [0] + brk_pt_lst + [1]

    # portfolio construction
    for port in range(len(brk_pt_lst) - 1):
        df_portfolio_period = df_panel_period.iloc[
            int(len(df_panel_period) * brk_pt_lst[port]) : int(
                len(df_panel_period) * brk_pt_lst[port + 1]
            )
        ].copy()

        ret_dict = _mcap_weight(
            df_portfolio=df_portfolio_period,
            ret_dict=ret_dict,
            port_idx=port + 2 if zero_value_portfolio else port + 1,
        )

    return ret_dict


def _mcap_weight(df_portfolio: pd.DataFrame, ret_dict: dict, port_idx: int) -> dict:
    """
    Function to calculate the market cap weight
    """

    # calculate the market cap weight
    df_portfolio["weight"] = df_portfolio["mcap"] / df_portfolio["mcap"].sum()
    ret_dict[f"P{port_idx}"].append(
        (df_portfolio["weight"] * df_portfolio["ret"]).sum()
    )

    return ret_dict


def _eval_port(
    df_ret: pd.DataFrame,
    freq: int,
    n_port: int,
) -> pd.DataFrame:
    """
    Function to evaluate the portfolio
    """

    df_ret.sort_values(by="Date", ascending=True, inplace=True)
    df_ret["Date"] = pd.to_datetime(df_ret["Date"])

    # annualize return
    for portfolio in [f"P{port}" for port in range(1, n_port + 1)]:
        df_ret[portfolio] = df_ret[portfolio] * 365.2425 / freq

    # calculate the bottom minus top
    df_ret[f"P{n_port} - P1"] = df_ret[f"P{n_port}"] - df_ret["P1"]

    portfolio_col = [f"P{port}" for port in range(1, n_port + 1)] + [f"P{n_port} - P1"]

    # a new dataframe to store the averag return for each portfolio
    df_ret_avg = pd.DataFrame(
        {
            "Portfolios": portfolio_col,
            "Mean": df_ret[portfolio_col].mean().to_list(),
            "t-stat of mean": df_ret[portfolio_col]
            .apply(lambda x: stats.ttest_1samp(x, 0)[0])
            .to_list(),
            "p-value of mean": df_ret[portfolio_col]
            .apply(lambda x: stats.ttest_1samp(x, 0)[1])
            .to_list(),
            "Stdev": df_ret[portfolio_col].std().to_list(),
            "Sharpe": (
                df_ret[portfolio_col].mean() / df_ret[portfolio_col].std()
            ).to_list(),
        }
    )

    return df_ret_avg


def asset_pricing(
    reg_panel: pd.DataFrame,
    brk_pt_lst: list[float],
    dominance_var: str = "volume_ultimate_share",
    freq: int = 14,
    zero_value_portfolio: bool = True,
) -> pd.DataFrame:
    """
    Aggregate function to create portfolios
    """

    n_port = len(brk_pt_lst) + 2 if zero_value_portfolio else len(brk_pt_lst) + 1
    df_panel = calculate_period_return(df_panel=reg_panel, freq=freq)

    # prepare the dataframe to store the portfolio
    date_list = list(df_panel["Date"].unique())
    date_list.remove(df_panel["Date"].min())

    # dict to store the freq and portfolio return
    ret_dict = {f"P{port}": [] for port in range(1, n_port + 1)}
    ret_dict["Date"] = []

    df_panel = lag_variable_columns(
        data=df_panel,
        variable=[dominance_var, REFERENCE_DOM],
        time_variable="Date",
        entity_variable="Token",
    )

    # loop through the date
    for period in date_list:
        # asset pricing
        df_panel_period = df_panel[df_panel["Date"] == period].copy()
        ret_dict = _sorting(
            df_panel_period=df_panel_period,
            risk_factor=dominance_var,
            zero_value_portfolio=zero_value_portfolio,
            ret_dict=ret_dict,
            brk_pt_lst=brk_pt_lst,
        )
        ret_dict["Date"].append(period)

    # evaluate the performance of the portfolio
    return _eval_port(pd.DataFrame(ret_dict), freq, n_port)
