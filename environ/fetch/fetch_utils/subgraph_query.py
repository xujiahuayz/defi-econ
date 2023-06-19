"""
Query structure from the API.
"""

import requests

HTTP_V2 = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2"
HTTP_V3 = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3"


def run_query(http: str, query_scripts: str) -> None:
    """
    execute query without variable parameters
    """
    # endpoint where you are making the request
    request = requests.post(http, "", json={"query": query_scripts}, timeout=120)
    if request.status_code == 200:
        return request.json()

    raise Exception(
        f"Query failed. return code is{request.status_code}.      {query_scripts}"
    )


def run_query_var(http: str, query_scripts: str, var: dict[str, str]) -> None:
    """
    execute query with variable paramters
    """
    # endpoint where you are making the request
    request = requests.post(
        http, "", json={"query": query_scripts, "variables": var}, timeout=120
    )
    if request.status_code == 200:
        return request.json()

    raise Exception(
        f"Query failed. return code is{request.status_code}.      {query_scripts}"
    )
