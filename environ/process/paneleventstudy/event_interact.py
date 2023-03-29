from typing import List, Optional
import pandas as pd
import numpy as np
import statsmodels.api as sm
from linearmodels import PanelOLS
from linearmodels.panel import covariance


def event_study_interact(
    data: pd.DataFrame,
    dep_var: str,
    rel_time_vars: List[str],
    control_cohort: str,
    absorb: List[str],
    cohort: str,
    covariates: Optional[List[str]] = None,
    weights: Optional[str] = None,
) -> pd.DataFrame:
    """
    This function replicates the Stata function eventstudyinteract and returns the IW estimates for dynamic effects.

    Parameters
    ----------
    data : pd.DataFrame
        The dataset containing the variables needed for the analysis.
    dep_var : str
        The dependent variable.
    rel_time_vars : List[str]
        The list of relative time indicator variables.
    control_cohort : str
        The control cohort variable.
    absorb : List[str]
        The list of variables to be absorbed.
    cohort : str
        The cohort variable.
    covariates : Optional[List[str]], default=None
        The list of covariates to be included in the model.
    weights : Optional[str], default=None
        The name of the weight variable, if any.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the IW estimates for dynamic effects.

    """
    if covariates is None:
        covariates = []

    # Mark sample (reflects the if/in conditions, and includes only nonmissing observations)
    touse = data.notna().all(axis=1)

    # Create nvarlist and dvarlist
    nvarlist = []
    dvarlist = []
    for rel_time_var in rel_time_vars:
        dvarlist.append(rel_time_var)
        nvar = f"n_{rel_time_var}"
        data[nvar] = data[rel_time_var]
        data.loc[data[control_cohort] == 1, nvar] = 0
        nvarlist.append(nvar)

    # Get cohort count and count of relative time
    cohort_list = data.loc[data[control_cohort] == 0, cohort].unique()
    nrel_times = len(nvarlist)
    ncohort = len(cohort_list)

    # Create the interaction terms for the interacted regression
    cohort_rel_varlist = []
    for nvar in nvarlist:
        for c in cohort_list:
            cohort_rel_var = f"{nvar}_x_{c}"
            data[cohort_rel_var] = (data[cohort] == c) * data[nvar]
            cohort_rel_varlist.append(cohort_rel_var)

    # Estimate the interacted regression
    exog_vars = cohort_rel_varlist
    exog_vars += covariates
    exog = sm.add_constant(data[exog_vars])

    # Run the PanelOLS model
    panel_data = data.set_index([cohort, data.index])
    mod = PanelOLS(
        panel_data[dep_var],
        panel_data[exog_vars],
        entity_effects=True,
        weights=panel_data[weights],
    )
    return mod.fit(cov_type="clustered", cluster_entity=True)
    # res = mod.fit(cov_type="clustered", cluster_entity=True)

    # # Calculate the IW estimates
    # b_iw = []
    # V_iw_diag = []
    # for i, rel_time_var in enumerate(rel_time_vars):
    #     b_iw.append(res.params[cohort_rel_varlist[i::nrel_times]].sum())
    #     V_iw_diag.append(
    #         covariance.compute_clustered_entity_cov(res)[
    #             i::nrel_times, i::nrel_times
    #         ].sum()
    #     )

    # # Store the IW estimates in a DataFrame
    # results = pd.DataFrame(
    #     {"Variable": dvarlist, "Coefficient": b_iw, "Std. Error": np.sqrt(V_iw_diag)}
    # )
    # return results
