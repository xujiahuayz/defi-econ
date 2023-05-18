"""
Constants for the project.
"""

from pathlib import Path

from environ.settings import PROJECT_ROOT

# google what is my user agent to get it
USER_AGENT: str = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    + "AppleWebKit/537.36 (KHTML, like Gecko) "
    + "Chrome/111.0.0.0 Safari/537.36"
)


SAMPLE_PERIOD = [
    "2020-07-01",
    "2023-01-31",
]

KEY_TOKEN_LIST = ["WETH", "WBTC", "MATIC", "USDC", "USDT", "DAI", "FEI"]

EVENT_DATE_LIST = ["2020-11-26", "2021-05-05", "2022-05-10", "2022-11-11"]

FIGURE_PATH: Path = PROJECT_ROOT / "figures"
TABLE_PATH: Path = PROJECT_ROOT / "tables"
DATA_PATH: Path = PROJECT_ROOT / "data"
PROCESSED_DATA_PATH: Path = PROJECT_ROOT / "processed_data"
GLOBAL_DATA_PATH: Path = PROJECT_ROOT / "data" / "data_global"
BETWEENNESS_DATA_PATH: Path = PROJECT_ROOT / "data" / "data_betweenness"
NETWORK_DATA_PATH: Path = PROJECT_ROOT / "data" / "data_network"
PLOT_DATA_PATH: Path = PROJECT_ROOT / "data" / "data_plot"
COMPOUND_DATA_PATH: Path = PROJECT_ROOT / "data" / "data_compound"
CACHE_PATH: Path = PROJECT_ROOT / ".cache"
TEST_RESULT_PATH: Path = PROJECT_ROOT / "test_results"
UNISWAP_V2_DATA_PATH: Path = PROJECT_ROOT / "data" / "data_uniswap_v2"
UNISWAP_V3_DATA_PATH: Path = PROJECT_ROOT / "data" / "data_uniswap_v3"

# Information fo variables to be merged into the main panel
PANEL_VAR_INFO = {
    "panel_var": [
        {
            "data_path": NETWORK_DATA_PATH / "merged" / "volume_total",
            "data_col": ["Volume"],
            "rename_dict": {"Volume": "Volume"},
        },
        {
            "data_path": NETWORK_DATA_PATH / "merged" / "inflow_centrality",
            "data_col": ["Inflow_centrality"],
            "rename_dict": {
                "eigenvector_centrality": "Inflow_centrality",
                "token": "Token",
            },
        },
        {
            "data_path": NETWORK_DATA_PATH / "merged" / "outflow_centrality",
            "data_col": ["Outflow_centrality"],
            "rename_dict": {
                "eigenvector_centrality": "Outflow_centrality",
                "token": "Token",
            },
        },
        {
            "data_path": NETWORK_DATA_PATH / "merged" / "tvl",
            "data_col": ["TVL"],
            "rename_dict": {"total_tvl": "TVL", "token": "Token"},
        },
        {
            "data_path": NETWORK_DATA_PATH / "merged" / "volume_in",
            "data_col": ["volume_in"],
            "rename_dict": {"Volume": "volume_in"},
        },
        {
            "data_path": NETWORK_DATA_PATH / "merged" / "volume_out",
            "data_col": ["volume_out"],
            "rename_dict": {"Volume": "volume_out"},
        },
        {
            "data_path": COMPOUND_DATA_PATH / "processed",
            "data_col": ["Borrow_share", "Supply_share", "borrow_rate", "supply_rates"],
            "rename_dict": {
                "borrow_share": "Borrow_share",
                "supply_share": "Supply_share",
            },
        },
        {
            "data_path": NETWORK_DATA_PATH / "merged" / "betweenness",
            "data_col": [
                "betweenness_centrality_count",
                "betweenness_centrality_volume",
            ],
            "rename_dict": {"node": "Token"},
        },
        {
            "data_path": NETWORK_DATA_PATH / "merged" / "vol_in_full_len",
            "data_col": ["vol_in_full_len"],
            "rename_dict": {
                "volume": "vol_in_full_len",
            },
        },
        {
            "data_path": NETWORK_DATA_PATH / "merged" / "vol_out_full_len",
            "data_col": ["vol_out_full_len"],
            "rename_dict": {
                "volume": "vol_out_full_len",
            },
        },
        {
            "data_path": NETWORK_DATA_PATH / "merged" / "vol_inter_full_len",
            "data_col": ["vol_inter_full_len"],
            "rename_dict": {
                "volume": "vol_inter_full_len",
            },
        },
        {
            "data_path": NETWORK_DATA_PATH / "merged" / "eigen_centrality_undirected",
            "data_col": ["eigen_centrality_undirected"],
            "rename_dict": {
                "eigenvector_centrality": "eigen_centrality_undirected",
            },
        },
        {
            "data_path": NETWORK_DATA_PATH
            / "merged"
            / "total_eigen_centrality_undirected",
            "data_col": ["total_eigen_centrality_undirected"],
            "rename_dict": {
                "eigenvector_centrality": "total_eigen_centrality_undirected",
            },
        },
    ],
    "corr_var": {
        "corr_gas": "gas_price_usd",
        "corr_eth": "ether_price_usd",
        "corr_sp": "S&P",
    },
    "share_var": [
        "Volume",
        "TVL",
        "volume_in",
        "volume_out",
        "vol_in_full_len",
        "vol_out_full_len",
        "vol_inter_full_len",
        "volume_ultimate",
        "mcap",
    ],
}

