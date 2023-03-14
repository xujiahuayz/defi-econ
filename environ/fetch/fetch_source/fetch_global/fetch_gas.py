"""
fetch gas and ether price from etherscan
"""

from pathlib import Path

import requests

from environ.constants import GLOBAL_DATA_PATH, USER_AGENT


def get_csv_from_etherscan(
    series: str = "gasprice",
    user_agent: str = USER_AGENT,
) -> bytes:
    """
    download data from etherscan to csv file in GLOBAL_DATA_PATH
    """
    url = f"https://etherscan.io/chart/{series}?output=csv"
    r = requests.get(url, headers={"User-Agent": user_agent})
    # save the data to a csv file
    content = r.content
    with open(Path(GLOBAL_DATA_PATH) / f"{series}.csv", "wb") as f:
        f.write(r.content)
    return content


if __name__ == "__main__":
    # download the price for each fiat
    get_csv_from_etherscan(series="gasprice")
    get_csv_from_etherscan(series="etherprice")
