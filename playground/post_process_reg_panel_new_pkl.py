import pandas as pd

from environ.constants import DATA_PATH, DEPENDENT_VARIABLES

reg_panel = pd.read_pickle(DATA_PATH / "reg_panel_merged.pkl")

unprocessed_dvs = ["eigen_centrality_undirected", "vol_undirected_full_len_share"]

var_without_na = [
    "Inflow_centrality_swap",
    "Outflow_centrality_swap",
    "vol_in_full_len",
    "vol_out_full_len",
] + list(set(DEPENDENT_VARIABLES) - set(unprocessed_dvs))
reg_panel[var_without_na] = reg_panel[var_without_na].fillna(0)

# take the average of Inflow_centrality and Outflow_centrality for eigen_centrality_undirected
reg_panel["eigen_centrality_undirected"] = (
    reg_panel["Inflow_centrality_swap"] + reg_panel["Outflow_centrality_swap"]
) / 2

reg_panel["vol_undirected_full_len"] = (
    reg_panel["vol_in_full_len"] + reg_panel["vol_out_full_len"]
)
# calculate each token's share of vol_undirected_full_len by day
# group by day first
reg_panel["vol_undirected_full_len_share"] = reg_panel.groupby("Date")[
    "vol_undirected_full_len"
].transform(lambda x: x / x.sum())


# TODO: check why this is necessary -- why some eigenvector centrality values are negative?
reg_panel[DEPENDENT_VARIABLES] = reg_panel[DEPENDENT_VARIABLES].clip(lower=0)


# repickle the reg_panel
reg_panel.to_pickle(DATA_PATH / "reg_panel_merged.pkl")
