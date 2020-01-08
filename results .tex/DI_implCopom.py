from py_init import *
from addict import *
from scipy.interpolate import *
from numpy import *
import mUtil as uu
#import mPyMatlab as mat
import pandas as pd
import numpy as np
from asset import asset
from mDataStore.globalMongo import mds
#dbdi=mat.loadMat('W:\\Multi-Asset Portfolio Solutions\\Databases\\Ativos\\DB_DI_CONS2.mat')
#DATA=mat.loadMat('W:\\Multi-Asset Portfolio Solutions\\Databases\\Ativos\\DATA.mat')
bk=xw.books.open(globalM.dataRoot+'/COPOM_decisions.xlsx')
sh=bk.sheets['Sheet1']
cpom = sh.range('tbSelic[#All]').options(pd.DataFrame, expand='table').value  #scipy.io.loadmat(globalM.dataRoot+'/copom_decisions.mat')['cpom']
cpom.columns=['close']#fer = scipy.io.loadmat('W:\\Multi-Asset Portfolio Solutions\\Databases\\Ativos\\feriados.mat')['feriados']

di1 = mds.getDI(filterMty=False)
di1 = asset.get(di1)

dbdi_du = pd.concat([d._mdf.du for d in di1],1)
dbdi_tx = pd.concat([d._mdf.yield_close for d in di1],1)

dbdi_du.columns = [d.name for d in di1]
dbdi_tx.columns = [d.name for d in di1]

dbdi_du.index=uu.x2dti_date(dbdi_du.index)
dbdi_tx.index=uu.x2dti_date(dbdi_tx.index)

#fer=uu.m2pdate(fer[:,0])
#ferDT=fer.date
#dbdi=Dict(dbdi)
#DATA=Dict(DATA)
out=Dict()

out.cpom = cpom#pd.DataFrame(data=cpom[:,1],index=uu.x2pdate(cpom[:,0]),columns=['rate'])
out.cpomAll=out.cpom.copy()
out.du = dbdi_du
out.tx = dbdi_tx/100


#out.cdi=pd.DataFrame(data=DATA.INDEX.CDI[:,1],index=uu.x2pdate(DATA.INDEX.CDI[:,0]),columns=['rate'])
out.cdi = mds.read('CDI')
out.cdi.iloc[:,0]=insert(diff(log(out.cdi.values),axis=0),0,0)
out.cdi.iloc[:,0]=exp(out.cdi)**252-1

out.cpom=out.cpom.reindex(out.du.index,method='ffill')/100
out.cpom=out.cpom.fillna(method='ffill')
out.cdi=out.cdi.reindex(out.du.index,method='ffill')

delt=(out.cdi-out.cpom).rolling(30).mean()

out.cdiProxy=out.cpom.shift(1)+delt
#out.cpom=out.cpom[(~pd.isna(out.cpom)).values]


# t=out.tx.shape[0]-1
# dt=out.tx.index[t]
# t0=out.cpom.index.searchsorted(dt)
# t0=minimum(t0,out.cpom.shape[0]-1)
# out.cpom.iloc[t0,:]
out.cpomAll[out.cpomAll.index>out.tx.index[-1]]=NaN
cpomDec=insert(diff(out.cpomAll.values[:,0],axis=0)*1e2,0,0)[:,None]
out.cpomDec=cpomDec

out.cpomFit=np.tile(cpomDec,[1,out.tx.shape[0]])
dt_cpom_tmp=np.tile(uu.dti2x_date(out.cpomAll.index),[out.tx.shape[0],1])
II= dt_cpom_tmp>=uu.dti2x_date(out.tx.index)[:,None]
out.cpomFit[II.T]=NaN


out.txMkt=[]
out.txFit=[]
out.duFit=[]
out.errFit=[]
out.spl=[]
out.duCpom=full((out.tx.shape[0],out.cpomAll.size),NaN)

#t=out.tx.shape[0]-1
t0=where(~isnan(out.cdiProxy.values))[0][0]
vcto=pd.DatetimeIndex([d.md.maturity for d in di1])
vertOut=array([1,21,42,63,126,252,378,512,756,1008,1512,1764,2520])

dfVertFix=ds.mDataFrame(full((out.tx.shape[0],vertOut.size),nan),index=out.tx.index,columns=vertOut)

