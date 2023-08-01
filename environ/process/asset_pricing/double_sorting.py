"""
Functions to help with asset pricing
"""

import datetime
import warnings

import numpy as np
import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm
from tqdm import tqdm

from environ.process.market.risk_free_rate import df_rf
from environ.utils.variable_constructer import lag_variable_columns, name_lag_variable

warnings.filterwarnings("ignore")

FONT_SIZE = 25
REFERENCE_DOM = "betweenness_centrality_count"


def _ret_cal(
    df_panel: pd.DataFrame,
    freq: int,
) -> pd.DataFrame:
    """
    Function to calculate the APY return
    """

    # convert annalized supply rates to daily supply rates
    df_panel["supply_rates"] = df_panel["supply_rates"] / 365
    df_panel.sort_values(by=["Token", "Date"], ascending=True, inplace=True)

    # calculate the compound APY
    for token in tqdm(df_panel["Token"].unique()):
        df_token = df_panel[df_panel["Token"] == token].copy()
        date_list = df_token[df_token["freq"]]["Date"].tolist()

        for date in date_list:
            df_date = df_token[
                (df_token["Date"] <= date)
                & (df_token["Date"] > date - datetime.timedelta(days=freq))
            ].copy()

            cum_apy = (df_date["supply_rates"] + 1).prod() - 1

            df_panel.loc[
                (df_panel["Token"] == token) & (df_panel["Date"] == date), "cum_apy"
            ] = cum_apy

    # data frequent conversion and sorting
    df_panel = df_panel[df_panel["freq"]]
    df_panel.sort_values(by=["Token", "Date"], ascending=True, inplace=True)

    # calculate simple dollar return
    df_panel["dollar_ret"] = df_panel.groupby("Token")[
        "dollar_exchange_rate"
    ].pct_change()
    df_panel["mret"] = df_panel.groupby("Token")["S&P"].pct_change()

    # calculate the DPY plus dollar return
    df_panel["ret"] = (1 + df_panel["cum_apy"]) * (df_panel["dollar_ret"] + 1) - 1

    return df_panel


def _freq_conversion(
    df_panel: pd.DataFrame,
    freq: int,
    date_col: str = "Date",
) -> pd.DataFrame:
    """
    Function to convert the frequency of a series from daily to a given frequency
    """

    df_panel["timestamp"] = df_panel[date_col].apply(lambda x: int(x.timestamp()))

    # create a freq column where True if the timestamp is a multiple of freq
    df_panel["freq"] = (
        (df_panel["timestamp"] - df_panel["timestamp"].min()) % (freq * 24 * 60 * 60)
    ) == 0

    return df_panel


def _asset_pricing_preprocess(
    df_panel: pd.DataFrame,
    dominance_var: str,
    freq: int,
) -> pd.DataFrame:
    """
    Function to preprocess the dataframe
    """

    df_panel = _freq_conversion(df_panel, freq=freq)
    df_panel = _ret_cal(df_panel, freq=freq)
    df_panel = lag_variable_columns(
        data=df_panel,
        variable=[dominance_var, REFERENCE_DOM],
        time_variable="Date",
        entity_variable="Token",
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
    )

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

    df_ret.sort_values(by="freq", ascending=True, inplace=True)
    df_ret["freq"] = pd.to_datetime(df_ret["freq"])

    # include the risk free rate
    df_rf_ap = df_rf.copy()
    df_rf_ap.rename(columns={"Date": "freq"}, inplace=True)
    df_rf_ap["RF"] = (1 + df_rf_ap["RF"]) ** freq - 1
    df_ret["RF"] = df_rf_ap.loc[
        df_rf_ap["freq"] == df_ret["freq"].values[0], "RF"
    ].values[0]

    # calculate the excess return
    for portfolio in [f"P{port}" for port in range(1, n_port + 1)]:
        df_ret[portfolio] = np.log(df_ret[portfolio] + 1) - np.log(df_ret["RF"] + 1)

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
            "Alpha": df_ret[portfolio_col]
            .apply(
                lambda x: sm.OLS(
                    x, np.log(df_ret["mret"] + 1) - np.log(df_ret["RF"] + 1)
                )
                .fit()
                .params[0]
            )
            .to_list(),
            "t-stat of alpha": df_ret[portfolio_col]
            .apply(
                lambda x: sm.OLS(
                    x, np.log(df_ret["mret"] + 1) - np.log(df_ret["RF"] + 1)
                )
                .fit()
                .tvalues[0]
            )
            .to_list(),
        }
    )

    return df_ret_avg


def asset_pricing(
    reg_panel: pd.DataFrame,
    brk_pt_lst: list[float],
    dom_var: str = "volume_ultimate_share",
    freq: int = 14,
    zero_value_portfolio: bool = True,
) -> pd.DataFrame:
    """
    Aggregate function to create portfolios
    """

    n_port = len(brk_pt_lst) + 2 if zero_value_portfolio else len(brk_pt_lst) + 1
    df_panel = _asset_pricing_preprocess(reg_panel, dom_var, freq)

    # prepare the dataframe to store the portfolio
    df_panel = df_panel.sort_values(by=["Date"], ascending=True)
    date_list = list(df_panel["Date"].unique())
    date_list.remove(df_panel["Date"].min())

    # dict to store the freq and portfolio return
    ret_dict = {f"P{port}": [] for port in range(1, n_port + 1)}
    ret_dict["freq"] = []
    ret_dict["mret"] = []

    # loop through the date
    for period in date_list:
        # asset pricing
        df_panel_period = df_panel[df_panel["Date"] == period].copy()
        ret_dict = _sorting(
            df_panel_period=df_panel_period,
            risk_factor=dom_var,
            zero_value_portfolio=zero_value_portfolio,
            ret_dict=ret_dict,
            brk_pt_lst=brk_pt_lst,
        )
        ret_dict["freq"].append(period)
        ret_dict["mret"].append(df_panel_period["mret"].mean())

    # evaluate the performance of the portfolio
    return _eval_port(pd.DataFrame(ret_dict), freq, n_port)
