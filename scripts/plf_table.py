import pandas as pd
from environ.constants import COMPOUND_DEPLOYMENT_DATE, AAVE_DEPLOYMENT_DATE, TABLE_PATH


for k, v in {
    "Compound": COMPOUND_DEPLOYMENT_DATE,
    "Aave": AAVE_DEPLOYMENT_DATE,
}.items():

    plf_table = pd.DataFrame(v)
    plf_table.columns = [
        "Token",
        "Lending pool smart contract",
        f"Time added to {k} [UTC]",
    ]

    # change smart contract column to be a link to etherscan
    plf_table["Lending pool smart contract"] = plf_table[
        "Lending pool smart contract"
    ].apply(lambda x: f"\\href{{https://etherscan.io/address/{x}}}{{\\tt {x}}}")

    # make latex table and ensure that the smart contract column is not escaped and shown in full
    with pd.option_context("max_colwidth", 1000):
        plf_table.to_latex(
            TABLE_PATH / f"{k}_table.tex",
            escape=False,
            index=False,
        )
