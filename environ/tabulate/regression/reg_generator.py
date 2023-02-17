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
from matplotlib import pyplot as plt
from stargazer.stargazer import Stargazer
from environ.utils.config_parser import Config

# ignore the warnings
warnings.filterwarnings("ignore")

# Initialize the config parser
config = Config()

# Initialize the path
TABLE_PATH = config["dev"]["config"]["result"]["TABLE_PATH"]
FIGURE_PATH = config["dev"]["config"]["result"]["FIGURE_PATH"]


def generate_unit_of_account(reg_panel: pd.DataFrame) -> None:
    """
    Generate the unit-of-account regression
    """

    # create a list to store the results
    stargazer_list = []
    stargazer_col_list = []

    # loop through the dependent variables as eigenvector centrality
    for dependent_variable in [
        "${\it EigenCent}^{In}$",
        "${\it EigenCent}^{Out}$",
    ]:
        # record the dependet variables
        stargazer_col_list.append(dependent_variable)
        # set the mcap, cov_gas, cov_eth, dollar_exchange_rate as independent variables
        independent_variables = [
            # "${\it MCap}^{USD}$",
            "${\it CovGas}$",
            "${\it CovETH}$",
            "${\it ExchangeRate}^{USD}$",
        ]

        # run the regression
        model = sm.OLS(
            reg_panel[dependent_variable],
            sm.add_constant(reg_panel[independent_variables]),
            missing="drop",
        ).fit()

        # store the results
        stargazer_list.append(model)

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
    with open(rf"{TABLE_PATH}/unit_of_acct.tex", "w") as to_file:
        to_file.write(stargazer.render_latex())

    # save the table to a html file
    with open(rf"{TABLE_PATH}/unit_of_acct.html", "w") as to_file:
        to_file.write(stargazer.render_html())


def generate_reg(reg_panel: pd.DataFrame) -> None:
    """
    Generage the regression.
    """

    # create a list to store the results
    stargazer_list = []
    stargazer_col_list = []

    # fix the dependent variable
    for dep_variable in [
        "${\it VShare}$",
        "${\it VShare}^{\it In}$",
        "${\it VShare}^{\it Out}$",
    ]:
        dependent_variable = reg_panel[dep_variable]
        # loop through the independent variables
        for eigen in ["${\it EigenCent}^{In}$", "${\it EigenCent}^{Out}$"]:
            for betw in ["${\it BetwCent}^C$", "${\it BetwCent}^V$"]:
                for supply in ["${\it SupplyShare}$", "${\it BorrowShare}$"]:
                    for apy in ["${\it BorrowAPY}^{USD}$", "${\it SupplyAPY}^{USD}$"]:
                        # record the dependet variables
                        stargazer_col_list.append(dep_variable)
                        # create the independent variable
                        independent_variable = reg_panel[
                            [
                                eigen,
                                betw,
                                supply,
                                apy,
                                "${R}^{\it USD}$",
                                "${\it CovGas}$",
                                "${\it CovSP}$",
                                "${\it CovETH}$",
                                "${\it \sigma}^{USD}$",
                                # "${\it MCap}^{USD}$",
                                "${\i Nonstable}$",
                                "${\i IsWETH}$",
                                "${\t GasPrice}$",
                            ]
                        ]
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

    # save the table to a html file
    with open(rf"{TABLE_PATH}/regression_table.html", "w") as to_file:
        to_file.write(stargazer.render_html())

    # save the panel dataset as a csv file
    reg_panel.to_csv(rf"{TABLE_PATH}/regression_panel.csv")


def change_in_r_squared(reg_panel: pd.DataFrame) -> None:
    """
    Function to plot the increase of R square.
    """
    _, ax = plt.subplots(figsize=(16, 9))

    for dependent_variable, d_str in [
        ("${\it VShare}$", "V"),
        ("${\it VShare}^{\it In}$", "VIn"),
        ("${\it VShare}^{\it Out}$", "VOut"),
    ]:
        dependent_variable = reg_panel[dependent_variable]
        # loop through the independent variables
        for betw, betw_str in [
            ("${\it BetwCent}^C$", "BetwC"),
            ("${\it BetwCent}^V$", "BetwV"),
        ]:
            for safe, safe_str in [
                ("beta", "Beta"),
                ("cov_semtiment", "Senti"),
                ("average_return", "Rmean"),
                ("${\it \sigma}^{USD}$", "Vol"),
            ]:
                for eigen, eigen_str in [
                    ("${\it EigenCent}^{In}$", "EigenIn"),
                    ("${\it EigenCent}^{Out}$", "EigenOut"),
                ]:
                    r_list = []
                    # graduatelly add the independent variables
                    independent_variable = reg_panel[[safe]]
                    independent_variable = sm.add_constant(independent_variable)
                    model = sm.OLS(
                        dependent_variable, independent_variable, missing="drop"
                    )
                    # calculate the R square
                    r_list.append(model.fit().rsquared)

                    independent_variable = reg_panel[[safe, betw]]
                    independent_variable = sm.add_constant(independent_variable)
                    model = sm.OLS(
                        dependent_variable, independent_variable, missing="drop"
                    )
                    # calculate the R square
                    r_list.append(model.fit().rsquared)

                    independent_variable = reg_panel[[safe, betw, eigen]]
                    independent_variable = sm.add_constant(independent_variable)
                    model = sm.OLS(
                        dependent_variable, independent_variable, missing="drop"
                    )
                    # calculate the R square
                    r_list.append(model.fit().rsquared)

                    # Plot numerous changes in R square in one graph using subplots
                    ax.plot(
                        [
                            "Safe",
                            "Safe + " + "Betw",
                            "Safe + " + "Betw" + " + " + "Eigen",
                        ],
                        r_list,
                        label=f"{d_str}~{betw_str}+{safe_str}+{eigen_str}",
                    )
                    ax.set_title("Change in R square")
                    ax.set_xlabel("Independent Variables")
                    ax.set_ylabel("R square")
    # show the legend in the right hand side of the graph in one column
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.5), ncol=1)

    # save the figure
    plt.savefig(
        rf"{FIGURE_PATH}/R_square.pdf",
        dpi=300,
        bbox_inches="tight",
    )