# Information fo variables to be merged into the herfindal pane;
HERFIN_VAR_INFO = {
    "volume_ultimate_share": "herfindahl_volume_ultimate",
    "betweenness_centrality_count": "herfindahl_betweenness_centrality_count",
    "betweenness_centrality_volume": "herfindahl_betweenness_centrality_volume",
    "vol_inter_full_len_share": "herfindahl_vol_inter_full_len",
    "Volume_share": "herfindahl_volume",
}

DEPENDENT_VARIABLES = [
    "volume_ultimate_share",
    "eigen_centrality_undirected",
    "vol_inter_full_len_share",
    "betweenness_centrality_volume",
    "betweenness_centrality_count",
    "total_eigen_centrality_undirected",
    "Volume_share",
]

# Aave pool deployment time
AAVE_DEPLOYMENT_DATE = [
    {
        "Token": "ETH",
        "poolAddress": "0x030ba81f1c18d280636f32af80b9aad02cf0854e",
        "Date": "2020-11-30 22:20:30",
    },
    {
        "Token": "USDC",
        "poolAddress": "0xbcca60bb61934080951369a648fb03df4f96263c",
        "Date": "2020-12-01 14:23:56",
    },
    {
        "Token": "USDT",
        "poolAddress": "0x3ed3b47dd13ec9a98b44e6204a523e766b225811",
        "Date": "2020-11-30 22:20:30",
    },
    {
        "Token": "WBTC",
        "poolAddress": "0x9ff58f4ffb29fa2266ab25e75e2a8b3503311656",
        "Date": "2020-11-30 22:20:30",
    },
    {
        "Token": "DAI",
        "poolAddress": "0x028171bca77440897b824ca71d1c56cac55b68a3",
        "Date": "2020-12-01 14:22:02",
    },
    {
        "Token": "UNI",
        "poolAddress": "0xb9d7cb55f463405cdfbe4e90a6d2df01c2b92bf1",
        "Date": "2020-11-30 22:20:58",
    },
    {
        "Token": "LINK",
        "poolAddress": "0xa06bc25b5805d5f8d82847d191cb4af5a3e873e0",
        "Date": "2020-12-01 14:23:08",
    },
    {
        "Token": "FRAX",
        "poolAddress": "0xd4937682df3c8aef4fe912a96a74121c0829e664",
        "Date": "2021-09-11 23:42:46",
    },
    {
        "Token": "GUSD",
        "poolAddress": "0xd37ee7e4f452c6638c96536e68090de8cbcdb583",
        "Date": "2021-01-02 19:16:42",
    },
    {
        "Token": "LUSD",
        "poolAddress": "0xce1871f791548600cb59efbeffc9c38719142079",
        "Date": "2022-08-29 19:06:59",
    },
    {
        "Token": "sUSD",
        "poolAddress": "0x6c5024cd4f8a59110119c56f8933403a539555eb",
        "Date": "2020-12-01 14:23:43",
    },
    {
        "Token": "TUSD",
        "poolAddress": "0x101cc05f4a51c0319f570d5e146a8c625198e636",
        "Date": "2020-12-01 14:23:56",
    },
    {
        "Token": "USDP",
        "poolAddress": "0x2e8f4bdbe3d47d7d7de490437aea9915d930f1a3",
        "Date": "2021-07-25 12:17:36",
    },
    {
        "Token": "1INCH",
        "poolAddress": "0xb29130cbcc3f791f077eade0266168e808e5151e",
        "Date": "2022-07-30 17:30:33",
    },
    {
        "Token": "AAVE",
        "poolAddress": "0xffc97d72e13e01096502cb8eb52dee56f74dad7b",
        "Date": "2020-12-01 14:22:02",
    },
    {
        "Token": "CRV",
        "poolAddress": "0x8dae6cb04688c62d939ed9b68d32bc62e49970b1",
        "Date": "2020-12-27 21:46:55",
    },
    {
        "Token": "DPI",
        "poolAddress": "0x6f634c6135d2ebd550000ac92f494f9cb8183dae",
        "Date": "2021-08-21 17:42:40",
    },
    {
        "Token": "ENS",
        "poolAddress": "0x9a14e23a58edf4efdcb360f68cd1b95ce2081a2f",
        "Date": "2022-03-07 06:02:56",
    },
    {
        "Token": "MKR",
        "poolAddress": "0xc713e5e149d5d0715dcd1c156a020976e7e56b88",
        "Date": "2020-12-01 14:23:43",
    },
    {
        "Token": "SNX",
        "poolAddress": "0x35f6b052c598d933d69a4eec4d04c73a191fe6c2",
        "Date": "2020-12-01 14:23:43",
    },
    {
        "Token": "stETH",
        "poolAddress": "0x1982b2f5814301d4e9a8b0201555376e62f82428",
        "Date": "2022-02-27 16:22:12",
    },
    {
        "Token": "WETH",
        "poolAddress": "0x030ba81f1c18d280636f32af80b9aad02cf0854e",
        "Date": "2020-11-30 22:20:30",
    },
]


