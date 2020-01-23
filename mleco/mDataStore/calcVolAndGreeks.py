from py_init import *
from py_vollib.black.greeks import analytical
from py_vollib.black.implied_volatility import *

def calcVolAll():
    calcVol(mercFilter='IND')
    calcVol(mercFilter='DOL')
    calcVol(mercFilter='IND',opcMercFilter='IBOV')
    calcVol(mercFilter='DI1',opcMercFilter='IDI')
    calcVol(mercFilter='DI1',opcMercFilter='IDI') #adapt code




def calcVol(mercFilter='DOL',opcMercFilter=None):
    if opcMercFilter is None:
        opcMercFilter=mercFilter
    opclst=mds.find({'$regex':'^{}'.format(opcMercFilter)},ds.freqHelper.bday,mds.b3VS,False,type='option')
    futlst=mds.find({'$regex':'^{}'.format(mercFilter)},ds.freqHelper.bday,mds.b3VS,False,type='future')
    opclst=[o[1].replace('_1BDay','') for o in opclst]
    futlst=[o[1].replace('_1BDay','') for o in futlst]

    df_fut = mds.read(futlst,library=mds.b3VS)
    df_fut={f.md.name:f for f in df_fut}
    #df_opc=

    for i,nm in enumerate(opclst):
        df=mds.read(nm,ds.freqHelper.bday,mds.b3VS)
        df0=df.copy()
        underlying1 = mercFilter + uu.futCodeFromDate(df.md.maturity)
        #df.md.underlying
        try:
            df_fut1=df_fut[underlying1+'_b3']
        except:
            try:
                df_fut1=df_fut[underlying1.replace('0','')+'_b3']
            except:
                warn('future not found {}'.format(underlying1))
                continue


        df_fut1=df_fut1.reindex(df.index)
        du=uu.networkdays(df.index,df.md.maturity)
        dc=(df.md.maturity-df.index).days/365
        rf = uu.rCont(uu.getRates(df.index,du))
        vol = empty_like(df.close)
        vol1 = empty_like(df.close)
        df['vol']=nan
        df['delta']=nan
        df['gamma']=nan
        df['theta']=nan
        df['vega']=nan

        px=df.close*exp(rf*((du+1)/252))
        for t,px1 in enumerate(px):
            if du[t]>0:
    #            vol[t] = implied_volatility(px,df_fut1.close[t],df.md.strike,rf[t],du[t]/252,df.md.cp)
                try:
                    df['vol'].values[t] = implied_volatility_of_undiscounted_option_price(px1,
                                            df_fut1.close[t],df.md.strike,dc[t],df.md.cp)
                    df.gamma.values[t] = analytical.gamma(df.md.cp, df_fut1.close[t], df.md.strike, dc[t], rf[t], df['vol'][t])
                    df.theta.values[t] = analytical.theta(df.md.cp, df_fut1.close[t], df.md.strike, dc[t], rf[t], df['vol'][t])
                    df.vega.values[t] = analytical.vega(df.md.cp, df_fut1.close[t], df.md.strike, dc[t], rf[t], df['vol'][t])


                    df.delta.values[t] = analytical.delta(df.md.cp, df_fut1.close[t], df.md.strike, dc[t], rf[t], df['vol'][t])
                except:
                    warn('invalid vol (prob below intrinsic)')
            else:
                df['vol'].values[t] =0

        print('{} i: {}/{}'.format(nm,i,len(opclst)))
        if not df0.equals(df):
            mds.write(df,library=mds.b3VS,check_metadata=False,prune_previous_version=True)


    #df.md
    #uu.writeXL('opc',df)

