"""
Plot (auto)correlation and (auto)covariance matrices
"""

import pandas as pd

from environ.constants import DATA_PATH, DEPENDENT_VARIABLES

reg_panel = pd.read_pickle(DATA_PATH / "processed" / "reg_panel_merged.pkl")

eigen_centrality_undirected = "eigen_centrality_undirected"

var_without_na = [
    "Inflow_centrality_swap",
    "Outflow_centrality_swap",
] + list(set(DEPENDENT_VARIABLES) - {eigen_centrality_undirected})
reg_panel[var_without_na] = reg_panel[var_without_na].fillna(0)

# take the average of Inflow_centrality and Outflow_centrality for eigen_centrality_undirected
reg_panel[eigen_centrality_undirected] = (
    reg_panel["Inflow_centrality_swap"] + reg_panel["Outflow_centrality_swap"]
) / 2


# TODO: check why this is necessary -- why some eigenvector centrality values are negative?
reg_panel[DEPENDENT_VARIABLES] = reg_panel[DEPENDENT_VARIABLES].clip(lower=0)

# repickle the reg_panel
reg_panel.to_pickle(DATA_PATH / "processed" / "reg_panel_merged.pkl")