for t in range(t0+5,out.tx.shape[0]):

    tx1=out.tx.iloc[t,:].values
    du1=out.du.iloc[t,:].values
    du1[isnan(du1)]=0
    I=(~(isnan(tx1)))&(du1>1)

    tx1=tx1[I].astype(float64)
    du1=du1[I].astype(float64)


    #m1 = uu.m2pdate(dbdi.vcto[I][:,0])
    m1 = vcto[I]

    J=argsort(du1)
    du1=du1[J]
    tx1=tx1[J]
    m1=m1[J]

    tx1=insert(tx1,0,out.cdiProxy.iloc[t,0])
    du1=insert(du1,0,1)



    w = 10.0*(m1.month==1)+1*(m1.month==4)+5*(m1.month==7)+1*(m1.month==10)+1
    w[du1[1:]<60]=maximum(w[du1[1:]<60],5.)
    w=insert(w,0,100)

    tck = splrep(du1, tx1,w=w,s=0.00005) #/rho1[:,t].size
    #tck = splrep(du1, tx1) #/rho1[:,t].size
    bs = BSpline(tck[0],tck[1],tck[2])

    dt0=out.tx.index.to_pydatetime().astype(np.datetime64)[t]

    I = (out.cpomAll.index>=out.tx.index[t])&(out.cpomAll.index<=m1[-1])

    dtCpom = out.cpomAll.index[I].to_pydatetime().astype(np.datetime64)

    #ferDT=fer.to_pydatetime()
    #ferDT=ferDT.astype(np.datetime64)
    #du = busday_count(dt0,dtCpom,holidays=ferDT)
    du = uu.networkdays(dt0,dtCpom)

    txCpom=bs(du)
    dfVertFix.values[t,:]=bs(vertOut)

    frwCopom=(((1+txCpom[1:])**(du[1:]/252))/((1+txCpom[:-1])**(du[:-1]/252)))**(252/(du[1:]-du[:-1]))-1
    cpomAcc=(frwCopom-tx1[0])*1e4
    cpomCurve=np.insert(diff(cpomAcc),0,cpomAcc[0])

    out.cpomFit[where(I)[0][:-1],t]=cpomCurve

    errFit=tx1-bs(du1)

    out.txMkt.append(tx1)
    out.txFit.append(bs(du1))
    out.duFit.append(du1)
    out.errFit=errFit
    out.spl.append(bs)
    out.duCpom[t,I]=du

    print('t:{}'.format(t))

#uu.save_obj(out,'copomFit')
#out=Dict(uu.load_obj('copomFit'))

###### save COPOM fit
df1=ds.mDataFrame(pd.DataFrame(out.cpomFit.T,index=out.tx.index,columns=out.cpomAll.index))
df1.md = ds.metadataFundamental('copomFit','analysis',df1.index[0])
mds.write(df1,check_metadata=False,prune_previous_version=True)
df1.to_excel(globalM.dataRoot+'/cpomHist.xlsx')

###### save Fix Curve
dfVertFix.md = ds.metadataFundamental('ratesCurveBZ','analysis',dfVertFix.index[0])
dfVertFix=dfVertFix[~all(isnan(dfVertFix),1)]
mds.write(dfVertFix,check_metadata=False,prune_previous_version=True)
#uu.save_obj(out.spl,'rateCurveBZspline')
aspl=array(out.spl)
dfBS = ds.mDataFrame(aspl,df1.index[-aspl.size:],['bSpline'])
mds.obj.save('ratesCurveBZ',dfBS,'analysis')

#out.pop('spl')
#scipy.io.savemat('W:\\Multi-Asset Portfolio Solutions\\Databases\\copom_decisions_fit.mat',out)

cpomPast = out.cpomDec[out.cpomAll.index<out.tx.index[-1]]

#premio copom

In=isnan(out.duCpom)



N=252
i0=30
premiumCpom=empty([N,cpomPast.size-i0])
for i in range(i0,cpomPast.size):
    ti=np.where(df1.index==out.cpomAll.index[i])[0][0]
    premiumCpom[:,i-i0]=out.cpomFit[i,ti-N:ti]-cpomPast[i]



N1=-30
m0=nanmean(premiumCpom[:,N1:],1)
m_m1=nanmean(premiumCpom[:,N1:],1)-nanstd(premiumCpom[:,N1:],1)
m_p1=nanmean(premiumCpom[:,N1:],1)+nanstd(premiumCpom[:,N1:],1)

#df1[out.duCpom]
duCpom1=out.duCpom.astype(int)
In=isnan(out.duCpom)
duCpom1[In]=0

cpomExPremium=df1.values- m0[-minimum(duCpom1,m0.size)]
cpomExPremium[In]=nan

################################
N=252
i0=30
cpomAlign=empty([N,cpomPast.size-i0])
for i in range(i0,cpomPast.size):
    ti=np.where(df1.index==out.cpomAll.index[i])[0][0]
    cpomAlign[:,i-i0]=out.cpomFit[i,ti-N:ti]

#################################
import matplotlib.pyplot as plt
plt.plot(arange(-N,0),m0)
plt.plot(arange(-N,0),m_p1)
plt.plot(arange(-N,0),m_m1)


dfStat=pd.DataFrame(concatenate([m0[:,None],m_m1[:,None],m_p1[:,None]],1),columns=['meanCpom','m1StdCpom','p1StdCpom'])
dfStat.to_excel(globalM.dataRoot+'/pyObj/cpomStat.xlsx')

sum(m0[arange(30,252,30)])

# plt.figure()
# plt.plot(premiumCpom[:,-30:])

dfPremiumExPost=ds.mDataFrame(premiumCpom)
dfPremiumExPost.md=ds.metadataFundamental('copomPremiumExPost','analisys')
mds.write(dfPremiumExPost,check_metadata=False,prune_previous_version=True)


# import matlab.engine
# eng = matlab.engine.start_matlab()
# eng.AA_cnvDBDI(nargout=0)
#
# o1=eng.ones(3,1)

# xx=linspace(1,2880,10000)
#
#
#
#
#
#
#
#
#
# plt.plot(xx,bs(xx))
#
# for i in range(du1.size):
#     plt.plot(du1[i], tx1[i], 'ro')






dbdi.keys()
dbdi.code.shape
dbdi.vcto.shape
dbdi.tx.shape
