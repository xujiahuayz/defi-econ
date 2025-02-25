"""
Functions for Fama Macbeth regression
"""

import pandas as pd
import scipy.stats as stats
import statsmodels.formula.api as sm
# import statsmodels.api as sm

# from environ.process.market.risk_free_rate import df_rf
from environ.utils.variable_constructer import lag_variable_columns, name_lag_variable
from environ.process.asset_pricing.double_sorting import calculate_period_return, _sorting
REFERENCE_DOM = "betweenness_centrality_count"

def build_dominance_factor(
    reg_panel: pd.DataFrame,
    brk_pt_lst: list[float],
    dominance_var: str = "volume_ultimate_share",
    zero_value_portfolio: bool = True,
    simple_dollar_ret: bool = False,
) -> pd.DataFrame:
    """
    Aggregate function to create portfolios by week of the year
    """

    n_port = len(brk_pt_lst) + 2 if zero_value_portfolio else len(brk_pt_lst) + 1
    df_panel = calculate_period_return(
        df_panel=reg_panel, freq=7, simple_dollar_ret=simple_dollar_ret
    )

    # Add columns for the week and year
    df_panel['Week'] = df_panel['Date'].dt.isocalendar().week
    df_panel['Year'] = df_panel['Date'].dt.isocalendar().year

    # Prepare the dataframe to store the portfolio
    week_year_list = df_panel[['Year', 'Week']].drop_duplicates().sort_values(by=['Year', 'Week']).values.tolist()

    # Dict to store the weekly portfolio return
    ret_dict = {f"P{port}": [] for port in range(1, n_port + 1)}
    ret_dict["Year"] = []
    ret_dict["Week"] = []

    df_panel = lag_variable_columns(
        data=df_panel,
        variable=[dominance_var, REFERENCE_DOM],
        time_variable="Date",
        entity_variable="Token",
    )

    # Loop through the weeks
    for year, week in week_year_list:
        # Asset pricing
        df_panel_week = df_panel[(df_panel['Year'] == year) & (df_panel['Week'] == week)].copy()
        ret_dict = _sorting(
            df_panel_period=df_panel_week,
            risk_factor=dominance_var,
            zero_value_portfolio=zero_value_portfolio,
            ret_dict=ret_dict,
            brk_pt_lst=brk_pt_lst,
        )
        ret_dict["Year"].append(year)
        ret_dict["Week"].append(week)

    df_ret = pd.DataFrame(ret_dict)
    df_ret.sort_values(by=["Year", "Week"], ascending=True, inplace=True)

    # Calculate the bottom minus top
    df_ret[f"P{n_port} - P1"] = df_ret[f"P{n_port}"] - df_ret["P1"]

    return df_ret


def calculate_weekly_returns(df_panel: pd.DataFrame,
) -> pd.DataFrame:
    weekly = df_panel.groupby(['Token', 'Year', 'Week']).agg(
        weekly_dollar_ret=('dollar_ret', lambda x: (1 + x).prod() - 1),
        weekly_ret=('ret', lambda x: (1 + x).prod() - 1)
    ).reset_index()
    return weekly