from matplotlib import pyplot as plt
import pandas as pd
from data.constants import FIGURE_PATH, TABLE_PATH
from environ.utils.variable_constructer import map_variable_name_latex


herf_panel = pd.read_pickle(TABLE_PATH / "herf_panel.pkl")

for v in [
    "herfindahl_volume",
    "herfindahl_betweenness_centrality_count",
    "herfindahl_betweenness_centrality_volume",
    "herfindahl_tvl",
]:
    # TODO: check abnormal value with HHITVL
    plt.plot(herf_panel["Date"], herf_panel[v], label=map_variable_name_latex(v))

plt.legend(
    loc="upper left",
    bbox_to_anchor=(1.01, 1),
)

# rotate x axis label by 45 degree
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig(FIGURE_PATH / "herfindahl_many.pdf")
