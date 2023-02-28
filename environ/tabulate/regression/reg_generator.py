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

# Initialize constants
NAMING_DIC_PROPERTIES_OF_DOMINANCE_LAG = {
    # Dominance
    "${\it VShare}$": "${\it-1 VShare}$",
    "${\it VShare}^{\it In}$": "${\it-1 VShare}^{\it-1 In}$",
    "${\it VShare}^{\it Out}$": "${\it-1 VShare}^{\it-1 Out}$",
    # Eigenvector
    "${\it EigenCent}^{In}$": "${\it-1 EigenCent}^{In}$",
    "${\it EigenCent}^{Out}$": "${\it-1 EigenCent}^{Out}$",
    # Betweenness
    "${\it BetwCent}^C$": "${\it-1 BetwCent}^C$",
    "${\it BetwCent}^V$": "${\it-1 BetwCent}^V$",
    # Store
    "${\it BorrowShare}$": "${\it-1 BorrowShare}$",
    "${\it SupplyShare}$": "${\it-1 SupplyShare}$",
    "${\it BorrowAPY}^{USD}$": "${\it-1 BorrowAPY}^{USD}$",
    "${\it SupplyAPY}^{USD}$": "${\it-1 SupplyAPY}^{USD}$",
    "${\it Beta}$": "${\it-1 Beta}$",
    "${\it \sigma}^{USD}$": "${\it-1 \sigma}^{USD}$",
    "${\it \mu}^{USD}$": "${\it-1 \mu}^{USD}$",
    # Other
    "${\it CorrGas}$": "${\it-1 CorrGas}$",
    "${\it CorrSP}$": "${\it-1 CorrSP}$",
    "${\it CorrETH}$": "${\it-1 CorrETH}$",
    "${R}^{\it USD}$": "${R}^{\it-1 USD}$",
    "${\it MCap}^{USD}$": "${\it-1 MCap}^{USD}$",
    "${\i Nonstable}$": "${\i Nonstable}$",
    "${\i IsWETH}$": "${\i IsWETH}$",
    "${\t GasPrice}$": "${\t-1 GasPrice}$",
    "${\it ExchangeRate}^{USD}$": "${\it-1 ExchangeRate}^{USD}$",
    "${\it LiquidityShare}$": "${\it-1 LiquidityShare}$",
    "${\it exceedance}^{USD}$": "${\it-1 exceedance}^{USD}$",
    "${\t \sigma}_{Gas}$": "${\t-1 \sigma}_{Gas}$",
    # Drop
    "${\it CorrSent}$": "${\it-1 CorrSent}$",
}

NAMING_DIC_HERFINDAHL_LAG = {
    "${\t HHIVolume}$": "${\t-1 HHIVolume}$",
    "${\t HHIEigenCent}^{In}$": "${\t-1 HHIEigenCent}^{In}$",
    "${\t HHIEigenCent}^{Out}$": "${\t-1 HHIEigenCent}^{Out}$",
    "${\t HHIBetwCent}^C$": "${\t-1 HHIBetwCent}^C$",
    "${\t HHIBetwCent}^V$": "${\t-1 HHIBetwCent}^V$",
    "${\t TotalVolume}$": "${\t-1 TotalVolume}$",
    "${\t R}^{USD}_{SP}$": "${\t-1 R}^{USD}_{SP}$",
    "${\t \sigma}^{USD}_{SP}$": "${\t-1 \sigma}^{USD}_{SP}$",
    "${\t GasPrice}$": "${\t-1 GasPrice}$",
    "${\t \sigma}_{Gas}$": "${\t-1 \sigma}_{Gas}$",
}


