"""

University College London
Project : defi_econ
Topic   : reg_generator.py
Author  : Yichen Luo
Date    : 2023-02-06
Desc    : Generate the regression.

"""

import warnings
import pandas as pd
import statsmodels.api as sm
from stargazer.stargazer import Stargazer
from environ.utils.config_parser import Config

# ignore the warnings
warnings.filterwarnings("ignore")

# Initialize the config parser
config = Config()

# Initialize the path
TABLE_PATH = config["dev"]["config"]["result"]["TABLE_PATH"]


def generate_reg(reg_panel: pd.DataFrame) -> None:
    """
    Generage the regression.
    """

    # dependent_variable = reg_panel["${\it VShare}$"]

    # independent_variable_1 = reg_panel[
    #     ["${\it EigenCent}^{In}$", "${\it BetwCent}^C$", "${\it SupplyShare}$"]
    # ]

    # independent_variable_1 = sm.add_constant(independent_variable_1)

    # model_1 = sm.OLS(dependent_variable, independent_variable_1, missing="drop")

    # # fit the model_1
    # results_1 = model_1.fit()

    # independent_variable_2 = reg_panel[
    #     ["${\it EigenCent}^{Out}$", "${\it BetwCent}^V$", "${\it SupplyShare}$"]
    # ]

    # independent_variable_2 = sm.add_constant(independent_variable_2)

    # model_2 = sm.OLS(dependent_variable, independent_variable_2, missing="drop")

    # # fit the model_2
    # results_2 = model_2.fit()

    # create a list to store the results
    stargazer_list = []
    stargazer_col_list = []

    # fix the dependent variable
    for dependent_variable in [
        "${\it VShare}$",
        "${\it VShare}^{\it In}$",
        "${\it VShare}^{\it Out}$",
    ]:
        dependent_variable = reg_panel[dependent_variable]
        # loop through the independent variables
        for eigen in ["${\it EigenCent}^{In}$", "${\it EigenCent}^{Out}$"]:
            for betw in ["${\it BetwCent}^C$", "${\it BetwCent}^V$"]:
                for supply in ["${\it SupplyShare}$", "${\it BorrowShare}$"]:
                    for apy in ["${\it BorrowAPY}^{USD}$", "${\it SupplyAPY}^{USD}$"]:
                        # record the dependet variables
                        stargazer_col_list.append(eigen)

                        # create the independent variable
                        independent_variable = reg_panel[[eigen, betw, supply, apy]]
                        independent_variable = sm.add_constant(independent_variable)
                        model = sm.OLS(
                            dependent_variable, independent_variable, missing="drop"
                        )

                        # store the results
                        stargazer_list.append(model.fit())

        # use stargazer to create the regression table
        # stargazer = Stargazer([results_1, results_2])
        stargazer = Stargazer(stargazer_list)

        # set the title of the table
        stargazer.title("Simple Linear Regression")

        # customize the column name
        stargazer.custom_columns(
            stargazer_col_list,
            [1 for _ in stargazer_col_list],
        )

        # save the table to a latex file
        with open(rf"{TABLE_PATH}/regression_table.tex", "w") as to_file:
            to_file.write(stargazer.render_latex())

    # save the panel dataset as a csv file
    reg_panel.to_csv(rf"{TABLE_PATH}/regression_panel.csv")
