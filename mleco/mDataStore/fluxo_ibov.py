from py_init import *
from mDataStore.bloomberg.remote import rBLP
from mUtil import bPlotYY,bPlot
from bokeh.layouts import column
from bokeh.io import output_file, show



blp1 = rBLP()


dfs = blp1.getHistoricData(['BZSIFODN Index','BMFCIBNF Index','IBOV index','BMFCIBNN index','BMFCIINJ index'],['PX_LAST'],dt(2000,1,1),dt(2050,1,1))

idx = dfs[0].index.intersection(dfs[1].index).intersection(dfs[2].index)


dfs = [df.reindex(idx) for df in dfs]



dfVista = dfs[0]/1000000

dfVista=dfVista.cumsum()

dfFut = dfs[1]*dfs[2]/1000000000

dfTotal = dfVista+dfFut


df1=dfVista.iloc[:,0]
df2=dfs[2].iloc[:,0]
df1.name='fluxo estrangeiro a vista'
df2.name='ibov'

s1 = bPlotYY(df1,df2,'Fluxo x Ibov',doShow=False)

df1=dfTotal.iloc[:,0]
df2=dfs[2].iloc[:,0]
df1.name='fluxo estrangeiro (vista+futuro)'
df2.name='ibov'


s2 = bPlotYY(df1,df2,'Fluxo x Ibov',doShow=False)

dvol0 = dfVista.diff()
dvol1 = dfTotal.diff()

ret = log(dfs[2]).diff()

rho0=ret.rolling(200).corr(dvol0).iloc[:,0]
rho1=ret.rolling(200).corr(dvol1)

rho0=ret.rolling(200).corr(dvol0.shift(4)).iloc[:,0]
rho1=ret.rolling(200).corr(dvol1.shift(4))

rho0.name='vista'

s3 = bPlot(rho0,'Correlacao',doShow=False)
s3.line(rho1.index,rho1.values[:,0], line_color="blue",legend='total')

output_file(r'F:\SISTDAD\MEMPGRP\QUANT\analysis\flow_ibov.html')

show(column(s1,s2)) #,s3
# show(s3)


