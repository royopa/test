import globalM

import pandas as pd
import numpy as np
from numpy import *
from warnings import warn
from io import StringIO
import re

def updateAll():
    pass

def insertAll():
    #insertAllPX()
    insertALLFundamental()


def insertAllPX():
    from mDataStore.globalMongo import mds
    from mDataStore.mongo import mDataFrame,metadataAsset
    files=['PX_NOT_ADJ.txt','PX_ADJ.txt']
    suffixName=['_E_nadj','_E']
    subtype=['equity_nadj','equity']
    dtFormat='%d/%m/%Y'

    origCols=['Data', 'Q Negs', 'Q Títs', 'Volume$', 'Fechamento', 'Abertura','Mínimo', 'Máximo', 'Médio', 'code']
    newCols=['dt','neg','volume','volume_fin','close','open','low','high','vwap','code']
    #need to confirm 'Medio' is vwap
    mapCols={k:newCols[i] for i,k in enumerate(origCols)}

    for i,f in enumerate(files):
        df = readEconCSVPX(f)
        #df.rename(mapCols[i],inplace=True)
        df.columns=newCols
        df.dt = pd.to_datetime(df.dt, format=dtFormat)
        df.set_index('dt',inplace=True)
        ucode=unique(df.code)
        for n,code in enumerate(ucode):
            print('n: {}/{}'.format(n,len(ucode)))
            df1=df.loc[df.code==code]
            del df1['code']
            df1=mDataFrame(df1)
            df1.md = metadataAsset(code+suffixName[i],'equity',stDT=df1.index[0])
            df1.md.subtype=subtype[i]
            df1.md.source='economatica'

            mds.write(df1,check_metadata=False,prune_previous_version=True,library=mds.assetVS)
        #dfs=convertDF(df)

#    df = readEconCSVPX('PX_ADJ.txt')

