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
import numpy as np
import statsmodels.api as sm
from matplotlib import pyplot as plt
from stargazer.stargazer import Stargazer
from environ.constants import (
    FIGURE_PATH,
    TABLE_PATH,
    NAMING_DIC_HERFINDAHL_LAG,
    NAMING_DIC_PROPERTIES_OF_DOMINANCE_LAG,
    NAMING_DIC_SPECIFICATION_LAG,
)

# ignore the warnings
warnings.filterwarnings("ignore")


def generate_regression_specification(reg_panel: pd.DataFrame, lag: bool) -> None:
    """
    Function to generate the regression of specification
    """

    # sort the panel by "Token", "Date"
    reg_panel = reg_panel.sort_values(by=["Token", "Date"], ascending=True)

    # loop through the status
    for status in ["boom", "bust", "full"]:

        # define the subsample
        reg_subsample = reg_panel.copy()

        # if the status is boom, set all bust data to nan
        # if the status is bust, set all boom data to nan
        if status == "boom":
            reg_subsample.loc[reg_subsample["${\t DeFibust}$"] == 1, :] = np.nan
        elif status == "bust":
            reg_subsample.loc[reg_subsample["${\t DeFiboom}$"] == 1, :] = np.nan
        else:
            pass

        # create a list to store the results
        stargazer_list = []
        stargazer_col_list = []

        # loop through the dependent variables as eigenvector centrality
        for dependent_variable in [
            "${\it AvgEigenCent}$",
            "${\it EigenCent}^{In}$",
            "${\it EigenCent}^{Out}$",
            "${\it BetwCent}^C$",
            "${\it BetwCent}^V$",
            "${\it VShare}$",
            "${\it VShare}^{\it In}$",
            "${\it VShare}^{\it Out}$",
        ]:
            for stability in [
                "${\i Stable}$",
                "${\it DepeggingDegree}$",
                "${\it DepeggingDegree}^{Uppeg}$",
                "${\it PeggingDegree}^{Uppeg}$",
                "${\it StableShare}$",
            ]:
                for financial_service in [
                    "${\it CorrETH}$",
                    "${\it CorrSP}$",
                ]:
                    for heding in [
                        "${\it CorrGas}$",
                    ]:
                        # record the dependet variables
                        stargazer_col_list.append(dependent_variable)
                        independent_variables = [
                            "${\it \sigma}^{USD}$",
                            stability,
                            financial_service,
                            heding,
                            "${\it SupplyShare}$",
                            "${\it MCapShare}$",
                        ]

                        reg_list = [
                            "Date",
                            "Token",
                            dependent_variable,
                            "${\it \sigma}^{USD}$",
                            stability,
                            financial_service,
                            heding,
                            "${\it MCapShare}$",
                        ]

                        if (stability == "${\it DepeggingDegree}$") | (
                            stability == "${\it DepeggingDegree}^{Uppeg}$"
                        ):
                            reg_list.append("${\i Stable}$")
                            independent_variables.append("${\i Stable}$")

                        # isolate the data for the regression and drop the missing values
                        processed_panel = reg_subsample[reg_list].dropna().copy()

                        # create the dummy variables
                        dummy_vars = pd.get_dummies(
                            processed_panel["Token"], drop_first=True
                        )

                        # add the dummy variables to the data
                        processed_panel = pd.concat(
                            [processed_panel, dummy_vars], axis=1
                        )

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
                            ).shift(7)
                            # rename the columns
                            independent_variables = independent_variables.rename(
                                columns=NAMING_DIC_SPECIFICATION_LAG
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
        with open(
            rf"{TABLE_PATH}/regression_specification_{status}.tex", "w"
        ) as to_file:
            to_file.write(stargazer.render_latex())

        # save the table to a html file
        with open(
            rf"{TABLE_PATH}/regression_specification_{status}.html", "w"
        ) as to_file:
            to_file.write(stargazer.render_html())

        reg_panel.to_csv(rf"{TABLE_PATH}/regression_panel.csv")


def generate_regression_herfindahl(
    herfindahl: pd.DataFrame, lag: bool, standardized: bool
) -> None:
    """
    Generate the regression of herfindahl
    """
    # sort the series by "Date"
    herfindahl = herfindahl.sort_values(by=["Date"], ascending=True)

    reg_herfindahl = herfindahl.copy()

    # create a list to store the results
    stargazer_list = []
    stargazer_col_list = []

    # dataframe to store the standardized coefficients
    standardized_coefficient_df = pd.DataFrame()

    # loop through the dependent variables as eigenvector centrality
    for dependent_variable in [
        "${\t HHIVolume}$",
        "${\t HHIBetwCent}^C$",
        "${\t HHIBetwCent}^V$",
        "${\t HHITVL}$",
    ]:

        # record the dependet variables
        stargazer_col_list.append(dependent_variable)
        independent_variables = reg_herfindahl[
            [
                "${\t TotalVolume}$",
                "${\t \sigma}^{USD}_{SP}$",
                "${\t GasPrice}$",
                "${\t \sigma}_{Gas}$",
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
            reg_herfindahl[dependent_variable],
            sm.add_constant(independent_variables),
            missing="drop",
        ).fit()

        if standardized:
            # append the dependent variable to the left of  independent variables
            full_panel = pd.concat(
                [reg_herfindahl[dependent_variable], independent_variables], axis=1
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

    # use stargazer to create the regression table
    stargazer = Stargazer(stargazer_list)

    # set the title of the table
    stargazer.title(f"Regression of Herfindahl")

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


def generate_regression_herfindahl_boom_bust(
    herfindahl: pd.DataFrame, lag: bool, standardized: bool
) -> None:
    """
    Generate the regression of herfindahl
    """
    # sort the series by "Date"
    herfindahl = herfindahl.sort_values(by=["Date"], ascending=True)

    reg_herfindahl = herfindahl.copy()

    # create a list to store the results
    stargazer_list = []
    stargazer_col_list = []

    # dataframe to store the standardized coefficients
    standardized_coefficient_df = pd.DataFrame()

    # list of the independent variables
    list_of_independent_variables = [
        "${\t TotalVolume}$",
        "${\t \sigma}^{USD}_{SP}$",
        "${\t GasPrice}$",
        "${\t \sigma}_{Gas}$",
    ]

    # calculate the interaction term between "DeFiBoom"
    # and variable in list_of_independent_variables
    for var in list_of_independent_variables:
        reg_herfindahl[f"{var} * DeFiBoom"] = (
            reg_herfindahl[var] * reg_herfindahl["${\t DeFiboom}$"]
        )

    # loop through the dependent variables as eigenvector centrality
    for dependent_variable in [
        "${\t HHIVolume}$",
        "${\t HHIBetwCent}^C$",
        "${\t HHIBetwCent}^V$",
        "${\t HHITVL}$",
    ]:

        # record the dependet variables
        stargazer_col_list.append(dependent_variable)
        independent_variables = reg_herfindahl[
            [f"{var} * DeFiBoom" for var in list_of_independent_variables]
            + ["${\t DeFiboom}$"]
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
            reg_herfindahl[dependent_variable],
            sm.add_constant(independent_variables),
            missing="drop",
        ).fit()

        if standardized:
            # append the dependent variable to the left of  independent variables
            full_panel = pd.concat(
                [reg_herfindahl[dependent_variable], independent_variables], axis=1
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

    # use stargazer to create the regression table
    stargazer = Stargazer(stargazer_list)

    # set the title of the table
    stargazer.title(f"Regression of Herfindahl")

    # customize the column name
    stargazer.custom_columns(
        stargazer_col_list,
        [1 for _ in stargazer_col_list],
    )

    # save the table to a latex file
    with open(rf"{TABLE_PATH}/regression_herfindahl_boom_bust.tex", "w") as to_file:
        to_file.write(stargazer.render_latex())

    # save the table to a html file
    with open(rf"{TABLE_PATH}/regression_herfindahl_boom_bust.html", "w") as to_file:
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
            "${\it CorrGas}$",
            "${\it CorrETH}$",
            "${\it ExchangeRate}^{USD}$",
            "${\it MCapShare}$",
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

    # # save the panel dataset as a csv file
    # reg_panel.to_csv(rf"{TABLE_PATH}/regression_panel.csv")


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
