import pandas as pd
from environ.constants import COMPOUND_DEPLOYMENT_DATE, TABLE_PATH

compound_table = pd.DataFrame(COMPOUND_DEPLOYMENT_DATE)
compound_table.columns = [
    "Token",
    "Lending pool smart contract",
    "Time added to Compound [UTC]",
]

# change smart contract column to be a link to etherscan
compound_table["Lending pool smart contract"] = compound_table[
    "Lending pool smart contract"
].apply(lambda x: f"\\href{{https://etherscan.io/address/{x}}}{{\\tt {x}}}")

# make latex table and ensure that the smart contract column is not escaped and shown in full
with pd.option_context("max_colwidth", 1000):
    compound_table.to_latex(
        TABLE_PATH / "compound_table.tex",
        escape=False,
        index=False,
    )
