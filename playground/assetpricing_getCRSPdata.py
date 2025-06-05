from sqlalchemy import create_engine
import pandas as pd

WRDS_username = 'placeholder'
WRDS_password = 'password'

# Define the connection string (replace 'username' and 'pw' with your credentials)
connection_string = (
    "postgresql+psycopg2://"
    f"{WRDS_username}:{WRDS_password}"
    "@wrds-pgdata.wharton.upenn.edu:9737/wrds"
)

# Create the SQLAlchemy engine with pre-ping enabled
engine = create_engine(connection_string, pool_pre_ping=True)

# Define the date range for your query (adjust as needed)
start_date = '2010-01-01'
end_date = '2024-01-01'

# SQL query to extract the desired fields for the specified subset of stocks
query = f"""
SELECT d.date, d.permno, d.prc, d.vol, d.ret, d.shrout
FROM crsp.dsf d
JOIN crsp_a_indexes.dsp500list_v2 s
  ON d.permno = s.permno
WHERE d.date BETWEEN '{start_date}' AND '{end_date}'
  AND d.date BETWEEN s.mbrstartdt AND s.mbrenddt
"""

# Execute the query and parse the 'date' column as datetime
stocks = pd.read_sql(query, engine, parse_dates=['date'])
stocks.to_csv('CRSP_data.csv', index=False)