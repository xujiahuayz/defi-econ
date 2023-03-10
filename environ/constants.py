from os import path
from environ.settings import PROJECT_ROOT

BOOM_BUST = {
    "boom": [(1469966400, 1472558500), (1469966800, 1469966900)],
    "bust": [(1472558500, 1475150600), (1469966900, 1469967000)],
}

FIGURE_PATH = path.join(PROJECT_ROOT, "figures")
TABLE_PATH = path.join(PROJECT_ROOT, "tables")
GLOBAL_DATA_PATH = path.join(PROJECT_ROOT, "data", "data_global")


NAMING_DICT = {
    "TVL_share": "${\it LiquidityShare}$",
    "Inflow_centrality": "${\it EigenCent}^{In}$",
    "Outflow_centrality": "${\it EigenCent}^{Out}$",
    "Volume_share": "${\it VShare}$",
    "volume_in_share": "${\it VShare}^{\it In}$",
    "volume_out_share": "${\it VShare}^{\it Out}$",
    "Borrow_share": "${\it BorrowShare}$",
    "Supply_share": "${\it SupplyShare}$",
    "betweenness_centrality_count": "${\it BetwCent}^C$",
    "betweenness_centrality_volume": "${\it BetwCent}^V$",
    "cov_gas": "${\it CovGas}$",
    "cov_sp": "${\it CovSP}$",
    "cov_eth": "${\it CovETH}$",
    "log_return": "${R}^{\it USD}$",
    "std": "${\it \sigma}^{USD}$",
    "borrow_rate": "${\it BorrowAPY}^{USD}$",
    "supply_rates": "${\it SupplyAPY}^{USD}$",
    "beta": "${\it Beta}$",
    "average_return": "${\it \mu}^{USD}$",
    "corr_gas": "${\it CorrGas}$",
    "corr_sp": "${\it CorrSP}$",
    "corr_eth": "${\it CorrETH}$",
    "Nonstable": "${\it Nonstable}$",
    "Stable": "${\it IsStable}$",
    "IsWETH": "${\it IsWETH}$",
    "Gas_fee": "${\it GasPrice}$",
    "dollar_exchange_rate": "${\it ExchangeRate}^{USD}$",
    "exceedance": "${\it exceedance}^{USD}$",
    "Gas_fee_volatility": "${\it \sigma}_{Gas}$",
    "avg_eigenvector_centrality": "${\it AvgEigenCent}$",
    "stableshare": "${\it StableShare}$",
    "stablecoin_deviation": "${\it StableDepeg}$",
    "pegging_degree": "${\it PeggingDegree}$",
    "depegging_degree": "${\it DepeggingDegree}$",
    "pegging_degree_uppeg": "${\it PeggingDegree}^{Uppeg}$",
    "pegging_degree_downpeg": "${\it PeggingDegree}^{Downpeg}$",
    "depegging_degree_uppeg": "${\it DepeggingDegree}^{Uppeg}$",
    "depegging_degree_downpeg": "${\it DepeggingDegree}^{Downpeg}$",
    "mcap_share": "${\it MCapShare}$",
    "corr_sentiment": "${\it CorrSent}$",
    "herfindahl_volume": "${\it HHIVolume}$",
    "herfindahl_inflow_centrality": "${\it HHIEigenCent}^{In}$",
    "herfindahl_outflow_centrality": "${\it HHIEigenCent}^{Out}$",
    "herfindahl_betweenness_centrality_count": "${\it HHIBetwCent}^C$",
    "herfindahl_betweenness_centrality_volume": "${\it HHIBetwCent}^V$",
    "herfindahl_tvl": "${\it HHITVL}$",
    "total_volumes": "${\it TotalVolume}$",
    "S&P": "${\it R}^{USD}_{SP}$",
    "S&P_volatility": "${\it \sigma}^{USD}_{SP}$",
}


