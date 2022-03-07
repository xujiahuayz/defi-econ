import requests
import json
from pprint import pprint

reserves_query = """
query {
  reserves (first: 6) {
    id
    symbol
    name
    decimals
    usageAsCollateralEnabled
    borrowingEnabled
    price {
      # id
      priceInEth
    }
    lastUpdateTimestamp
    baseLTVasCollateral
    aToken {
    id
    # underlyingAssetAddress
    underlyingAssetDecimals
  }
  }
}
"""

api_key = '045ea7d75e95bf4d87943ecc70cd4c31'
# url = 'https://api.thegraph.com/subgraphs/name/aave/protocol-raw'
url = f'https://gateway.thegraph.com/api/{api_key}/subgraphs/id/0x0d69090672c1e5a94e9aedfbc59558d18a78e1d3-0'
r = requests.post(url, json={'query': reserves_query})
reserves_json = json.loads(r.text)['data']['reserves']

pprint(reserves_json)
