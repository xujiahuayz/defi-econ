import pandas as pd
from environ.constants import TABLE_PATH
from environ.plot.plot_ma import preprocess_ma, plot_time_series


regression_panel = pd.read_pickle(TABLE_PATH / "reg_panel.pkl")

ma_df = preprocess_ma(df=regression_panel, value_colume="Volume_share", ma_window=30)
plot_time_series(ma_df)