def generate_regression_specification(reg_panel: pd.DataFrame, lag: bool) -> None:
    """
    Function to generate the regression of specification
    """

    # sort the panel by "Token", "Date"
    reg_panel = reg_panel.sort_values(by=["Token", "Date"], ascending=True)

    # create a list to store the results
    stargazer_list = []
    stargazer_col_list = []

    # loop through the dependent variables as eigenvector centrality
    for dependent_variable in [
        "${\it EigenCent}^{In}$",
        "${\it EigenCent}^{Out}$",
        "${\it BetwCent}^C$",
        "${\it BetwCent}^V$",
        "${\it LiquidityShare}$",
    ]:
        for stability in [
            "${\it CorrSP}$",
            "${\it \sigma}^{USD}$",
            # "${\it exceedance}^{USD}$",
        ]:
            for financial_service in [
                "${\it BorrowShare}$",
                "${\it SupplyShare}$",
                "${\it BorrowAPY}^{USD}$",
                "${\it SupplyAPY}^{USD}$",
            ]:
                for heding in [
                    "${\it CorrGas}$",
                    "${\it CorrETH}$",
                    "${\t \sigma}_{Gas}$",
                ]:
                    # record the dependet variables
                    stargazer_col_list.append(dependent_variable)
                    independent_variables = [
                        stability,
                        financial_service,
                        heding,
                    ]

                    # isolate the data for the regression and drop the missing values
                    processed_panel = (
                        reg_panel[
                            [
                                "Date",
                                "Token",
                                dependent_variable,
                                stability,
                                financial_service,
                                heding,
                            ]
                        ]
                        .dropna()
                        .copy()
                    )

                    # create the dummy variables
                    dummy_vars = pd.get_dummies(
                        processed_panel["Token"], drop_first=True
                    )

                    # add the dummy variables to the data
                    processed_panel = pd.concat([processed_panel, dummy_vars], axis=1)

                    # set the independent variables equal to the
                    # otal panel minus the dependent variable
                    independent_variables = [
                        var
                        for var in processed_panel.columns
                        if var != dependent_variable
                    ]

                    # independent variables
                    independent_variables = processed_panel[
                        independent_variables
                    ].copy()

                    # lag the independent variables
                    if lag:
                        # one lag of in the group of "Token" and "Date"
                        independent_variables = independent_variables.groupby(
                            ["Token"]
                        ).shift(1)
                        # rename the columns
                        independent_variables = independent_variables.rename(
                            columns=NAMING_DIC_HERFINDAHL_LAG
                        )
                        # drop the column of "Date"
                        independent_variables = independent_variables.drop(
                            columns=["Date"]
                        )
                    else:
                        # drop the column of "Date" and "Token"
                        independent_variables = independent_variables.drop(
                            ["Date", "Token"], axis=1
                        )

                    # run the regression using
                    model = sm.OLS(
                        processed_panel[dependent_variable],
                        independent_variables,
                        missing="drop",
                    ).fit()

                    # store the results
                    stargazer_list.append(model)

    # use stargazer to create the regression table
    stargazer = Stargazer(stargazer_list)

    # set the title of the table
    stargazer.title("Regression of Specification")

    # customize the column name
    stargazer.custom_columns(
        stargazer_col_list,
        [1 for _ in stargazer_col_list],
    )

    # save the table to a latex file
    with open(rf"{TABLE_PATH}/regression_specification.tex", "w") as to_file:
        to_file.write(stargazer.render_latex())

    # save the table to a html file
    with open(rf"{TABLE_PATH}/regression_specification.html", "w") as to_file:
        to_file.write(stargazer.render_html())


