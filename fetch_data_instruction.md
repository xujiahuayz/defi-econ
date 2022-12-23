# DeFi Economics

## Data Sources

- DEX: Uniswap

  - Uniswap V2: fetched by Uniswap V2 Subgraph
  - Uniswap V3: fetched by Uniswap V2 Subgraph

- DeFi Lending

  - Compound: https://api.compound.finance/
  - AAVE: download from DuneAnalytics

- Global Data
  - Ethereum Gas Fee, ETH Price: Etherscan
  - Token Price: https://www.coingecko.com/en/api
  - Token Market Cap: https://www.coingecko.com/en/api (WETH: Infura archive node)
  - Volatility of Gas Fee and Token Price

## Uniswap (Aggregated)

**WORK FLOW SCRIPTS AS [`scripts/fetch_integrated_data_uniswap.py`](scripts/fetch_integrated_data_uniswap.py)**

1. **Step 1**: Determine the top 50 pools by the avg daily volume for the given time period: `select_top50_pairs_vX_script.py` `select_top50_pairs_vX(end_date, 31, top50_list_label)`

   - example: Monthly top50 pools
   - input: 2022-5-31 as `end_date`, 31 as `period`, "2022MAY" as `top50_list_label`
   - output: `data_uniswap_vX/top50_pairs_list_v2_2022MAY.csv`
     - dailyVolumeUSD: only for the single end date
     - pastValidDays: how many trading days in the past period, filter can be controlled by the `valid_threshold` (for example, one pool created at 15 May was removed, because there are only 31-16=15 < 31 valid days between 2022-5-1 and 2022-5-31)
     - pastTotalVolumeUSD: sum of the daily volume USD for all days in the past period
     - avgDailyVolumeUSD: average of daily volume (pastTotalVolumeUSD/pastValidDays)

2. **Step 2**: Get directional daily volume for all dates based on the list in Step 1:
   `top50_pair_directional_volume_vX_script.py` `top50_pair_directional_volume_vX(date, top50_list_label)`

   - example: directional daily volume for 20220531
   - input: date, top50_list_label (e.g. "2022MAY")
   - output: `data_uniswap_vX/top50_directional_volume_vX_YYYYMMDD.csv`
     - token0To1VolumeUSD, token1To0VolumeUSD, GrossVolumeUSD (e.g. USDC -> WETH, WETH -> USDC)
     - mintsCount, burnsCount, swapsCount

3. **Step 3**: prepare the network data from the "top50_directional_volume.csv" in Step 2:
   transfer the directional volume by pair (USDC <-> WETH) to node lists (USDC, WETH) and edge lists (USDC -> WETH, WETH -> USDC)
   `prepare_network_data.py` `prepare_network_data(date, uniswap_version)`

   - example: node list and edge list for 20220531
   - input: date, uniswap_version ("v2" or "v3")
   - output: `data_network/primary_tokens_YYYYMMDD.csv` as node list

     - token: distinct tokens involved in the top50 pools
     - total_tvl: sum up total liquidity snapshots of pools which token involved in top50 pools

   - output: `data_network/inout_flow_tokens_YYYYMMDD.csv` as edge list
     - Source, Target
     - Volume (daily trading volume USD from tokenA to tokenB)

4. **Step 4**: generate network plot and degree dataset
   plot the network by networkx and calculate the centrality and degree
   `plot_network.py` `plot_network(date, uniswap_version)`

   - example: network graph, centrality and degree data file for 20220531
   - input: date, uniswap_version
   - output: `data_network/network_YYYYMMDD.jpg`
   - output: `data_network/centrality_YYYYMMDD.csv`
     - eigenvector_centrality
     - weighted_in_degree: sum up all the edges with weight by volume USD into the node
     - weighted_out_degree: sum up all the edges with weight by volume USD out of the node
     - weighted_degree: the sum of weighted_in_degree and weighted_out_degree, which indicates the total trading volume involving this token

5. Supplementary Information for Uniswap

   - Historical information of pools: `top50_pair_overview_vX_script.py` `top50_pair_overview_vX()`

     - input: top50 list label (e.g. "MAY2022")
     - output: `data_uniswap_vX/top50_pairs_overview_vX_rundate.csv`

   - All pools of protocol: `uniswap_vX_all_pools_script.py` `uniswap_vX_all_pools()`

     - input: None, and will get the snapshot at the executing date
     - output: `data_uniswap_vX/uniswap_vX_all_pools_YYYYMMDD.csv`

   - All tokens of protocol: `uniswap_vX_all_tokens_script.py` `uniswap_vX_all_tokens()`

     - input: None, and will get the snapshot at the executing date
     - output: `data_uniswap_vX/uniswap_vX_all_tokens_YYYYMMDD.csv`

   - Protocol overview: `uniswap_vX_overview_script.py`
     - input: `data_uniswap_vX/uniswap_v2_overview.csv`, read and update the csv by adding one row snapshot after executing
     - output: `uniswap_v2_overview.csv`
     - Note: recommend directly execute the script


## Uniswap (Swaps)

In the previous sections "Uniswap (Aggregated), the scripts fetch the daily aggregated data of Uniswap in the format like "GrossVolumeUSD in each day". While this section fetchs the transaction level raw data which entity is the transaction id (hash), so that the data volume is large and the fectching time is long. The raw data is primarily used for computing betweenness centrality which needs to iterate each transaction. 


