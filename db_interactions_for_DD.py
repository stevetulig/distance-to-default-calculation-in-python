"""
Python files to
(i) establish a connection to the Zenith database
(ii) extract necessary data for the distance-to-default calculation and
(iii) store them in pandas dataframes
"""
import pandas as pd
import pyodbc

def connectZenithDb():
    """returns a connection to a local SQL Server database (Zenith)
    using Windows authentication"""
    driver='{ODBC Driver 17 for SQL Server}'
    server='STEVE_XPS\SQLEXPRESS'
    database='Zenith'
    try:
        cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+'; \
                      DATABASE='+database+';Trusted_Connection=yes;')
    except:
        return None            
    return cnxn

def getMarketValues(cnxn, stockid, yr):
    strQry='select MarketCap as Ve from Daily_prices ' + \
        'where StockID=' + str(stockid) + \
        ' and MarketCap>0' + \
        ' and datepart(year,PriceDate)=' + str(yr) + ' order by PriceDate'
    return pd.read_sql(strQry, cnxn)

def getDebt(cnxn, yr):
    # returns the value of X = CL + NCL/2 for every company in rebalance year yr
    strQry='select a.StockID, b.ItemValue' + \
        ' from financialRefDates a inner join Debt_x b ' + \
        'on a.StockID=b.StockID and b.ReportMonth=month(a.reportDate) ' + \
        'and b.ReportYear=year(a.reportDate) ' + \
        'where year(a.rebalanceDate)=' + str(yr)
    return pd.read_sql(strQry, cnxn)
    
def getRf(cnxn, yr, mnth):
    # returns the 6-month BAB rate as a proxy for the risk-free rate
    strQry='select BAB_rate from rba_monthly_bab_rates where PriceDate=(' + \
        'select max(Pricedate) from rba_monthly_bab_rates '  \
            'where year(PriceDate)='+str(yr) + \
                'and month(PriceDate)='+str(mnth)+')'
    return pd.read_sql(strQry, cnxn)

