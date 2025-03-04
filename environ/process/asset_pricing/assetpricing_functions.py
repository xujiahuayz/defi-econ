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
from environ.process.asset_pricing.double_sorting import calculate_period_return, _sorting
from environ.constants import (
    DEPENDENT_VARIABLES,
    PROCESSED_DATA_PATH,
    STABLE_DICT,
    TABLE_PATH,
)
REFERENCE_DOM = "betweenness_centrality_count"

def reg_fama_macbeth(data_fama_macbeth, formula:str = "dollar_ret ~ DOM"
) -> pd.DataFrame:
  risk_premia = (data_fama_macbeth
    .groupby(["WeekYear"])
    .apply(lambda x: smf.ols(
        formula= formula, 
        data=x
      ).fit()
      .params
    )
    .reset_index()
  )

  price_of_risk = (risk_premia
    .melt(id_vars=["WeekYear"], var_name="factor", value_name="estimate")
    .groupby("factor")["estimate"]
    .apply(lambda x: pd.Series({
        "risk_premium": x.mean(),
        "t_stat": x.mean()/x.std()*np.sqrt(len(x))
      })
    )
    .reset_index()
    .pivot(index="factor", columns="level_1", values="estimate")
    .reset_index()
  )

  price_of_risk_NW = (risk_premia
    .melt(id_vars=["WeekYear"], var_name="factor", value_name="estimate")
    .groupby("factor")
    .apply(lambda x: (
        x["estimate"].mean()/ 
          smf.ols("estimate ~ 1", x)
          .fit(cov_type="HAC", cov_kwds={"maxlags": 4}).bse
      )
    )
    .reset_index()
    .rename(columns={"Intercept": "t_stat_NW"})
  )
  # express risk premium in percentage
  price_of_risk['risk_premium'] = price_of_risk['risk_premium'] * 100
  return price_of_risk.merge(price_of_risk_NW, on="factor").round(3)

def clean_weekly_panel(reg_panel, dom_variable, is_stablecoin= 0, is_boom=-1):

    if is_stablecoin == 1:
        reg_panel = reg_panel[reg_panel["stableshare"] > 0]
    elif is_stablecoin == 0:
        reg_panel = reg_panel[reg_panel["stableshare"] == 0]
    else:
        pass

    if is_boom == 1:
        reg_panel = reg_panel[reg_panel["is_boom"] ==1]
    elif is_boom == 0:
        reg_panel = reg_panel[reg_panel["is_boom"] ==0]
    else:   
        pass
        
    # reg_panel = reg_panel[reg_panel['Volume'] > 0]
    reg_panel = reg_panel[reg_panel[dom_variable] > 0]

    # Filter out tokens without enough data
    reg_panel = reg_panel[reg_panel['Token'].map(reg_panel['Token'].value_counts()) >= 120]

    # Filter out tokens with low market capitalization
    reg_panel = reg_panel.groupby('Token').filter(lambda group: group['mcap'].max() >= 5e6)

    # add supply rates
    reg_panel["daily_supply_return"] = reg_panel["supply_rates"] / 365.2425
    # add daily returns
    df_panel = calculate_period_return(
        df_panel=reg_panel, freq=1, simple_dollar_ret=True
    )
    # Add columns for the week and year
    df_panel['Week'] = df_panel['Date'].dt.isocalendar().week.replace(53, 52)
    df_panel['Year'] = df_panel['Date'].dt.isocalendar().year
    df_panel["WeekYear"] = df_panel["Year"].astype(str) + '-' + df_panel["Week"].astype(str)
    agg_dict = {
        'ret':('ret', lambda x: (1 + x).prod() - 1),
    }
    for col in DEPENDENT_VARIABLES+['mcap']:
        agg_dict[col] = (col, 'mean')

    df_panel = df_panel.groupby(['Token', 'WeekYear']).agg(**agg_dict).reset_index()

    # winsorize returns
    df_panel['ret'] = df_panel.groupby(['WeekYear'])['ret'].transform(
            lambda x: x.clip(lower=x.quantile(0.05), upper=x.quantile(0.95))
    )

    return df_panel


def calculate_weekly_returns(df_panel: pd.DataFrame, other_variables = True
) -> pd.DataFrame:
    agg_dict = {
        'weekly_dollar_ret':('dollar_ret', lambda x: (1 + x).prod() - 1),
    'weekly_ret':('ret', lambda x: (1 + x).prod() - 1),
    }
    if other_variables:
        for col in DEPENDENT_VARIABLES+['mcap']:
            agg_dict[col] = (col, 'mean')

    return df_panel.groupby(['Token', 'Year', 'Week']).agg(**agg_dict).reset_index()
    

