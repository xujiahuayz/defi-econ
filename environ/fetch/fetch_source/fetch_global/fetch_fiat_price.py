"""
download fiat price from yahoo finance
"""

from pathlib import Path

import requests

from environ.constants import FIAT_LIST, GLOBAL_DATA_PATH, USER_AGENT


def get_fiat_usd_price(
    fiat: str,
    start: int = 1547020367,
    end: int = 1678000000,
    user_agent: str = USER_AGENT,
) -> str:
    """
    download fiat price from yahoo finance to csv file in GLOBAL_DATA_PATH
    """
    url = f"https://query1.finance.yahoo.com/v7/finance/download/{fiat}USD=X?period1={start}&period2={end}&interval=1d"
    # use requests to download the data
    r = requests.get(url, headers={"User-Agent": user_agent})
    # save the data to a csv file
    with open(Path(GLOBAL_DATA_PATH) / f"{fiat}_price.csv", "wb") as f:
        f.write(r.content)
    return url


if __name__ == "__main__":
    # download the price for each fiat
    for fiat in FIAT_LIST:
        if fiat != "USD":
            get_fiat_usd_price(fiat)
