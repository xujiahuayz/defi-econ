# -*- coding: utf-8 -*-


import pandas as pd
import requests

def get_token_list(token_address=[]): 
  url_ctoken_service = 'https://api.compound.finance/api/v2/ctoken'
  fetch_all_tokens = {
      "addresses": token_address,
      "block_timestamp": 0
  }

  query_all_tokens = requests.get(url = url_ctoken_service, params=fetch_all_tokens)
  query_all_tokens = query_all_tokens.json()

  token_list = pd.DataFrame(columns=['name', 'symbol', 'token_address', 'underlying_symbol', 'underlying_address'])
  for i in range(len(query_all_tokens['cToken'])):
    token_info = pd.DataFrame({
        'name': [query_all_tokens['cToken'][i]['name']],
        'symbol': [query_all_tokens['cToken'][i]['symbol']],
        'token_address': [query_all_tokens['cToken'][i]['token_address']],
        'underlying_symbol': [query_all_tokens['cToken'][i]['underlying_symbol']],
        'underlying_address': [query_all_tokens['cToken'][i]['underlying_address']]
    })
    token_list = pd.concat([token_list, token_info], ignore_index = True, axis = 0)

  return token_list

df_compound_tokens = get_token_list()
df_compound_tokens

df_compound_tokens.to_csv("data_compound/all_compound_tokens.csv")