def generate_regression_herfindahl(
    herfindahl: pd.DataFrame, lag: bool, standardized: bool
) -> None:
    """
    Generate the regression of herfindahl
    """
    # sort the series by "Date"
    herfindahl = herfindahl.sort_values(by=["Date"], ascending=True)

    # create a list to store the results
    stargazer_list = []
    stargazer_col_list = []

    # dataframe to store the standardized coefficients
    standardized_coefficient_df = pd.DataFrame()

    # loop through the dependent variables as eigenvector centrality
    for dependent_variable in [
        "${\t HHIVolume}$",
        # "${\t HHIEigenCent}^{In}$",
        # "${\t HHIEigenCent}^{Out}$",
        "${\t HHIBetwCent}^C$",
        "${\t HHIBetwCent}^V$",
    ]:

        # record the dependet variables
        stargazer_col_list.append(dependent_variable)
        independent_variables = herfindahl[
            [
                "${\t TotalVolume}$",
                "${\t R}^{USD}_{SP}$",
                "${\t \sigma}^{USD}_{SP}$",
                "${\t GasPrice}$",
                "${\t \sigma}_{Gas}$",
                "${\t DeFiboom}$",
                "${\t DeFibust}$",
            ]
        ].copy()

        if lag:
            # one lag of the independent variable
            independent_variables = independent_variables.shift(1)

            # rename the columns using NAMING_DIC_HERFINDAHL_LAG
            independent_variables = independent_variables.rename(
                columns=NAMING_DIC_HERFINDAHL_LAG
            )

        # run the regression
        model = sm.OLS(
            herfindahl[dependent_variable],
            sm.add_constant(independent_variables),
            missing="drop",
        ).fit()

        if standardized:
            # append the dependent variable to the left of  independent variables
            full_panel = pd.concat(
                [herfindahl[dependent_variable], independent_variables], axis=1
            )

            # drop the missing values
            full_panel = full_panel.dropna()

            # calculate the std of the independent variables
            std_y = full_panel[dependent_variable].std()

            # iterate through sm.add_constant(independent_variables)
            for _, var in enumerate(sm.add_constant(independent_variables)):
                # calculate the std of the independent variables
                std_x = sm.add_constant(independent_variables)[var].std()

                # calculate the standardized coefficient
                standardized_coefficient = model.params[var] * std_x / std_y

                # append the standardized coefficient to the dataframe
                standardized_coefficient_df = standardized_coefficient_df.append(
                    {
                        "Dependent Variable": dependent_variable,
                        "Independent Variable": var,
                        "Standardized Coefficient": standardized_coefficient,
                    },
                    ignore_index=True,
                )

                # # update the coefficient of the independent variables
                # model.params[var] = standardized_coefficient

        # store the results
        stargazer_list.append(model)

    # save the standardized coefficient to a csv file
    if standardized:
        standardized_coefficient_df.to_csv(
            rf"{TABLE_PATH}/standardized_coefficient_herfindahl.csv",
            index=False,
        )

    # use stargazer to create the regression table
    stargazer = Stargazer(stargazer_list)

    # set the title of the table
    stargazer.title("Regression of Herfindahl")

    # customize the column name
    stargazer.custom_columns(
        stargazer_col_list,
        [1 for _ in stargazer_col_list],
    )

    # save the table to a latex file
    with open(rf"{TABLE_PATH}/regression_herfindahl.tex", "w") as to_file:
        to_file.write(stargazer.render_latex())

    # save the table to a html file
    with open(rf"{TABLE_PATH}/regression_herfindahl.html", "w") as to_file:
        to_file.write(stargazer.render_html())


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
            "${\it CorrGas}$",
            "${\it CorrETH}$",
            "${\it ExchangeRate}^{USD}$",
            "${\it MCap}^{USD}$",
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


def generate_reg_property_of_dominance(
    reg_panel: pd.DataFrame, file_name: str, lag: bool
) -> None:
    """
    Generage the regression.
    """

    # sort the data by the date
    reg_panel = reg_panel.sort_values(by=["Token", "Date"], ascending=True)

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
                # for supply in ["${\it SupplyShare}$", "${\it BorrowShare}$"]:
                #     for apy in ["${\it BorrowAPY}^{USD}$", "${\it SupplyAPY}^{USD}$"]:
                for store in ["${\i Nonstable}$", "${\i IsWETH}$"]:
                    # record the dependet variables
                    stargazer_col_list.append(dep_variable)
                    # create the independent variable
                    independent_variable = reg_panel[
                        [
                            "Token",
                            "Date",
                            eigen,
                            betw,
                            store,
                        ]
                    ].copy()

                    if lag:
                        # one lag of in the group of "Token" and "Date"
                        independent_variable = independent_variable.groupby(
                            ["Token"]
                        ).shift(1)
                        # rename the columns using NAMING_DIC_PROPERTIES_OF_DOMINANCE_LAG
                        independent_variable = independent_variable.rename(
                            columns=NAMING_DIC_PROPERTIES_OF_DOMINANCE_LAG
                        )
                        # drop the column of "Date"
                        independent_variable = independent_variable.drop(
                            columns=["Date"]
                        )
                    else:
                        # drop the column of "Date" and "Token"
                        independent_variable = independent_variable.drop(
                            columns=["Date", "Token"]
                        )

                    # add constant
                    independent_variable = sm.add_constant(independent_variable)

                    # run the regression
                    model = sm.OLS(
                        dependent_variable, independent_variable, missing="drop"
                    )

                    # store the results
                    stargazer_list.append(model.fit())

    # use all store proxies
    for dep_variable in [
        "${\it VShare}$",
        "${\it VShare}^{\it In}$",
        "${\it VShare}^{\it Out}$",
    ]:
        dependent_variable = reg_panel[dep_variable]
        # loop through the independent variables
        for eigen in ["${\it EigenCent}^{In}$", "${\it EigenCent}^{Out}$"]:
            for betw in ["${\it BetwCent}^C$", "${\it BetwCent}^V$"]:
                # record the dependet variables
                stargazer_col_list.append(dep_variable)
                # create the independent variable
                independent_variable = reg_panel[
                    [
                        "Token",
                        "Date",
                        eigen,
                        betw,
                        "${\i Nonstable}$",
                        "${\i IsWETH}$",
                    ]
                ].copy()

                if lag:
                    # one lag of in the group of "Token" and "Date"
                    independent_variable = independent_variable.groupby(
                        ["Token"]
                    ).shift(1)
                    # rename the columns using NAMING_DIC_PROPERTIES_OF_DOMINANCE_LAG
                    independent_variable = independent_variable.rename(
                        columns=NAMING_DIC_PROPERTIES_OF_DOMINANCE_LAG
                    )
                    # drop the column of "Date"
                    independent_variable = independent_variable.drop(columns=["Date"])
                else:
                    # drop the column of "Date" and "Token"
                    independent_variable = independent_variable.drop(
                        columns=["Date", "Token"]
                    )

                # add constant
                independent_variable = sm.add_constant(independent_variable)

                # run the regression
                model = sm.OLS(dependent_variable, independent_variable, missing="drop")

                # store the results
                stargazer_list.append(model.fit())

    # use stargazer to create the regression table
    # stargazer = Stargazer([results_1, results_2])
    stargazer = Stargazer(stargazer_list)

    # set the title of the table
    stargazer.title(f"Properties of Dominance: {file_name}")

    # customize the column name
    stargazer.custom_columns(
        stargazer_col_list,
        [1 for _ in stargazer_col_list],
    )

    # save the table to a latex file
    with open(
        rf"{TABLE_PATH}/regression_properties_of_dominance_{file_name}.tex", "w"
    ) as to_file:
        to_file.write(stargazer.render_latex())

    # save the table to a html file
    with open(
        rf"{TABLE_PATH}/regression_properties_of_dominance_{file_name}.html", "w"
    ) as to_file:
        to_file.write(stargazer.render_html())

    # save the panel dataset as a csv file
    reg_panel.to_csv(rf"{TABLE_PATH}/regression_panel.csv")


