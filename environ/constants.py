from os import path
from environ.settings import PROJECT_ROOT

BOOM_BUST = {
    "boom": [(1469966400, 1472558500), (1469966800, 1469966900)],
    "bust": [(1472558500, 1475150600), (1469966900, 1469967000)],
}

FIGURE_PATH = path.join(PROJECT_ROOT, "figures")
TABLE_PATH = path.join(PROJECT_ROOT, "tables")

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
    "${\t GasPrice}$": "${\t-1 GasPrice}$",
    "${\it ExchangeRate}^{USD}$": "${\it-1 ExchangeRate}^{USD}$",
    "${\it LiquidityShare}$": "${\it-1 LiquidityShare}$",
    "${\it exceedance}^{USD}$": "${\it-1 exceedance}^{USD}$",
    "${\t \sigma}_{Gas}$": "${\t-1 \sigma}_{Gas}$",
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
    "${\t HHIVolume}$": "${\t-1 HHIVolume}$",
    "${\t HHIEigenCent}^{In}$": "${\t-1 HHIEigenCent}^{In}$",
    "${\t HHIEigenCent}^{Out}$": "${\t-1 HHIEigenCent}^{Out}$",
    "${\t HHIBetwCent}^C$": "${\t-1 HHIBetwCent}^C$",
    "${\t HHIBetwCent}^V$": "${\t-1 HHIBetwCent}^V$",
    "${\t TotalVolume}$": "${\t-1 TotalVolume}$",
    "${\t R}^{USD}_{SP}$": "${\t-1 R}^{USD}_{SP}$",
    "${\t \sigma}^{USD}_{SP}$": "${\t-1 \sigma}^{USD}_{SP}$",
    "${\t GasPrice}$": "${\t-1 GasPrice}$",
    "${\t \sigma}_{Gas}$": "${\t-1 \sigma}_{Gas}$",
}
