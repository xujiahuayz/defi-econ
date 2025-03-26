import pandas as pd
import statsmodels.formula.api as smf
from environ.constants import (
    DEPENDENT_VARIABLES,
    DEPENDENT_VARIABLES_ASSETPRICING,
    PROCESSED_DATA_PATH,
    TABLE_PATH,
    QUANTILES,
)

from environ.process.asset_pricing.assetpricing_functions import (
    clean_weekly_panel,
    univariate_sort,
    get_dominance_portfolios,
    significance_stars,
)


if __name__ == "__main__":
    factor_models = ["MKT", "CMKT", "CMKT+CMOM+CSIZE"]
    factor_models_names = ["MKT", "CMKT", "LTW3"]
    factor_dict = dict(zip(factor_models, factor_models_names))
    is_boom = -1
    ret_agg = "value_weight"

    # load factors
    ff3 = pd.read_csv(PROCESSED_DATA_PATH / "FF3.csv")
    ltw3 = pd.read_csv(PROCESSED_DATA_PATH / "LTW3.csv")

    # load the regression panel dataset
    reg_panel = pd.read_pickle(
        PROCESSED_DATA_PATH / "panel_main.pickle.zip", compression="zip"
    )

    for factor_model in factor_models:
        for dom_variable in DEPENDENT_VARIABLES_ASSETPRICING:
            # 1. Prepare your data
            quantiles = QUANTILES
            df_panel = clean_weekly_panel(reg_panel, is_stablecoin=0, is_boom=is_boom)
            df_panel = df_panel[df_panel[dom_variable] > 0]
            df_panel = univariate_sort(
                df_panel,
                dom_variable,
                quantiles,
                separate_zero_value=False,
            )
            dominance_portfolios = get_dominance_portfolios(df_panel, ret_agg=ret_agg)
            dominance_portfolios.rename(
                columns={dominance_portfolios.columns[-1]: "CDOM"}, inplace=True
            )
            portfolios = list(dominance_portfolios.columns)

            # 2. Merge all factors into a single DataFrame
            factors_data = pd.merge(
                dominance_portfolios, ff3, on=["WeekYear"], how="left"
            )
            factors_data = pd.merge(factors_data, ltw3, on=["WeekYear"], how="left")
            for p in portfolios:
                factors_data[p] = factors_data[p] - factors_data["RF"]
            # 3. Build a list of factor names from the formula (plus "alpha")
            #    Example: factor_model="MKT + SMB + HML" => ["MKT", "SMB", "HML"]
            #    We'll store "alpha" and then each factor, plus a matching "_t" row for t-stats
            raw_factors = factor_model.replace(" ", "").split("+")
            factor_names = ["alpha"] + raw_factors  # "alpha" is the renamed Intercept
            row_list = []
            for f in factor_names:
                row_list.append(f)  # e.g. "alpha", "MKT", "SMB", ...
                row_list.append(f"{f}_t")  # e.g. "alpha_t", "MKT_t", ...

            # Finally, add R-squared and N at the bottom
            row_list += ["R-squared", "N"]
            final_table = pd.DataFrame(index=row_list, columns=portfolios)

            # 4. Run a separate regression for each portfolio
            for p in portfolios:
                formula = f"{p} ~ {factor_model}"

                # Use Newey–West (HAC) standard errors
                model = smf.ols(formula=formula, data=factors_data).fit(
                    cov_type="HAC", cov_kwds={"maxlags": 4}
                )

                # Extract estimates, t-stats, p-values
                coefs = model.params.copy()
                tvals = model.tvalues.copy()
                pvals = model.pvalues.copy()

                # Rename "Intercept" to "alpha"
                if "Intercept" in coefs.index:
                    coefs.rename({"Intercept": "alpha"}, inplace=True)
                    tvals.rename({"Intercept": "alpha"}, inplace=True)
                    pvals.rename({"Intercept": "alpha"}, inplace=True)

                # Fill each factor row with the coefficient and the next row with the t-stat
                for f in factor_names:
                    if f in coefs.index:
                        star = significance_stars(pvals[f])

                        # Row for coefficient (with stars)
                        final_table.loc[f, p] = f"{coefs[f]:.4f}{star}"

                        # Row for p-value
                        # final_table.loc["p", p] = f"({pvals[f]:.2f})"

                        # Row for t-stat
                        final_table.loc[f"{f}_t", p] = f"({tvals[f]:.2f})"
                    else:
                        # If factor not found in the regression, fill with blanks or zeros
                        final_table.loc[f, p] = ""
                        final_table.loc[f"{f}_t", p] = ""

                # Fill in R-squared and # obs
                final_table.loc["R-squared", p] = f"{model.rsquared:.3f}"
                final_table.loc["N", p] = f"{int(model.nobs)}"

            # 5. Print or export the final table
            print(f"== Results for {dom_variable} | Model: {factor_model} ")
            file_name = (
                TABLE_PATH
                / "assetpricing"
                / f"assetpricing_factortesting_{dom_variable}_{factor_dict[factor_model]}"
            )
            final_table.to_latex(
                f"{file_name}.tex",
                index=True,
                escape=False,
            )