def realized_holding_period(reg_panel: pd.DataFrame, lag: bool) -> None:
    """
    Function to generate the regression of realized holding period.
    """

    # sort the data by the date
    reg_panel = reg_panel.sort_values(by=["Token", "Date"], ascending=True)

    # create a list to store the results
    stargazer_list = []
    stargazer_col_list = []

    # loop through the dependent variables as eigenvector centrality
    for dependent_variable in ["${R}^{\it USD}$"]:
        # set the mcap, cov_gas, cov_eth, dollar_exchange_rate as independent variables
        for eigen in ["${\it EigenCent}^{In}$", "${\it EigenCent}^{Out}$"]:
            for betw in ["${\it BetwCent}^C$", "${\it BetwCent}^V$"]:
                # record the dependet variables
                stargazer_col_list.append(dependent_variable)
                independent_variables = reg_panel[
                    [
                        "Date",
                        "Token",
                        eigen,
                        betw,
                    ]
                ].copy()

                if lag:
                    # one lag of in the group of "Token" and "Date"
                    independent_variables = independent_variables.groupby(
                        ["Token"]
                    ).shift(1)
                    # rename the columns using NAMING_DIC_PROPERTIES_OF_DOMINANCE_LAG
                    independent_variables = independent_variables.rename(
                        columns=NAMING_DIC_PROPERTIES_OF_DOMINANCE_LAG
                    )
                    # drop the column of "Date"
                    independent_variables = independent_variables.drop(columns=["Date"])
                else:
                    # drop the column of "Date" and "Token"
                    independent_variables = independent_variables.drop(
                        columns=["Date", "Token"]
                    )

                # run the regression
                model = sm.OLS(
                    reg_panel[dependent_variable],
                    sm.add_constant(independent_variables),
                    missing="drop",
                ).fit()

                # store the results
                stargazer_list.append(model)

    # use stargazer to create the regression table
    # stargazer = Stargazer([results_1, results_2])
    stargazer = Stargazer(stargazer_list)

    # set the title of the table
    stargazer.title("Realized Holding Period")

    # customize the column name
    stargazer.custom_columns(
        stargazer_col_list,
        [1 for _ in stargazer_col_list],
    )

    # save the table to a latex file
    with open(rf"{TABLE_PATH}/realized_holding_period.tex", "w") as to_file:
        to_file.write(stargazer.render_latex())

    # save the table to a html file
    with open(rf"{TABLE_PATH}/realized_holding_period.html", "w") as to_file:
        to_file.write(stargazer.render_html())


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
                ("${\it Beta}$", "Beta"),
                ("${\it CorrSent}$", "Senti"),
                ("${\it \mu}^{USD}$", "Rmean"),
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