**SCRIPTS AS [`scripts/fetch_swap_transactions_v2.py`](scripts/fetch_swap_transactions_v2.py) Uniswap V2 and [`scripts/fetch_swap_transactions_v3.py`](scripts/fetch_swap_transactions_v3.py) for Uniswap V3**

Note: the scripts will fetch all the swap transactions in the specific time period which would not filtered by the top50 pools. 


Extention: Work flow of computing betweenness centrality

1. **Step 1**: fetch raw data by: `fetch_swap_transactions_vX.py` `uniswap_vX_swaps(start_timestamp, end_timestamp, date_str)`

   - example: transaction level swaps data in a single day
   - input: datetime(2022, 5, 1, 0, 0) as `start_timestamp`, datetime(2022, 5, 2, 0, 0) as `end_timestamp`, 31 as `period`, "20220501" as `date_str`
   - output: `data_uniswap_vX/swap/uniswap_vX_swaps_20220501.csv`

2. **Step 1**: run computing scripts by: [`scripts/betweenness_scripts.py.py`](scripts/betweenness_scripts.py.py) `get_betweenness_centrality(date_label: str, top_list_label: str, uniswap_version: str)`

   - example: betweenness centrality in a single day
   - input: 20220501 as `date_label`,  as 2022MAY `top_list_label`, v2v3 as `uniswap_version` (candidate: v2, v3, v2v3)
   - output1: `data_betweenness/swap_route/swaps_tx_route_v2v3_20220501.csv` as the data backup for transforming transaction level raw data to the list-like transactions.
   - output2: `data_betweenness/betweenness/betweenness_centrality_v2v3_20220501.csv` as the results of betweenness centrality within one day.



## DeFi

1. Compound

   - `scripts/fetch_compound_historical_data.py` generate `data/data_compound/compound_TOKEN.csv` for the historical data of each token
   - `scripts/fetch_compound_token_list.py` generate `data/data_compound/all_compound_tokens.csv`as knowledge base

2. AAVE
   - `scripts/download_aave_historical_data.py` generate `data/data_aave/aave_top_token_historical_data.csv` for the historical data of all the tokens

## Global

### Ethereum Gas Fee

1. Gas fee
   - Gas fee by WEI: `data/data_global/gas_fee/data_source/etherscan_avg_gas_price.csv` download from https://etherscan.io/chart/gasprice
   - ETH close price: `data/data_global/gas_fee/data_source/etherscan_ether_price.csv` download from https://etherscan.io/chart/etherprice
   - Gas fee USD: use `scripts/convert_gas_fee_to_usd.py` to convert WEI to USD using the close ETH price, generate `data/data_global/gas_fee/avg_gas_fee.csv` for the daily average gas fee by USD

### Token Price

1. Token price
   - token price: fectched from https://www.coingecko.com/en/api, saved at `data/data_global/token_market/primary_token_price.csv`

### Token Market Cap

1. Token market cap except WETH:

   - market cap: fetched from https://www.coingecko.com/en/api, saved at `data/data_global/token_market/primary_token_marketcap.csv`

2. Token market cap for WETH:
   - WETH total supply: fetched on-chain data from Infura archive node
   - WETH price: token price in `primary_token_price.csv`
   - WTH market cap: WETH total supply \* WETH price

### Volatility

Volatility is calculated by the log return of price list and standard deviation for the past `30 days`
scripts: `scripts/volatility.py`

1. Gas fee volatility

   - `data/data_global/gas_fee/gas_volatility.csv`

2. Token price volatility
   - `data/data_global/token_market/primary_token_volatility.csv`

## Regression

- Dataset:
- Scripts:
- Results:

### Data Dir of Regression Variables

- **Dependent Variables**

  - **eigencentrality**: main dependent variable, which is calculated from the network `data/data_network/centrality_vX_YYYYMMDD.csv`
  - **volume_gross**: sum of volume_in and volume_out
  - **volume_in**: total daily volume USD into the token among top50 pools (sum up all the in-degree edges by weights)
  - **volume_out**: total daily volume USD out the token among top50 pools (sum up all the out-degree edges by weights)

  Note: eigencentrality would be highly correlated with volume_in and volume_out

- **Potential Independent Variables**
  - **asset_price**: token price, `data/data_global/token_market/primary_token_price.csv`
  - **price_volatility**: token price volatility (daily log return, monthly standard deviation), `data/data_global/token_market/primary_token_volatility.csv`
  - **gas_fee**: Ethereum daily average gas fee (we use unit of `USD`), `data/data_global/gas_fee/avg_gas_fee.csv`
  - **gas_vol**: gas fee volatility (regard gas fee USD as one kind of 'price', same method with `price_volatility`), `data/data_global/gas_fee/gas_volatility.csv`
  - **market_cap**: token market capitalization, `data/data_global/token_market/primary_token_marketcap.csv`
  - **defi_deposit**: [`aave_deposit`](data/data_aave/aave_top_token_historical_data.csv) + [`compound_total_supply`](data/data_compound/compound_USDC.csv)
  - **defi_borrow**: [`aave_borrow`](data/data_aave/aave_top_token_historical_data.csv) + [`compound_total_borrow`](data/data_compound/compound_USDC.csv)
    Note: Currently the `defi_deposit` and `defi_borrow` are calculated by simply sum. Weighted average or standardize may be considered in the future.
