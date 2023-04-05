"""
Script to render the moving averages of the variables
"""

from environ.constants import EVENT_DATE_LIST, NETWORK_DATA_PATH
from environ.plot.plot_ma import plot_ma_time_series
from environ.process.market.boom_bust import BOOM_BUST

# GRAPH_DICT = {
#     "eigen_in_swap_v2": {
#         "file_folder": str(NETWORK_DATA_PATH / "v2" / "eigen_centrality_swap"),
#         "file_name": "eigen_in_swap_v2",
#         "value_colume": "Inflow_centrality",
#         "token_col_name": "Token",
#     },
#     "eigen_in_swap_v3": {
#         "file_folder": str(NETWORK_DATA_PATH / "v3" / "eigen_centrality_swap"),
#         "file_name": "eigen_in_swap_v3",
#         "value_colume": "Inflow_centrality",
#         "token_col_name": "Token",
#     },
#     "eigen_in_swap_merged": {
#         "file_folder": str(NETWORK_DATA_PATH / "merged" / "eigen_centrality_swap"),
#         "file_name": "eigen_in_swap_merged",
#         "value_colume": "Inflow_centrality",
#         "token_col_name": "Token",
#     },
#     "eigen_out_swap_v2": {
#         "file_folder": str(NETWORK_DATA_PATH / "v2" / "eigen_centrality_swap"),
#         "file_name": "eigen_out_swap_v2",
#         "value_colume": "Outflow_centrality",
#         "token_col_name": "Token",
#     },
#     "eigen_out_swap_v3": {
#         "file_folder": str(NETWORK_DATA_PATH / "v3" / "eigen_centrality_swap"),
#         "file_name": "eigen_out_swap_v3",
#         "value_colume": "Outflow_centrality",
#         "token_col_name": "Token",
#     },
#     "eigen_out_swap_merged": {
#         "file_folder": str(NETWORK_DATA_PATH / "merged" / "eigen_centrality_swap"),
#         "file_name": "eigen_out_swap_merged",
#         "value_colume": "Outflow_centrality",
#         "token_col_name": "Token",
#     },
# }


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

# for version in ["v2", "v3", "merged"]:
#     for plot_type in ["Inflow_centrality", "Outflow_centrality"]:
#         plot_ma_time_series(
#             file_folder=str(NETWORK_DATA_PATH / version / "eigen_centrality_swap"),
#             file_name=f"eigen_in_swap_{version}"
#             if plot_type == "Inflow_centrality"
#             else f"eigen_out_swap_{version}",
#             value_colume=plot_type,
#             token_col_name="Token",
#             ma_window=30,
#             event_date_list=EVENT_DATE_LIST,
#             boom_bust=BOOM_BUST,
#         )

# plot_ma_time_series(
#     file_folder=str(NETWORK_DATA_PATH / "eigen_centrality_pool")
#     + rf"/*_{version}_*",
#     file_name=f"eigen_in_{version}"
#     if plot_type == "Inflow_centrality"
#     else f"eigen_out_{version}",
#     value_colume=plot_type,
#     token_col_name="Token",
#     ma_window=30,
#     event_date_list=EVENT_DATE_LIST,
#     boom_bust=BOOM_BUST,
# )