# Compound pool deployment time
COMPOUND_DEPLOYMENT_DATE = [
    {
        "Token": "ETH",
        "poolAddress": "0x4ddc2d193948926d02f9b1fe9e1daa0718270ed5",
        "Date": "2019-05-07 01:25:18",
    },
    {
        "Token": "USDC",
        "poolAddress": "0x39aa39c021dfbae8fac545936693ac917d5e7563",
        "Date": "2019-05-07 01:25:31",
    },
    {
        "Token": "USDT",
        "poolAddress": "0xf650c3d88d12db855b8bf7d11be6c55a4e07dcc9",
        "Date": "2020-04-15 21:13:06",
    },
    {
        "Token": "WBTC",
        "poolAddress": "0xc11b1268c1a384e55c48c2391d8d480264a3a7f4",
        "Date": "2019-07-16 19:47:37",
    },
    {
        "Token": "DAI",
        "poolAddress": "0x5d3a536e4d6dbd6114cc1ead35777bab948e3643",
        "Date": "2019-11-23 01:03:33",
    },
    {
        "Token": "UNI",
        "poolAddress": "0x35a18000230da775cac24873d00ff85bccded550",
        "Date": "2020-09-23 22:05:47",
    },
    {
        "Token": "SAI",
        "poolAddress": "0xf5dce57282a584d2746faf1593d3121fcac444dc",
        "Date": "2019-05-07 01:24:12",
    },
    {
        "Token": "REP",
        "poolAddress": "0x158079ee67fce2f58472a96584a73c7ab9ac95c1",
        "Date": "2019-05-07 01:24:48",
    },
    {
        "Token": "MKR",
        "poolAddress": "0x95b4ef2869ebd94beb4eee400a99824bf5dc325b",
        "Date": "2021-07-16 05:30:17",
    },
    {
        "Token": "YFI",
        "poolAddress": "0x80a2ae356fc9ef4305676f7a3e2ed04e12c33946",
        "Date": "2021-07-18 03:19:05",
    },
    {
        "Token": "USDP",
        "poolAddress": "0x041171993284df560249b57358f931d9eb7b925d",
        "Date": "2021-09-19 19:42:57",
    },
    {
        "Token": "ZRX",
        "poolAddress": "0xb3319f5d18bc0d84dd1b4825dcde5d5f7266d407",
        "Date": "2019-05-07 01:20:54",
    },
    {
        "Token": "SUSHI",
        "poolAddress": "0x4b0181102a0112a2ef11abee5563bb4a3176c9d7",
        "Date": "2021-07-18 03:12:59",
    },
    {
        "Token": "FEI",
        "poolAddress": "0x7713dd9ca933848f6819f38b8352d9a15ea73f67",
        "Date": "2021-09-15 02:26:35",
    },
    {
        "Token": "BAT",
        "poolAddress": "0x6c8c6b02e7b2be14d4fa6022dfd6d75921d90e4e",
        "Date": "2019-05-07 01:21:25",
    },
    {
        "Token": "COMP",
        "poolAddress": "0x70e36f6bf80a52b3b46b3af8e106cc0ed743e8e4",
        "Date": "2020-09-29 10:41:05",
    },
    {
        "Token": "TUSD",
        "poolAddress": "0x12392f67bdf24fae0af363c24ac620a2f67dad86",
        "Date": "2020-10-07 11:45:29",
    },
    {
        "Token": "AAVE",
        "poolAddress": "0xe65cdb6479bac1e22340e4e755fae7e509ecd06c",
        "Date": "2021-07-18 03:19:05",
    },
    {
        "Token": "LINK",
        "poolAddress": "0xface851a4921ce59e912d19329929ce6da6eb0c7",
        "Date": "2021-04-21 21:38:22",
    },
    {
        "Token": "WBTC2",
        "poolAddress": "0xccF4429DB6322D5C611ee964527D42E5d685DD6a",
        "Date": "2021-03-14 07:44:47",
    },
]

