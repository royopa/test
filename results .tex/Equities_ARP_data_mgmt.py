from py_init import *
from asset import *

library=mds.assetVS

#pega todos os equities
lst = mds.find(library=library,subtype='equity',currency='BRL')
nms = [l['name'] for l in lst if (('source' in l) and (l['source'] == 'economatica') ) ] #and l['maturity'] is None

# lst1 = [l for l in lst[:,2] if (('source' in l) or (l['source'] == 'economatica') and l['maturity'] is None)]
# nms=[l.name for l in lst1]
# len(lst)

a = asset.get(nms,library=library)

flds=['volume_fin','alpha_close','close','vwap','high','low','open','volume','neg']

#cria dataframes para cada campo
dfs=Dict()
for fld in flds:
    lst=[pd.DataFrame(a0.df[fld]).rename(columns={fld:a0.md.name}) for a0 in a]
    dfs[fld]=pd.concat(lst,axis=1)

# uncomment to save cache
uu.save_obj(dfs,'eqDfs')
# dfs=uu.load_obj('eqDfs')

avgVol=dfs.volume_fin.rolling(200).mean()

# plot(avgVol['ITUB4_E'])

# generate volume filter
prcVol = avgVol/avgVol.sum(axis=1).values[:,None]
prcVol=prcVol.fillna(0)
J=[]
for t in range(prcVol.shape[0]):
    J_=np.argsort(-prcVol.values[t,:])
    J.append( J_)
# plot(prcVol['ITUB4_E'])

# JJ=J[-1]
# JJ=J_
# prcVol.columns[JJ[:100]]


volMinFilter = (prcVol>0.005).any(0)
nms1=prcVol.columns[volMinFilter]
nms1=nms1[~nms1.str.contains('TELB')]

#filter for equities with the criteria above
dfs1 = Dict({k:v.loc[:,nms1] for k,v in dfs.items()})



# plot(log(dfP.iloc[:,1]))
########### PE - calc e bate ###############

#get unadjusted prices
dfs_n_adj =mds.read(list(pd.Index(nms1).str.replace('_E','_E_nadj')),library=library)
dfs_n = [pd.DataFrame(df.loc[:,'close']).rename(columns={'close':nms1[i]}) for i,df in enumerate(dfs_n_adj)]
dfs1['close_N'] = pd.concat(dfs_n, axis=1)
dfs1['close_N']=dfs1['close_N'].reindex(dfs1['close'].index)


dfs_indm = [mds.read(nm.replace('_E','_INDM'),library=mds.fundamentalVS) for nm in nms1]
dfs_indf = [mds.read(nm.replace('_E','_INDF'),library=mds.fundamentalVS) for nm in nms1]
dfs_bal = [mds.read(nm.replace('_E','_BAL'),library=mds.fundamentalVS) for nm in nms1]

### correcao de base! ###
dfsFund=Dict()
info=['indm','indf','bal']
for ii,df_col in enumerate([dfs_indm,dfs_indf,dfs_bal]):
    for i,df in enumerate(df_col):
        for k in range(len(df.columns)):
            if df.dtypes[k]==object:
                df.iloc[:,k]=df.iloc[:,k].str.replace('.','')
                df.iloc[:,k]=df.iloc[:,k].str.replace(',','.')
                df.iloc[:,k]=df.iloc[:,k].astype(float64)

    dfsFund[info[ii]] = Dict()
    flds=df_col[0].columns
    for fld in flds:
        lst = [pd.DataFrame(df[fld]).rename(columns={fld: nms1[jj]}) for jj,df in enumerate(df_col)]
        dfsFund[info[ii]][fld] = pd.concat(lst, axis=1)

###

# dfs_pe = [pd.DataFrame(df.loc[:,'pe12m']).rename(columns={'pe12m':nms1[i]}) for i,df in enumerate(dfs_indm)]
# dfs_eps = [pd.DataFrame(df.loc[:,'eps']).rename(columns={'eps':nms1[i]}) for i,df in enumerate(dfs_indf)]



#eps1=dfs1['eps'].reindex(dfs1.close.index,method='ffill')
#resultado em 12 meses
ni12m=dfsFund['bal']['netIncome'].copy()
II=where(ni12m.index.month.isin([4,7,10]))[0]
ni12m.values[II,:]=ni12m.values[II,:]-ni12m.values[II-1,:]
ni12m=ni12m.rolling(4).sum()

eps0=(ni12m/dfsFund['bal']['numSharesAvg'])

idx1= eps0.index.shift(3, freq='MS').shift(-1, freq='D')
pe0=dfs1.close_N.reindex(idx1,method='bfill')/eps0.values

# eps1=eps0.reindex(dfs1.close.index,method='ffill').fillna(method='ffill')
# pe1=dfs1.close_N/eps1

pe=pe0.reindex(dfs1.close.index,method='ffill')
lc=log(dfs1.close)
for idx in pe0.index:
    try:
        ii=lc.index.get_loc(idx,method='bfill')
    except:
        continue
    lc.values[ii:,:]=lc.values[ii:,:]-lc.values[ii:ii+1,:]

pe.values[:]=pe.values[:]*exp(lc.values)

dfsFund['pe_calc']= pe
dfsFund['pe_calc0']= pe0

#
# plot(eps1['ITUB4_E'])
# plot(pe1['ITUB4_E'])
# plot(pe['ITUB4_E'].loc[dt(2000,1,1):])
#
plot(dfsFund['indm']['pe12m']['ITUB4_E'])
plot(pe['ITUB4_E'])
plot(pe0['ITUB4_E'].loc[dt(1990,1,1):])

#adjustment for lagging pe

pel= pe.copy()

lagPE=0

pel=pel.reindex(dfs1.close.index,method='ffill')
# close1=dfs1.close.reindex(dfs1['pe'])
pel=pel.shift(lagPE)*dfs1.close.values/dfs1.close.shift(lagPE).values



dfsFund['pe_calc_wlag']=pel

uu.save_obj(dfsFund,'dfsFund',path=r'F:\SISTDAD\MEMPGRP\BMORIER\data')
uu.save_obj(dfs1,'dfsEq1',path=r'F:\SISTDAD\MEMPGRP\BMORIER\data')


