import pandas as pd
import linearmodels as lm
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

# Read in data
df = pd.read_csv(
    "https://raw.githubusercontent.com/LOST-STATS/LOST-STATS.github.io/master/Model_Estimation/Data/Event_Study_DiD/bacon_example.csv"
)

# create the lag/lead for treated states
# fill in control obs with 0
# This allows for the interaction between `treat` and `time_to_treat` to occur for each state.
# Otherwise, there may be some missingss and the estimations will be off.
df["time_to_treat"] = (
    df["_nfd"].sub(df["year"]).fillna(0).map(lambda x: str(int(x)).replace("-", "m"))
)


# Create our interactions by hand,
# skipping -1, the last one before treatment

df = (
    # returns dataframe with dummy columns in place of the columns
    # in the named argument, all other columns untouched
    pd.get_dummies(df, columns=["time_to_treat"], prefix="INX", prefix_sep="_")
    # get_dummies has a `drop_first` argument, but if we want to
    # refer to a specific level, we should return all levels and
    # drop out reference column manually
    .drop(columns="INX_m1")
    # Set our individual and time (index) for our data
    .set_index(["stfips", "year"])
)

# Estimate the regression

scalars = ["pcinc", "asmrh", "cases"]
factors = df.columns[df.columns.str.contains("INX")]
exog = factors.union(scalars)
endog = "asmrs"

# with the standard api:
mod = lm.PanelOLS(df[endog], df[exog], entity_effects=True, time_effects=True)
fit = mod.fit(cov_type="clustered", cluster_entity=True)
fit.summary

# with the formula api:
# We can save ourselves some time by creating the regression formula automatically
inxnames = df.columns[range(13, df.shape[1])]
formula = "{} ~ {} + EntityEffects + TimeEffects".format(endog, "+".join(exog))

mod = lm.PanelOLS.from_formula(formula, df)

# Specify clustering when we fit the model
clfe = mod.fit(cov_type="clustered", cluster_entity=True)

# Look at regression results
clfe.summary


# Get coefficients and CIs
res = pd.concat([clfe.params, clfe.std_errors], axis=1)
# Scale standard error to 95% CI
res["ci"] = res["std_error"] * 1.96

# We only want time interactions
res = res.filter(like="INX", axis=0)
# Turn the coefficient names back to numbers
res.index = (
    res.index.str.replace("INX_", "")
    .str.replace("m", "-")
    .astype("int")
    .rename("time_to_treat")
)

# And add our reference period back in, and sort automatically
res.reindex(range(res.index.min(), res.index.max() + 1)).fillna(0)

# Plot the estimates as connected lines with error bars

ax = res.plot(
    y="parameter",
    yerr="ci",
    xlabel="Time to Treatment",
    ylabel="Estimated Effect",
    legend=False,
)
# Add a horizontal line at 0
ax.axhline(0, linestyle="dashed")
# And a vertical line at the treatment time
# some versions of pandas have bug return x-axis object with data_interval
# starting at 0. In that case change 0 to 21
ax.axvline(0, linestyle="dashed")
