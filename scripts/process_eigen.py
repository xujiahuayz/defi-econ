"""
Script to generate the eigenvalues of full length volume.
"""

from environ.process.eigen_cluster.prepare_eigen_cluster import indicator_generator
from environ.constants import NETWORK_DATA_PATH, BETWEENNESS_DATA_PATH

for version in ["v2v3"]:
    indicator_generator(
        file_root=str(BETWEENNESS_DATA_PATH / "swap_route"),
        filter_name=version,
        edge_col=["ultimate_source", "ultimate_target"],
        weight_col=["volume_usd"],
        save_root=str(NETWORK_DATA_PATH / version / "eigen_centrality_undirected")
        if version != "v2v3"
        else str(NETWORK_DATA_PATH / "merged" / "eigen_centrality_undirected"),
        save_name="eigen_centrality",
        exclude_special_route=True,
        dict2str=False,
        aggreate_weight=False,
        graph_type="undirected",
        indicator_type="eigenvector",
        convert_undirected=True,
    )


# for version in ["v2", "v3", "v2v3"]:
#     eigencent_generator(
#         file_root=str(BETWEENNESS_DATA_PATH / "swap_route"),
#         filter_name=version,
#         edge_col=["ultimate_source", "ultimate_target"],
#         weight_col=["volume_usd"],
#         save_root=str(NETWORK_DATA_PATH / version / "eigen_centrality_swap")
#         if version != "v2v3"
#         else str(NETWORK_DATA_PATH / "merged" / "eigen_centrality_swap"),
#     )
