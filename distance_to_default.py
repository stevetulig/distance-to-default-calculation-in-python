"""
Script to calculate distance-to-default for all stocks in our database
from 2000 to 2012
"""
import numpy as np
import pandas as pd
from scipy.stats import norm
from db_interactions_for_DD import connectZenithDb, getMarketValues, \
    getDebt, getRf
import warnings
warnings.filterwarnings("ignore")


def calcVolatility(x): 
     return np.std(np.log(np.divide(x[1:],x[:-1])))*np.sqrt(252)

def BlackScholesCallValue(S,X,r,sigma,T):
    d1=(np.log(S/X)+(r+0.5*sigma**2)*T)/(sigma*np.sqrt(T));
    d2=d1-sigma*np.sqrt(T);
    delta=norm.cdf(d1)
    CP=S*delta-X*np.exp(-r*T)*norm.cdf(d2);
    return [CP, delta]    

def BlackScholesZero(C,X,r,sigma,T):
    # solves Black Scholes Call option formula for S using Newton's method
    if X==0:
        return C

    UpperS=C+X*np.exp(-r*T);
    if sigma==0 or X==0:
        return UpperS

    LowerS=C
    tol=0.0001*C
    delta=C; itercount=0; x0=LowerS; x1=UpperS
    while abs(delta)>tol and itercount<=100:
        itercount=itercount+1
        [bs0,D0]=BlackScholesCallValue(x0, X, r, sigma, T)
        y0=bs0-C
        [bs1,D1]=BlackScholesCallValue(x1, X, r, sigma, T)
        y1=bs1-C

        if D0<0.01:
            xguess=(x0*y1-x1*y0)/(y1-y0);
        else:
            xguess = x0 - y0/D0;

        if xguess>UpperS:
            xguess=UpperS
        elif xguess<LowerS:
            xguess=LowerS
        [bsxg,Dxg]=BlackScholesCallValue(xguess,X,r,sigma,T)
        delta=bsxg-C
        x0=xguess
        
    if abs(delta)>tol:
        return np.nan
    else:
        return xguess
    
def dailyDLIcalcs(Ve,X,r,sigma_a):
    Va=[]
    for v in Ve:
        Va.append(BlackScholesZero(v,X,r,sigma_a,1.0))
    Va=np.array(Va)
    return [Va, calcVolatility(Va)]

def calc_DD(rf, X, Ve, T):
    sigma_a=calcVolatility(Ve)
    sigma_previous=sigma_a

    delta=1.0
    itercount=0

    while not np.isnan(delta) and delta>0.0001 and itercount<100:
        itercount=itercount+1
        [Va, sigma_a]=dailyDLIcalcs(Ve, X, rf, sigma_a)
        delta=abs(sigma_a-sigma_previous)
        sigma_previous=sigma_a

    # compute drift term
    mu=np.mean(np.log(np.divide(Va[1:],Va[:-1])))

    if X==0: # no probability of default
        DD=100
    elif sigma_a==0: # if stock is not traded
        DD=np.nan
    else:
        DD=(np.log(Va[-1]/X)+(mu-(0.5*sigma_a**2))*T) / (sigma_a*np.sqrt(T))

    return [DD, itercount, delta]
 
#establish a connection to the Zenith database
cnxn=connectZenithDb()

T=1
for yr in range(2000,2013):
    res=[]
    # get the risk-free rate for the year
    df=getRf(cnxn, yr,12)
    rf=df.BAB_rate.values[0]/100
    # get a list of stocks and each stock's X value (precalculated)
    all_stocks_X=getDebt(cnxn, yr)
    for r in range(len(all_stocks_X.index)):
        stockid=all_stocks_X.iloc[r,0]
        X=all_stocks_X.iloc[r,1]
        # get the daily market values
        Ve=getMarketValues(cnxn,stockid,yr)
        if len(Ve.index)>0:
            Ve=Ve['Ve'].values*1000000
            z=calc_DD(rf, X, Ve, T)
            z.insert(0,stockid)
            z.insert(0,yr)
            res.append(z)

df=pd.DataFrame(np.array(res),columns=['Year','StockID','DD','itercount','delta'])
df=df.astype({'Year':'int32', 'StockID':'int32', 'itercount':'int32'})
df.to_csv('DD.csv')
print(df.head())