STABLE_DICT = {
    "BUSD": {"underlying": "USD", "color": "blue", "line_type": "solid"},
    "DAI": {"underlying": "USD", "color": "red", "line_type": "dashdot"},
    "DSD": {"underlying": "USD", "color": "green", "line_type": "dashed"},
    "ESD": {"underlying": "USD", "color": "orange", "line_type": "dotted"},
    "EURS": {"underlying": "EUR", "color": "purple", "line_type": "solid"},
    "EURT": {"underlying": "EUR", "color": "brown", "line_type": "dashdot"},
    "FEI": {"underlying": "USD", "color": "pink", "line_type": "dashed"},
    "FRAX": {"underlying": "USD", "color": "gray", "line_type": "dotted"},
    "LUSD": {"underlying": "USD", "color": "olive", "line_type": "solid"},
    "MIM": {"underlying": "USD", "color": "cyan", "line_type": "dashdot"},
    "PAX": {"underlying": "USD", "color": "magenta", "line_type": "dashed"},
    "TUSD": {"underlying": "USD", "color": "black", "line_type": "dotted"},
    "USDC": {"underlying": "USD", "color": "blue", "line_type": "solid"},
    "USDT": {"underlying": "USD", "color": "red", "line_type": "dashdot"},
    "UST": {"underlying": "USD", "color": "green", "line_type": "dashed"},
    "XSGD": {"underlying": "SGD", "color": "orange", "line_type": "dotted"},
    "agEUR": {"underlying": "EUR", "color": "purple", "line_type": "solid"},
    "oneUNI": {"underlying": "USD", "color": "brown", "line_type": "dashdot"},
    "sUSD": {"underlying": "USD", "color": "pink", "line_type": "dashed"},
}

TOKEN_PLOT_DICT = {
    "WETH": {"color": "blue", "line_type": "solid"},
    "WBTC": {"color": "red", "line_type": "dashdot"},
    "USDC": {"color": "green", "line_type": "dashed"},
    "DAI": {"color": "orange", "line_type": "dotted"},
    "USDT": {"color": "purple", "line_type": "solid"},
    "MATIC": {"color": "brown", "line_type": "dashdot"},
    "FEI": {"color": "pink", "line_type": "dashed"},
}

# combine stable_dict and token_plot_dict to get color and line_type for all tokens
ALL_TOKEN_DICT = {**STABLE_DICT, **TOKEN_PLOT_DICT}


# get all unique underling from stable_dict
FIAT_LIST = list(set([v["underlying"] for v in STABLE_DICT.values()]))

