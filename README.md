# distance-to-default-calculation-and-trading-strategies
Python code for calculating the Merton model distance-to-default, including interactions with SQL server to extract the raw data.
Distance-to-default is a measure of default risk. For a comprehensive discussion including calculation methodology and applications to equity markets refer to Vassalou and Xing (2004)[^1][^2].

The file db_interactions_for_DD.py uses pyodbc and pandas in functions that connect to a SQL Server database and extract the required data. This data includes balance sheet data, risk-free interest rates and market values.

The file distance_to_default.py calls the functions in script 1 and performs the necessary calculations for each stock in the cross-section, at yearly intervals from 2000 to 2012 (the extent of the data available to the author).

[^1]: Vassalou, M. and Y. Xing (2004). "Default Risk in Equity Returns." The Journal of finance (New York) 59(2): 831-868.
[^2]: However, note that the conclusions of Vassalou and Xing (2004) regarding the pricing of default risk in equity markets are somewhat contrary to the majority of studies in this area.
