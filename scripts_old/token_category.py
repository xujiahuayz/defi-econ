# -*- coding: utf-8 -*-
"""
Label the categories of tokens
"""

## Note for query: Please check from the local dictionary fisrt, then do query if necessary, to avoid the expensive query credits of keys
## Note for save: Please save the results to the local dictionary after your query, then we can re-use it

import coinmarketcapapi


def token_categories(token_ticker: str) -> dict:
    """
    Input the token ticker (e.g. "USDC", "BTC"), query the token info from coinmarketcap, and distinguish labels
    """

    # create instance of coinmarketcap api with "YOUR KEY"
    cmc = coinmarketcapapi.CoinMarketCapAPI("ca2f0d42-8524-4fae-8712-106fcab95ee5")

    # query token info
    token_info = cmc.cryptocurrency_info(symbol=token_ticker)

    # get token tags from token info
    token_tags = token_info.data[token_ticker][0]["tags"]

    categories = ["stablecoin", "governance", "payments"]

    labels = []
    for category in categories:
        label = int(category in token_tags)
        labels.append(label)

    return dict(zip(categories, labels))


if __name__ == "__main__":
    # MVP
    token = "MKR"
    token_categories_labels = token_categories(token)
    print("------Token Categories of " + token + " ------")
    print(token_categories_labels)
