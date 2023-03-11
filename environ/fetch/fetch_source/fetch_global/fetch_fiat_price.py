"""
download fiat price from yahoo finance
"""


import requests
from environ.constants import GLOBAL_DATA_PATH, FIAT_LIST

# google what is my user agent to get it
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"


def get_fiat_usd_price(
    fiat: str,
    start: int = 1547020367,
    end: int = 1678000000,
    user_agent: str = USER_AGENT,
) -> str:
    """
    download fiat price from yahoo finance to csv file in GLOBAL_DATA_PATH
    """
    # https://query1.finance.yahoo.com/v7/finance/download/SGDUSD=X?period1=1547020367&period2=1678000000&interval=1d
    url = f"https://query1.finance.yahoo.com/v7/finance/download/{fiat}USD=X?period1={start}&period2={end}&interval=1d"
    # use requests to download the data
    r = requests.get(url, headers={"User-Agent": user_agent})
    # save the data to a csv file
    with open(f"{GLOBAL_DATA_PATH}/{fiat}_price.csv", "wb") as f:
        f.write(r.content)
    return url


if __name__ == "__main__":
    # download the price for each fiat
    for fiat in FIAT_LIST:
        if fiat != "USD":
            get_fiat_usd_price(fiat)
