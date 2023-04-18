"""
Script to render the moving averages of the variables
"""

from environ.constants import EVENT_DATE_LIST, NETWORK_DATA_PATH
from environ.plot.plot_ma import plot_ma_time_series
from environ.process.market.boom_bust import BOOM_BUST


version: list = ["v2", "v3", "merged"]
plot_type_eigen: list = ["Inflow_centrality", "Outflow_centrality"]
plot_type_eigen_undirected: list = ["eigenvector_centrality"]
plot_type_cluster: list = ["clustering_coefficient"]

# generate the graph dict
graph_dict = {}

for v in version:
    for p in plot_type_eigen_undirected:
        graph_dict[f"eigen_undirected_{v}"] = {
            "file_folder": str(NETWORK_DATA_PATH / v / "eigen_centrality_undirected"),
            "file_name": f"eigen_centrality_undirected_{v}",
            "value_colume": p,
            "token_col_name": "Token",
        }

    for p in plot_type_eigen_undirected:
        graph_dict[f"eigen_undirected_multi_{v}"] = {
            "file_folder": str(
                NETWORK_DATA_PATH / v / "eigen_centrality_undirected_multi"
            ),
            "file_name": f"eigen_centrality_undirected_multi_{v}",
            "value_colume": p,
            "token_col_name": "Token",
        }

    for p in plot_type_cluster:
        graph_dict[f"cluster_{p}_swap_{v}"] = {
            "file_folder": str(NETWORK_DATA_PATH / v / "clustering_ind"),
            "file_name": f"cluster_{p}_swap_{v}",
            "value_colume": p,
            "token_col_name": "Token",
        }

    for p in plot_type_eigen:
        graph_dict[f"eigen_{p}_swap_{v}"] = {
            "file_folder": str(NETWORK_DATA_PATH / v / "eigen_centrality_swap"),
            "file_name": f"eigen_{p}_swap_{v}",
            "value_colume": p,
            "token_col_name": "Token",
        }


for key, value in graph_dict.items():
    print(rf"Plotting {key}")

    # plot the graph
    plot_ma_time_series(
        file_folder=value["file_folder"],
        file_name=value["file_name"],
        value_colume=value["value_colume"],
        token_col_name=value["token_col_name"],
        ma_window=30,
        event_date_list=EVENT_DATE_LIST,
        boom_bust=BOOM_BUST,
    )