def insertALLFundamental():
    '''
    For the columns correspondence see campos_economatica at economatica folder (surf)
    :return:
    '''
    from .globalMongo import mds
    from .mongo import mDataFrame,metadataFundamental
    files=['BAL.txt','INDF.txt','INDM.txt','SI.txt']
    dtFormat=[None,None,'%d/%m/%Y','%d/%m/%Y']
    suffixName=['_BAL','_INDF','_INDM','_SI']
    subtype=['bal','indf','indm','si']
    cols=[]
    newCols=[]

    cols.append(['Data', 'Qtd Ações|Outstanding|da empresa','Lucro Liquido| Em moeda orig| no exercício| consolid:sim*',       'EBIT| Em moeda orig| no exercício| consolid:sim*','DeprecAmorExaus| Em moeda orig| no exercício| consolid:sim*',       'AumLiqCap| Em moeda orig| no exercício| consolid:sim*','ReInFi| Em moeda orig| no exercício| consolid:sim*',       'Receita| Em moeda orig| no exercício| consolid:sim*','Ativo Tot| Em moeda orig| consolid:sim*',       'Aum Cap| Em moeda orig| no exercício| consolid:sim*','CaixaEEqCx| Em moeda orig| consolid:sim*',       'AtvCir| Em moeda orig| consolid:sim*','PasCir| Em moeda orig| consolid:sim*','Patrim Liq| Em moeda orig| consolid:sim*',       'TotEmFiLP| Em moeda orig| consolid:sim*','DbntLP| Em moeda orig| consolid:sim*','FinLP| Em moeda orig| consolid:sim*',       'Imobil| Em moeda orig| consolid:sim*','Pas+PL| Em moeda orig| consolid:sim*','AmDesAgi| Em moeda orig| no exercício| consolid:sim*',       'CxOper| Em moeda orig| no exercício| consolid:sim*','DeprAmor| Em moeda orig| no exercício| consolid:sim*',       'DasOpe| Em moeda orig| no exercício| consolid:sim*','DbntCP| Em moeda orig| consolid:sim*',       'DesAdm| Em moeda orig| no exercício| consolid:sim*','DesVen| Em moeda orig| no exercício| consolid:sim*',       'DivPag| Em moeda orig| no exercício| consolid:sim*','LAIR| Em moeda orig| no exercício| consolid:sim*',       'Lucro Bruto| Em moeda orig| no exercício| consolid:sim*','TotEmFiCP| Em moeda orig| consolid:sim*', 'RecBru| Em moeda orig| no exercício| consolid:sim*','ResFin(Ant)| Em moeda orig| no exercício| consolid:sim*',       'FinCP| Em moeda orig| consolid:sim*','FinObtLiq| Em moeda orig| no exercício| consolid:sim*',       'IRDife| Em moeda orig| no exercício| consolid:sim*','CPV| Em moeda orig| no exercício| consolid:sim*',       'LuOpCo| Em moeda orig| no exercício| consolid:sim*','Out Des Adm| Em moeda orig| no exercício| consolid:sim*',       'PrAcMi| Em moeda orig| no exercício| consolid:sim*','ImpRen| Em moeda orig| no exercício| consolid:sim*',       'Qtd Ações Méd|Outstanding|da empresa|em 1 ano','AuAcTe| Em moeda orig| no exercício| consolid:sim*',       'Integ Cap| Em moeda orig| no exercício| consolid:sim*','FinDeb| Em moeda orig| no exercício| consolid:sim*',       'Redu Cap| Em moeda orig| no exercício| consolid:sim*','DpInCP| Em moeda orig| consolid:sim*',       'DeInFi| Em moeda orig| no exercício| consolid:sim*', 'code'])

    cols.append(['Data', 'LPA| Em moeda orig| de 12 meses| consolid:sim*| ajust p/ prov',
       'VPA| Em moeda orig| consolid:sim*| ajust p/ prov',
       'Vendas/Acao| Em moeda orig| de 12 meses| consolid:sim*| ajust p/ prov',
       'EBITDA/Acao| Em moeda orig| de 12 meses| consolid:sim*| ajust p/ prov',
       'EBITDA| Em moeda orig| de 12 meses| consolid:sim*',
       'MrgBru| de 12 meses| consolid:sim*',
       'Mrg EBIT| de 12 meses| consolid:sim*',
       'RenPat(med)| Em moeda orig| de 12 meses| consolid:sim*',
       'ROIC (IC medio)%| de 12 meses| consolid:sim*',
       'Capex| Em moeda orig| de 12 meses| consolid:sim*',
       'AlaFin| de 12 meses| consolid:sim*',
       'Invest Cap $| Em moeda orig| consolid:sim*',
       'Depr e Amor| Em moeda orig| de 12 meses| consolid:sim*',
       'AlaOpe| de 12 meses| consolid:sim*', 'code'])
    cols.append(['Data', 'P/L|Em moeda orig|de 12 meses|consolid:sim*','Valor Mercado|da empresa|Em moeda orig',       'Div Yld (fim)|1 anos|Em moeda orig',       'EV/EBITDA emp|Em moeda orig|de 12 meses|consolid:sim*', 'code'])

    cols.append(['Data', 'Qtd\ntítulos', 'Cotação\nmédia', 'Valor$', 'Qtd\ntítulos.1',
       'Qtd\ncontratos', 'Valor$.1', 'Tx mín', 'Tx méd', 'Tx máx', 'Tx mín.1',
       'Tx méd.1', 'Tx máx.1', 'code'])

    newCols.append(['dt','numShares','netIncome','ebit','deprecAmortExhaus','netCapitalIncrease','finIncome','revenues','totalAssets','capitalIncrease','cashEquiv','assetST','liabST','netEquity','totLiabLT','debtLT','liabLT','fixedAssets','totalLiab','AmDesAgi','cfo','deprecAmort','DasOpe','debST','admExp','salesExp','divPaid','ebt','grossProfit','totLiabST','revenuesGross','finNetIncome','liabST','FinObtLiq','taxesPayable','cogs','LuOpCo','OutDesAdm','PrAcMi','taxesPaid','numSharesAvg','AuAcTe','IntegCap','FinDeb','ReduCap','DpInCP','DeInFi','code',])
    newCols.append(['dt','eps','bps','revps','ebitdaps','ebitda','grossMargin','ebitMargin','ROE',
                    'ROIC','capex','finLeverage','investedCap','deprecAmort','operLeverage','code'])
    newCols.append(['dt','pe12m','mktcap','div_yld12m','ev2ebitda12m','code'])
    newCols.append(['dt','volume','vwap','volume_fin','volume2','neg','volume_fin2',
                    'low_bid','avg_bid','high_bid','low_ask','avg_ask','high_ask','code'])
    #need to confirm 'Medio' is vwap

    # mapCols=[]
    # for i,v in enumerate(newCols):
    #     mapCols.append({k:newCols[i][j] for j,k in enumerate(cols[i])})