NAMING_DICT_OLD = {
    "TVL_share": "${\it LiquidityShare}$",
    "Inflow_centrality": "${\it EigenCent}^{In}$",
    "Outflow_centrality": "${\it EigenCent}^{Out}$",
    "Volume_share": "${\it VShare}$",
    "volume_in_share": "${\it VShare}^{\it In}$",
    "volume_out_share": "${\it VShare}^{\it Out}$",
    "Borrow_share": "${\it BorrowShare}$",
    "Supply_share": "${\it SupplyShare}$",
    "betweenness_centrality_count": "${\it BetwCent}^C$",
    "betweenness_centrality_volume": "${\it BetwCent}^V$",
    "cov_gas": "${\it CovGas}$",
    "cov_sp": "${\it CovSP}$",
    "cov_eth": "${\it CovETH}$",
    "log_return": "${R}^{\it USD}$",
    "std": "${\it \sigma}^{USD}$",
    "borrow_rate": "${\it BorrowAPY}^{USD}$",
    "supply_rates": "${\it SupplyAPY}^{USD}$",
    # "is_boom": "${\it Boom}$",
    # "cor_sp": "${\it CorSP}$",
    # "cor_eth": "${\it CorETH}$",
    # "cor_gas": "${\it CorGas}$",
    # "price": "${\it Price}$",
    # "market_cap": "${\it MarketCap}$",
}


NAMING_DIC_PROPERTIES_OF_DOMINANCE = {
    # Dominance
    "Volume_share": "${\it VShare}$",
    "volume_in_share": "${\it VShare}^{\it In}$",
    "volume_out_share": "${\it VShare}^{\it Out}$",
    # Eigenvector
    "Inflow_centrality": "${\it EigenCent}^{In}$",
    "Outflow_centrality": "${\it EigenCent}^{Out}$",
    # Betweenness
    "betweenness_centrality_count": "${\it BetwCent}^C$",
    "betweenness_centrality_volume": "${\it BetwCent}^V$",
    # Store
    "Borrow_share": "${\it BorrowShare}$",
    "Supply_share": "${\it SupplyShare}$",
    "borrow_rate": "${\it BorrowAPY}^{USD}$",
    "supply_rates": "${\it SupplyAPY}^{USD}$",
    "beta": "${\it Beta}$",
    "std": "${\it \sigma}^{USD}$",
    "average_return": "${\it \mu}^{USD}$",
    # Other
    "corr_gas": "${\it CorrGas}$",
    "corr_sp": "${\it CorrSP}$",
    "corr_eth": "${\it CorrETH}$",
    "log_return": "${R}^{\it USD}$",
    # "mcap": "${\it \ln MCap}^{USD}$",
    "Nonstable": "${\i Nonstable}$",
    "Stable": "${\i Stable}$",
    "IsWETH": "${\i IsWETH}$",
    "Gas_fee": "${\it GasPrice}$",
    "dollar_exchange_rate": "${\it ExchangeRate}^{USD}$",
    "TVL_share": "${\it LiquidityShare}$",
    "exceedance": "${\it exceedance}^{USD}$",
    "Gas_fee_volatility": "${\it \sigma}_{Gas}$",
    "avg_eigenvector_centrality": "${\it AvgEigenCent}$",
    "stableshare": "${\it StableShare}$",
    "boom": "${\it DeFiboom}$",
    "bust": "${\it DeFibust}$",
    "stablecoin_deviation": "${\it StableDepeg}$",
    "pegging_degree": "${\it PeggingDegree}$",
    "depegging_degree": "${\it DepeggingDegree}$",
    "pegging_degree_uppeg": "${\it PeggingDegree}^{Uppeg}$",
    "pegging_degree_downpeg": "${\it PeggingDegree}^{Downpeg}$",
    "depegging_degree_uppeg": "${\it DepeggingDegree}^{Uppeg}$",
    "depegging_degree_downpeg": "${\it DepeggingDegree}^{Downpeg}$",
    "mcap_share": "${\it MCapShare}$",
    # Drop
    "corr_sentiment": "${\it CorrSent}$",
}

