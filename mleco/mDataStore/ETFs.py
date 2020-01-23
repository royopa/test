from py_init import *
from mDataStore.bloomberg.remote import rBLP
from copy import deepcopy
# import holoviews as hv
# hv.extension('bokeh')
blp1 = rBLP()

etfEq=pd.Series(['BBSD','XBOV','IVVB','BOVA','BRAX','ECOO','SMAL','BOVV','DIVO','FIND','GOVE','MATB','ISUS','PIBB','SPXI'])
etfRF = pd.Series(['IMAB','FIXA'])

tickers=list(etfEq+'11 Equity')+list(etfRF+'11 Equity')
df1=blp1.getHistoricData( tickers ,['px_last','fund_total_assets'],dt(2010,1,1),dt(2020,1,1))
df2 = blp1.getRefData(tickers,['name'])


df1_=deepcopy(df1)
for i,df in enumerate(df1_):
    df1_[i] = df1_[i].fillna(method='ffill')


# xrData=xr.concat([df.to_xarray() for df in df1_], dim="dataset")
for i,df in enumerate(df1_):
    figure()
    plot(df1_[i].fund_total_assets)
    title(df2.name.loc[tickers[i]])


dimensions = ['Fund']

# items = [(hv.Image(sine(grid, *k), vdims=['Amplitude'])) for k in keys]
