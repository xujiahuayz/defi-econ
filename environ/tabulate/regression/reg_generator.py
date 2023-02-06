"""

University College London
Project : defi_econ
Topic   : reg_generator.py
Author  : Yichen Luo
Date    : 2023-02-06
Desc    : Generate the regression.

"""

import pandas as pd
import statsmodels.api as sm
from stargazer.stargazer import Stargazer
from environ.utils.config_parser import Config

# Initialize the config parser
config = Config()

# Initialize the path
TABLE_PATH = config["dev"]["config"]["data"]["TABLE_PATH"]


def generate_reg(reg_panel: pd.DataFrame) -> None:
    """
    Generage the regression.
    """

    dependent_variable = reg_panel["${\it VShare}$"]

    independent_variable_1 = reg_panel[
        ["${\it EigenCent}^{In}$", "${\it BetwCent}^C$", "${\it SupplyShare}$"]
    ]

    independent_variable_1 = sm.add_constant(independent_variable_1)

    model_1 = sm.OLS(dependent_variable, independent_variable_1, missing="drop")

    # fit the model_1
    results_1 = model_1.fit()

    independent_variable_2 = reg_panel[
        ["${\it EigenCent}^{Out}$", "${\it BetwCent}^V$", "${\it SupplyShare}$"]
    ]

    independent_variable_2 = sm.add_constant(independent_variable_2)

    model_2 = sm.OLS(dependent_variable, independent_variable_2, missing="drop")

    # fit the model_1
    results_2 = model_2.fit()

    # use stargazer to create the regression table
    stargazer = Stargazer([results_1, results_2])

    # set the title of the table
    stargazer.title("Simple Linear Regression")

    # customize the column name
    stargazer.custom_columns(["${\it VShare}$", "${\it VShare}$"], [1, 1])

    # save the table to a latex file
    with open(rf"{TABLE_PATH}/regression_table.tex", "w") as to_file:
        to_file.write(stargazer.render_latex())

    # save the panel dataset as a csv file
    reg_panel.to_csv(rf"{TABLE_PATH}/regression_panel.csv")