NAMING_DIC_HERFINDAHL = {
    "herfindahl_volume": "${\it HHIVolume}$",
    "herfindahl_inflow_centrality": "${\it HHIEigenCent}^{In}$",
    "herfindahl_outflow_centrality": "${\it HHIEigenCent}^{Out}$",
    "herfindahl_betweenness_centrality_count": "${\it HHIBetwCent}^C$",
    "herfindahl_betweenness_centrality_volume": "${\it HHIBetwCent}^V$",
    "herfindahl_tvl": "${\it HHITVL}$",
    "total_volumes": "${\it TotalVolume}$",
    "S&P": "${\it R}^{USD}_{SP}$",
    "S&P_volatility": "${\it \sigma}^{USD}_{SP}$",
    "Gas_fee": "${\it GasPrice}$",
    "Gas_fee_volatility": "${\it \sigma}_{Gas}$",
    "boom": "${\it DeFiboom}$",
    "bust": "${\it DeFibust}$",
}

# merge all naming dics above
# TODO: clean up - only need one naming dict
NAMING_DICT_OLD = {
    **NAMING_DICT_OLD,
    **NAMING_DIC_PROPERTIES_OF_DOMINANCE,
    **NAMING_DIC_HERFINDAHL,
}


# NAMING_DICT = {
#     "TVL_share": "${\it LiquidityShare}$",
#     "Inflow_centrality": "${\it EigenCent}^{In}$",
#     "Outflow_centrality": "${\it EigenCent}^{Out}$",
#     "Volume_share": "${\it VShare}$",
#     "volume_in_share": "${\it VShare}^{\it In}$",
#     "volume_out_share": "${\it VShare}^{\it Out}$",
#     "Borrow_share": "${\it BorrowShare}$",
#     "Supply_share": "${\it SupplyShare}$",
#     "betweenness_centrality_count": "${\it BetwCent}^C$",
#     "betweenness_centrality_volume": "${\it BetwCent}^V$",
#     "cov_gas": "${\it CovGas}$",
#     "cov_sp": "${\it CovSP}$",
#     "cov_eth": "${\it CovETH}$",
#     "log_return": "${R}^{\it USD}$",
#     "std": "${\it \sigma}^{USD}$",
#     "borrow_rate": "${\it BorrowAPY}^{USD}$",
#     "supply_rates": "${\it SupplyAPY}^{USD}$",
# }

# Initialize constants
NAMING_DIC_PROPERTIES_OF_DOMINANCE_LAG = {
    # Dominance
    "${\it VShare}$": "${\it-1 VShare}$",
    "${\it VShare}^{\it In}$": "${\it-1 VShare}^{\it-1 In}$",
    "${\it VShare}^{\it Out}$": "${\it-1 VShare}^{\it-1 Out}$",
    # Eigenvector
    "${\it EigenCent}^{In}$": "${\it-1 EigenCent}^{In}$",
    "${\it EigenCent}^{Out}$": "${\it-1 EigenCent}^{Out}$",
    # Betweenness
    "${\it BetwCent}^C$": "${\it-1 BetwCent}^C$",
    "${\it BetwCent}^V$": "${\it-1 BetwCent}^V$",
    # Store
    "${\it BorrowShare}$": "${\it-1 BorrowShare}$",
    "${\it SupplyShare}$": "${\it-1 SupplyShare}$",
    "${\it BorrowAPY}^{USD}$": "${\it-1 BorrowAPY}^{USD}$",
    "${\it SupplyAPY}^{USD}$": "${\it-1 SupplyAPY}^{USD}$",
    "${\it Beta}$": "${\it-1 Beta}$",
    "${\it \sigma}^{USD}$": "${\it-1 \sigma}^{USD}$",
    "${\it \mu}^{USD}$": "${\it-1 \mu}^{USD}$",
    # Other
    "${\it CorrGas}$": "${\it-1 CorrGas}$",
    "${\it CorrSP}$": "${\it-1 CorrSP}$",
    "${\it CorrETH}$": "${\it-1 CorrETH}$",
    "${R}^{\it USD}$": "${R}^{\it-1 USD}$",
    "${\it MCap}^{USD}$": "${\it-1 MCap}^{USD}$",
    "${\i Nonstable}$": "${\i Nonstable}$",
    "${\i IsWETH}$": "${\i IsWETH}$",
    "${\it GasPrice}$": "${\it-1 GasPrice}$",
    "${\it ExchangeRate}^{USD}$": "${\it-1 ExchangeRate}^{USD}$",
    "${\it LiquidityShare}$": "${\it-1 LiquidityShare}$",
    "${\it exceedance}^{USD}$": "${\it-1 exceedance}^{USD}$",
    "${\it \sigma}_{Gas}$": "${\it-1 \sigma}_{Gas}$",
    # Drop
    "${\it CorrSent}$": "${\it-1 CorrSent}$",
}

