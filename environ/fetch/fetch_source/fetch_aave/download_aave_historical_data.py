# -*- coding: utf-8 -*-
"""
Download the historical data for AAVE from Dune Analytics
Note: Dune account and password need to be filled
"""

from os import path
import pandas as pd
from tqdm import tqdm
from duneanalytics import DuneAnalytics
from environ.utils.config_parser import Config


def download_dune_data(dune_id: int) -> dict:
    """
    download dune data by the given dune id, example: https://dune.com/queries/4494/8769 => 4494
    """

    # initialize configuration
    config = Config()

    # initialize client
    dune = DuneAnalytics(
        config["dev"]["config"]["aave"]["DUNE_ACCOUNT"],
        config["dev"]["config"]["aave"]["DUNE_PASSWORD"],
    )

    # try to login
    dune.login()

    # fetch token
    dune.fetch_auth_token()

    # fetch query result id using query id
    # query id for any query can be found from the url of the query:
    # for example:
    # https://dune.com/queries/4494/8769 => 4494
    # https://dune.com/queries/3705/7192 => 3705
    # https://dune.com/queries/3751/7276 => 3751

    result_id = dune.query_result_id(query_id=dune_id)

    # fetch query result
    data = dune.query_result(result_id)

    # filter the raw result
    result_dict = data["data"]["get_result_by_result_id"]

    return result_dict


def fetch_aave_historical_data() -> None:

    """
    Fetch AAVE historical data.
    """

    # initialize configuration
    config = Config()

    # data source: https://dune.com/queries/589140/1100732 (top asset, instant)
    # data source: https://dune.com/queries/575705/1082614 (all asset)
    result_dict = download_dune_data(575705)

    # Initialize the dataframe for storing the result from dictionary
    df_result = pd.DataFrame()

    # read the result dict row by row
    for index in tqdm(range(len(result_dict))):
        new_entity = pd.DataFrame(result_dict[index]["data"], index=[index])
        df_result = pd.concat([df_result, new_entity], ignore_index=True, axis=0)

    # reorder the column
    # df_result = df_result[["day", "symbol", "deposit", "borrow"]]

    file_name = path.join(
        config["dev"]["config"]["data"]["AAVE_DATA_PATH"],
        "aave_all_token_historical_data.csv",
    )
    df_result.to_csv(file_name)
