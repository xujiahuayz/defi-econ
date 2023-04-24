"""
Script to plot herfindahl index
"""

from matplotlib import pyplot as plt
import pandas as pd
from environ.constants import FIGURE_PATH, PROCESSED_DATA_PATH
from environ.utils.variable_constructer import map_variable_name_latex


herf_panel = pd.read_pickle(
    PROCESSED_DATA_PATH / "herf_panel_merged.pickle.zip", compression="zip"
)

# plot two subplots side by side
fig, ax = plt.subplots(1, 2, figsize=(12, 6))

for graph_idx, v in [
    (1, "herfindahl_volume"),
    (0, "herfindahl_betweenness_centrality_count"),
    (0, "herfindahl_betweenness_centrality_volume"),
    (1, "herfindahl_volume_ultimate"),
    (0, "herfindahl_vol_inter_full_len"),
    (1, "herfindahl_tvl"),
]:
    # TODO: check abnormal value with HHITVL
    ax[graph_idx].plot(
        herf_panel["Date"],
        herf_panel[v],
        label=map_variable_name_latex(v),
        linewidth=0.75,
        alpha=0.8,
    )

for graph_idx in [0, 1]:
    ax[graph_idx].legend(
        loc="upper left",
        bbox_to_anchor=(1.01, 1),
    )

    # rotate x axis label by 45 degree
    for tick in ax[graph_idx].get_xticklabels():
        tick.set_rotation(45)

    # set all y axis label to be 0 to 1
    ax[graph_idx].set_ylim(0, 1)

# tight layout
fig.tight_layout()


plt.savefig(FIGURE_PATH / "herfindahl_many.pdf")
