"""
a parameterized solution to run a query like
{
  pairHourDatas(first: 3,orderBy: hourStartUnix, orderDirection: desc, where: {
    pair: "0xffa98a091331df4600f87c9164cd27e8a5cd2405", hourStartUnix_lt: 1646996400
  }) {
    id
    reserveUSD
    hourStartUnix
    pair {id}
}
}
"""

import requests
import json
from pprint import pprint

URL = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2"
BATCH_SIZE = 2  # can go up to 1_000
SERIES_NAME = "pairHourDatas"


def query_structurer(series: str, spec: str, arg: str = "") -> str:
    """
    format query arguments
    """
    if arg != "":
        arg = "(" + arg + ")"

    # format query content
    q = series + arg + "{" + spec + "}"
    return q


def graphdata(*q, url: str):
    """
    pack all subqueries into one big query concatenated with linebreak '\n'
    """

    query = "{" + "\n".join(q) + "}"

    # pretty print out query, can be commented out
    # pprint(query)

    r = requests.post(url, json={"query": query})

    response_list = json.loads(r.text)["data"][SERIES_NAME]
    return response_list


spec = """
    id
    reserveUSD
    hourStartUnix
    pair {
      id
      }
"""
pair_address = "0xffa98a091331df4600f87c9164cd27e8a5cd2405"
hour_lt = 1647014400
final_result = []

for _ in range(3):
    arg = f'first: {BATCH_SIZE}, orderBy: hourStartUnix, orderDirection: desc, where: {{pair: "{pair_address}", hourStartUnix_lt: {hour_lt}}}'
    uniswap_result = graphdata(
        query_structurer(series=SERIES_NAME, spec=spec, arg=arg), url=URL
    )
    hour_lt = uniswap_result[-1]["hourStartUnix"]
    final_result = final_result + uniswap_result

pprint(final_result)
