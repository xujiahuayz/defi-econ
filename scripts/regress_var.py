import numpy as np
import pandas as pd

np.random.seed(123)

# Generate some example data
nobs = 100
y1 = np.cumsum(np.random.randn(nobs))
y2 = np.cumsum(np.random.randn(nobs))

# Combine the variables into a DataFrame
data = pd.DataFrame({"y1": y1, "y2": y2})

from statsmodels.tsa.api import VAR

# Estimate a VAR model with lag 2
model = VAR(data)
results = model.fit(2)

results.summary()

# Print the lag coefficients
print(results.coefs)


import statsmodels.api as sm

# lagged y1
data["y1_lag1"] = data["y1"].shift(1)
data["y1_lag2"] = data["y1"].shift(2)
# lagged y2
data["y2_lag1"] = data["y2"].shift(1)
data["y2_lag2"] = data["y2"].shift(2)
data["const"] = 1

# Run OLS regressions separately
ols_y1 = sm.OLS(
    data["y1"],
    data[["const", "y1_lag1", "y1_lag2", "y2_lag1", "y2_lag2"]],
    missing="drop",
)
results_y1 = ols_y1.fit()
results_y1.summary()