NAMING_DIC_SPECIFICATION_LAG = {
    "${\it AvgEigenCent}$": "${\it-7 AvgEigenCent}$",
    "${\it EigenCent}^{In}$": "${\it-7 EigenCent}^{In}$",
    "${\it EigenCent}^{Out}$": "${\it-7 EigenCent}^{Out}$",
    "${\it BetwCent}^C$": "${\it-7 BetwCent}^C$",
    "${\it BetwCent}^V$": "${\it-7 BetwCent}^V$",
    "${\it VShare}$": "${\it-7 VShare}$",
    "${\it VShare}^{\it In}$": "${\it-7 VShare}^{\it-7 In}$",
    "${\it VShare}^{\it Out}$": "${\it-7 VShare}^{\it-7 Out}$",
    "${\i Stable}$": "${\i Stable}$",
    "${\it PeggingDegree}$": "${\it-7 PeggingDegree}$",
    "${\it DepeggingDegree}$": "${\it-7 DepeggingDegree}$",
    "${\it PeggingDegree}^{Uppeg}$": "${\it-7 PeggingDegree}^{Uppeg}$",
    "${\it PeggingDegree}^{Downpeg}$": "${\it-7 PeggingDegree}^{Downpeg}$",
    "${\it DepeggingDegree}^{Uppeg}$": "${\it-7 DepeggingDegree}^{Uppeg}$",
    "${\it DepeggingDegree}^{Downpeg}$": "${\it-7 DepeggingDegree}^{Downpeg}$",
    "${\it CorrGas}$": "${\it-7 CorrGas}$",
    "${\it CorrETH}$": "${\it-7 CorrETH}$",
    "${\it CorrSP}$": "${\it-7 CorrSP}$",
    "${\it \sigma}^{USD}$": "${\it-7 \sigma}^{USD}$",
    "${\it StableShare}$": "${\it-7 StableShare}$",
    "${\it SupplyShare}$": "${\it-7 SupplyShare}$",
    "${\it \ln MCap}^{USD}$": "${\it-7 \ln MCap}^{USD}$",
    "${\it MCapShare}$": "${\it-7 MCapShare}$",
}

NAMING_DIC_HERFINDAHL_LAG = {
    "${\it HHIVolume}$": "${\it-1 HHIVolume}$",
    "${\it HHIEigenCent}^{In}$": "${\it-1 HHIEigenCent}^{In}$",
    "${\it HHIEigenCent}^{Out}$": "${\it-1 HHIEigenCent}^{Out}$",
    "${\it HHIBetwCent}^C$": "${\it-1 HHIBetwCent}^C$",
    "${\it HHIBetwCent}^V$": "${\it-1 HHIBetwCent}^V$",
    "${\it TotalVolume}$": "${\it-1 TotalVolume}$",
    "${\it R}^{USD}_{SP}$": "${\it-1 R}^{USD}_{SP}$",
    "${\it \sigma}^{USD}_{SP}$": "${\it-1 \sigma}^{USD}_{SP}$",
    "${\it GasPrice}$": "${\it-1 GasPrice}$",
    "${\it \sigma}_{Gas}$": "${\it-1 \sigma}_{Gas}$",
}