#    for i,f in enumerate(files):
    i=3
    f=files[i]
    if i==3:
        df = readEconCSVPX(f)
    else:
        df = readEconCSV(f)
    df.columns=newCols[i]
    #df=df.rename(mapCols)
    df.dt = df.dt.str.replace('T', 'Q')
    df.dt = pd.to_datetime(df.dt, format=dtFormat[i])

    df.set_index('dt',inplace=True)
    ucode=unique(df.code)
    for n,code in enumerate(ucode):
        print('n: {}/{}'.format(n,len(ucode)))
        df1=df.loc[df.code==code]
        del df1['code']
        df1=mDataFrame(df1)
        df1.md = metadataFundamental(code+suffixName[i],'equity',stDT=df1.index[0])
        df1.md.source='economatica'
        df1.md.subtype=subtype[i]
        mds.write(df1,mds.fundamentalVS,check_metadata=False,prune_previous_version=True)





def readEconCSV(file1):
    path1 = globalM.dataRoot +'/economatica/'
    #file1 = 'BAL.txt'
    #file1 = 'INDF.txt'
    #file1 = 'INDM.txt'


    with open(path1+file1, 'r') as fp:
        txt1=fp.read()
        txts=txt1.split('\n\n')
        dfl=[]
        for i,txt in enumerate(txts):
            if txt[:6] =='"Data"':
                df1 = pd.read_csv(StringIO(txt), sep=';', decimal=',', na_values=['-'])
                nm=df1.iloc[0,1]
                df1=df1.iloc[1:,:]
                # df1.index = pd.MultiIndex.from_arrays(df1[['Data','code']].values.T,names=['Data','code'])
                # uu.writeXL('df',df1)
                df1['code']=nm
                dfl.append(df1)
            else:
                if i % 2 ==1:
                    warn('Aparent Invalid File: Odd "row" did not have data in themexpected format')

        df = pd.concat(dfl)
    return df

def readEconCSVPX(file1):
    path1 = globalM.dataRoot +'/economatica/'
    #file1 = 'BAL.txt'
    #file1 = 'INDF.txt'
    #file1 = 'INDM.txt'
    #file1='PX_ADJ.txt'
    #file1='PX_NOT_ADJ.txt'

    with open(path1+file1, 'r') as fp:
        txt1=fp.read()
        txts=txt1.split('\n\n')
        dfl=[]
        for i,txt in enumerate(txts):
            if i % 2 == 0:
                nm = re.findall('\(.*\)',txt)[0][1:-1]

            else:
                if txt[:6] =='"Data"':
                    df1 = pd.read_csv(StringIO(txt), sep=';', decimal=',', na_values=['-'])
                    #nm=df1.iloc[0,1]
                    #df1=df1.iloc[1:,:]
                    # df1.index = pd.MultiIndex.from_arrays(df1[['Data','code']].values.T,names=['Data','code'])
                    # uu.writeXL('df',df1)
                    df1['code']=nm
                    if df1.shape[0]>0:
                        dfl.append(df1)
                else:
                    warn('Aparently Invalid File: Odd "row" did not have data in themexpected format')

        df = pd.concat(dfl)
    return df