ALL_NAMING_DICT = {
    "eigen_centrality_undirected": "{\it EigenCent^{\it Ulti}}",
    "total_eigen_centrality_undirected": "{\it EigenCent}",
    "TVL_share": "{\it LiquidityShare}",
    "Inflow_centrality": "{\it EigenCent}^{In}",
    "Outflow_centrality": "{\it EigenCent}^{Out}",
    "Volume_share": "{\it VShare}",
    "volume_in_share": "{\it VShare}^{\it In}",
    "volume_out_share": "{\it VShare}^{\it Out}",
    "volume_ultimate_share": "{\it {VShare}^{\it Ulti}}",
    # "volume_
    "Borrow_share": "{\it BorrowShare}",
    "Supply_share": "{\it SupplyShare}",
    "betweenness_centrality_count": "{\it BetwCent}^{\it E}",
    "betweenness_centrality_volume": "{\it BetwCent}^{\it V}",
    "cov_gas": "{\it CovGas}",
    "cov_sp": "{\it CovSP}",
    "cov_eth": "{\it CovETH}",
    "log_return": "{R}^{\it USD}",
    "std": "{\it \sigma}^{USD}",
    "borrow_rate": "{\it BorrowAPY}^{USD}",
    "supply_rates": "{\it SupplyAPY}^{USD}",
    "beta": "{\it Beta}",
    "average_return": "{\it \mu}^{USD}",
    "corr_gas": "{\it CorGas}",
    "corr_sp": "{\it CorSP}",
    "corr_eth": "{\it CorETH}",
    "Nonstable": "{\it Nonstable}",
    "Stable": "{\it IsStable}",
    "IsWETH": "{\it IsWETH}",
    # TODO: to be removed
    "Gas_fee": "{\it GasPrice_old}",
    "gas_price_usd": "{\it GasPrice}^{USD}",
    "dollar_exchange_rate": "{\it ExchangeRate}^{USD}",
    "exceedance": "{\it exceedance}^{USD}",
    # TODO: to be removed
    "Gas_fee_volatility": "{\it \sigma}_{Gas}",
    "gas_price_usd_log_return_vol_1_30": "{\it \sigma}_{Gas}^{USD}",
    "avg_eigenvector_centrality": "{\it AvgEigenCent}",
    "stableshare": "{\it StableShare}",
    "stablecoin_deviation": "{\it StableDepeg}",
    "pegging_degree": "{\it PeggingDegree}",
    "depegging_degree": "{\it DepeggingDegree}",
    "pegging_degree_uppeg": "{\it PeggingDegree}^{Uppeg}",
    "pegging_degree_downpeg": "{\it PeggingDegree}^{Downpeg}",
    "depegging_degree_uppeg": "{\it DepeggingDegree}^{Uppeg}",
    "depegging_degree_downpeg": "{\it DepeggingDegree}^{Downpeg}",
    "itlnMCapUSD": "{\it \ln MCap}^{USD}",
    "mcap_share": "{\it MCapShare}",
    "corr_sentiment": "{\it CorrSent}",
    "herfindahl_volume": "{\it HHI_{VShare}}",
    "herfindahl_inflow_centrality": "{\it HHIEigenCent}^{In}",
    "herfindahl_outflow_centrality": "{\it HHIEigenCent}^{Out}",
    "herfindahl_betweenness_centrality_count": "{\it HHI_{{BetwCent}^{\it E}}}",
    "herfindahl_betweenness_centrality_volume": "{\it HHI_{{BetwCent}^{\it V}}}",
    "herfindahl_tvl": "{\it HHI_{LiquidityShare}}",
    "herfindahl_volume_ultimate": "{\it HHI_{{VShare}^{\it Ulti}}}",
    "herfindahl_vol_inter_full_len": "{\it HHI_{{VShare}^{\it Betw}}}",
    "total_volumes": "{\it MarketVolume}",
    "S&P": "{\it R}^{USD}_{SP}",
    # TODO: to be removed
    "S&P_volatility": "{\it \sigma}^{USD}_{SP}",
    "S&P_log_return_vol_1_30": "{\it \sigma}^{USD}_{SP}",
    "depeg_pers": "{\it DepegPersist}",
    "is_boom": "{\it IsBoom}",
    "after_treated_date": "{\it AfterTreatedDate}",
    "is_treated_token": "{\it IsTreatedToken}",
    "avg_cluster": "{\it AvgClustCoef}",
    "norm_clique_num": "{\it NumClique / NumTxn}",
    "vol_undirected_full_len_share": "{\it VShare}^{\it Ulti}",
    "vol_inter_full_len_share": "{\it VShare}^{\it Betw}",
    "dollar_exchange_rate_log_return_1": "\ln R",
}
