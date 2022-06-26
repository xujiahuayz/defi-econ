import requests

"""# Query Function"""

http_v2 = 'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2'
http_v3 = 'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3'

def run_query(http, query_scripts):
    # endpoint where you are making the request
    request = requests.post(http,
                            '',
                            json={'query': query_scripts})
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception('Query failed. return code is {}.      {}'.format(request.status_code, query_scripts))

def run_query_var(http, query_scripts, var):
    # endpoint where you are making the request
    request = requests.post(http,
                            '',
                            json={'query': query_scripts, 'variables': var})
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception('Query failed. return code is {}.      {}'.format(request.status_code, query_scripts))