def get_weekly_panel(reg_panel, other_variables = False):
    # add daily simple returns and convenience yield
    # reg_panel = calculate_period_return(df_panel=reg_panel, freq=1, simple_dollar_ret=False)

    # Change into weekly returns
    reg_panel = calculate_weekly_returns(df_panel=reg_panel, other_variables=other_variables)

    reg_panel['weekly_dollar_ret'] = reg_panel.groupby(['Year', 'Week'])['weekly_dollar_ret'].transform(
            lambda x: x.clip(lower=x.quantile(0.01), upper=x.quantile(0.99))
    )
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
    weekyear_list = df_panel[['WeekYear']].drop_duplicates().sort_values(by=['WeekYear'])

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
        df_panel_period = df_panel[
            (df_panel["WeekYear"] == weekyear)
        ].copy()
        ret_dict = _sorting(
            df_panel_period=df_panel_period,
            risk_factor=dominance_var,
            zero_value_portfolio=zero_value_portfolio,
            ret_dict=ret_dict,
            brk_pt_lst=brk_pt_lst,
        )
        ret_dict["WeekYear"].append(f"{weekyear}")

    return pd.DataFrame(ret_dict)


def univariate_sort(df_panel,dom_variable, n_quantiles=3, ret_agg = 'mean'):
    df_panel['portfolio'] = df_panel.groupby('WeekYear')[dom_variable].transform(
        lambda x: pd.qcut(x, q=n_quantiles, labels=[f'P{i}' for i in range(1, n_quantiles+1)])
    )

    # Create a dictionary to store the results for each portfolio
    results = {}

    # Group by portfolio and compute statistics
    for port, group in df_panel.groupby('portfolio'):
        returns = group['ret'] 
        mean_return = returns.mean() if ret_agg == 'mean' else returns.median()
        std_return = returns.std(ddof=1)  # Sample standard deviation
        # Compute t-statistic using ttest_1samp with population mean = 0
        t_stat, p_val = ttest_1samp(returns, popmean=0)
        
        # Save the results in the dictionary
        results[f'{port}'] = {
            'Mean': mean_return,
            't-Stat': t_stat,
            # 'p-value': p_val,
            'StdDev': std_return,
            'Sharpe':  np.sqrt(365/7) * mean_return / std_return
        }

    # Create the summary table DataFrame with portfolio names as columns
    summary_table = pd.DataFrame(results)
    return summary_table



    
def double_sort(df_panel,dom_variable,secondary_variable, n_quantiles=3, ret_agg = 'mean'):
    df_panel['primary_portfolio'] = df_panel.groupby('WeekYear')[dom_variable].transform(
        lambda x: pd.qcut(x, q=n_quantiles, labels=[f'P{i}' for i in range(1, n_quantiles+1)])
    )
    
    # Within primary portfolio, assign secondary portfolios 
    df_panel['secondary_portfolio'] = df_panel.groupby(['WeekYear', 'primary_portfolio'])[secondary_variable].transform(
        lambda x: pd.qcut(x, q=n_quantiles, labels=[f'Q{i}' for i in range(1, n_quantiles+1)])
    )

    mean_returns_table = df_panel.pivot_table(
        index='secondary_portfolio', 
        columns='primary_portfolio', 
        values='ret', 
        aggfunc= 'mean' if ret_agg == 'mean' else 'median'
    )

    return mean_returns_table

def vw_univariate_sort(df_panel,dom_variable, n_quantiles=3):
    df_panel['portfolio'] = df_panel.groupby('WeekYear')[dom_variable].transform(
        lambda x: pd.qcut(x, q=n_quantiles, labels=[f'P{i}' for i in range(1, n_quantiles+1)])
    )

    weekly_weighted = df_panel.groupby(['WeekYear', 'portfolio']).apply(
        lambda x: (x['ret'] * x['mcap']).sum() / x['mcap'].sum()
    ).reset_index(name='vw_ret')

    # Step 2: Compute the average of these weekly weighted returns for each portfolio
    portfolio_avg = weekly_weighted.groupby('portfolio')['vw_ret'].mean().reset_index()
    return portfolio_avg