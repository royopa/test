# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 07:14:39 2019

@author: marcgut
"""

import pandas as pd
import econuteis as eu
import numpy as np
from mDataStore.bloomberg.remote import rBLP
from datetime import datetime, timedelta
import shelve
from atacado_agrupamento import prohort_pond



def import_ws_db():
    # ceagesp
    path = r'F:\DADOS\ASSET\MACROECONOMIA\DADOS\Inflação\4.CEAGESP\bases\CEAGESP_base.xlsx'
    
    base_ceagesp = pd.read_excel(path, sheet_name='Sheet1',
                                 header=0, index_col = 1).transpose()
    base_ceagesp = base_ceagesp.iloc[1:, :]

    base_ceagesp = eu.add_label_df(base_ceagesp, 'ceagesp_')

    base_ceagesp = eu.index_to_datetime(base_ceagesp, '%Y-%m-%d')

    base_ceagesp = base_ceagesp.interpolate(method='time')
    
    last_day = base_ceagesp.index[-1]

    
    # cepea
    path = r'F:\DADOS\ASSET\MACROECONOMIA\DADOS\Inflação\5.CEPEA\bases\CEPEA_base.xlsx'
    
    base_cepea = pd.read_excel(path, sheet_name='Sheet1', header=0, index_col=0)
    
    base_cepea = eu.add_label_df(base_cepea, 'cepea_')
    
    base_cepea = eu.index_to_datetime(base_cepea, '%Y-%m-%d')
    
    base_cepea = base_cepea.interpolate(method='time')
    
    if base_cepea.index[-1] < last_day:
        last_day = base_cepea.index[-1]

    
    # Bloomberg
#    base_bbg = rBLP().getHistoricData(['SJC1 Comdty', 'BO1 Comdty', 'C 1 Comdty',
#                                      'W 1 Comdty', 'KC1 Comdty', 'SB1 Comdty',
#                                      'LC1 Comdty', 'FC1 Comdty',
#                                      'LH1 Comdty', 'Ls1 Comdty', 'bamtcaca index',
#                                      'BAMTCAFR Index', 'bamtcare index',
#                                      'BRL Curncy'],['PX_LAST'],
#                                    startDate=datetime(1997, 1, 1),
#                                    endDate=datetime(2100, 1, 1))
#    
#    ref_bbg = ['soja', 'oleo_soja', 'milho', 'trigo', 'cafe', 'açucar',
#                                      'live_cattle', 'feeder_cattle',
#                                      'lean_hog', 'boi_futuro', 'carcaça',
#                                      'dianteiro', 'traseiro',
#                                      'usd']
    # Não estou conseguindo pegar boi futuro da bloomberg, vou pegar da planilha
    path = r'F:\DADOS\ASSET\MACROECONOMIA\1PIETRO\BBG\bbg_assets_day.xlsx'
    
    base_bbg = pd.read_excel(path, sheet_name='PX_Comdty', header=0, index_col=0)
    
    base_bbg = base_bbg.loc[:,('soy', 'soy_oil', 'corn', 'wheat', 'coffee',
                               'sugar', 'live_cattle', 'feeder_cattle', 
                               'lean_hogs', 'boi futuro', 'carcaca', 'dianteiro',
                               'traseiro')]
    base_bbg = base_bbg.loc[eu.get_fst_date_idx(base_bbg):last_day, :]
    
    brl = rBLP().getHistoricData(['BRL Curncy'], ['PX_LAST'],
              startDate=datetime(1997, 1, 1), endDate=datetime(2100, 1, 1))[0]
    
    brl = brl.align(base_bbg, join='outer', axis=0)[0]
    brl = brl.align(base_bbg, join='inner', axis=0)[0].fillna(method='bfill')
    brl = pd.Series(brl.iloc[:,0], index=brl.index)    
    
    base_bbg.loc[:, ('soy', 'soy_oil', 'corn', 'wheat', 'coffee',
                               'sugar', 'live_cattle', 'feeder_cattle', 
                               'lean_hogs')] = base_bbg.loc[:, ('soy', 'soy_oil', 'corn', 'wheat', 'coffee',
                               'sugar', 'live_cattle', 'feeder_cattle', 
                               'lean_hogs')].multiply(brl, axis=0)

    base_bbg = eu.add_label_df(base_bbg, 'bbg_')

    
    # Prohort (função separada)
    base_prohort = import_prohort() 
#    items_prohort = list(base_prohort.columns)
#    
#    # Salvando as colunas do DF do prohort num shelve (é utilizado por outras funções sem precisar
#    # gerar imput e complicar a chamada das funções)
#    db = shelve.open(r'F:\DADOS\ASSET\MACROECONOMIA\DADOS\Inflação\9.PROHORT\items_prohort')
#    db['items_prohort'] = items_prohort
#    db.close()
#    
    #base_prohort
    # Juntando os dataframes
    whs_df = pd.concat([base_ceagesp, base_cepea, base_bbg, base_prohort], join='outer',
                       axis=1)
    
    whs_df = whs_df.fillna(method='pad')
    
    return whs_df


def import_monit_db():
    path = r'F:\DADOS\ASSET\MACROECONOMIA\DADOS\Inflação\3.MonitorFGV\MonitorFGV.xlsm'
    
    base_ponta = pd.read_excel(path, sheet_name='PONTA', header=3, index_col=0).transpose()
    base_media = pd.read_excel(path, sheet_name='MEDIA', header=3, index_col=0).transpose()
    
    base_ponta = base_ponta.loc[datetime(2012, 1, 2):, :]
    base_media = base_media.loc[datetime(2012, 1, 2):, :]
    
    path = r'F:\DADOS\ASSET\MACROECONOMIA\DADOS\Inflação\1.IPCA\bases\IPCA_base_var.xlsx'
    base_ipca = pd.read_excel(path, header=0, index_col=0, sheet_name='var').transpose()
    base_ipca = base_ipca.loc[datetime(2012, 1, 2):, :]
    
    path = r'F:\DADOS\ASSET\MACROECONOMIA\DADOS\Inflação\1.IPCA\bases\IPCA_base_peso.xlsx'
    base_ipca_peso = pd.read_excel(path, header=0, index_col=0, sheet_name='peso').transpose()
    base_ipca_peso = base_ipca_peso.loc[datetime(2012, 1, 2):, :]
    
    
    ipca_var = pd.DataFrame(index=base_ponta.index, columns=base_ponta.columns)
    ipca_peso = pd.DataFrame(index=base_ponta.index, columns=base_ponta.columns)
    
    monit_idx = list(base_ponta.index)
    
    for date in base_ipca.index:
        diff = [abs(x - date) for x in monit_idx]
        near = base_ponta.index[diff.index(min(diff))]
        ipca_var.loc[near, :] = base_ipca.loc[date, :]
        ipca_peso.loc[near, :] = base_ipca_peso.loc[date, :]

    ipca_peso = ipca_peso.fillna(method='backfill')
    ipca_peso = ipca_peso.fillna(method='ffill')

    return base_media, base_ponta, ipca_peso, ipca_var


def make_lags(X, lags_X=[10, 15, 20, 25, 30]):
    X_out = {}
    n_plus = min(lags_X)
    idx = list(X.index)
    for i in range(1, n_plus+1):
        idx.append(idx[-1]+timedelta(1))

    X = X.reindex(idx)

    for series in X:
        for lag in lags_X:
            l_series = X[series].shift(lag)
            X_out[str(series)+'_'+str(lag)] = l_series
    
    X_out = pd.DataFrame(X_out)
    
    return X_out
            

def mth_avg_hist(df):
    df_med = df.copy()
    df_std = df.copy()
    
    start_date = datetime(df.index[0].year, df.index[0].month, 1)
    end_date = datetime(df.index[-1].year, df.index[-1].month, 1)
    
    idx = pd.date_range(start=start_date, end=end_date, freq='MS')
    
    for el in idx:
        mth = el.month
        day = 28
        mth_df = df.loc[df.index.month == mth, :]
        mth_df = mth_df.loc[mth_df.index.day == day, :]
        avg = pd.DataFrame(np.mean(mth_df, axis=0)).T
        avg = pd.concat([avg, pd.Series(mth_df.index[0])], axis=1)
        
        std = pd.DataFrame(np.std(mth_df, axis=0)).T
        std = pd.concat([std, pd.Series(mth_df.index[0])], axis=1)
        
        mth_df = df.loc[df.index.month == mth, :]
        
        avg = avg.set_index(keys=avg.columns[-1])
        avg = avg.reindex(mth_df.index, method='nearest')
        std = std.set_index(keys=std.columns[-1])
        std = std.reindex(mth_df.index, method='nearest')
        
        df_med.loc[avg.index, :] = avg
        df_std.loc[std.index, :] = std
        
    df_top = df_med + df_std
    df_min = df_med - df_std
        
    return df_med, df_top, df_min


def import_prohort(path=r'F:\DADOS\ASSET\MACROECONOMIA\DADOS\Inflação\9.PROHORT\Preços Diarios.xlsm'):
    sheets = ['ABACATE', 'abacaxi', 'ALFACE', 'ALHO', 'BANANA_NANICA', 'BANANA_PRATA', 'BATATA', 
              'BRÓCOLOS', 'CEBOLA', 'CENOURA', 'couve', 'goiaba', 'LARANJA_PERA', 'MAÇÃ', 'MAMAO_FORMOSA',
              'MAMAO_HAVAI', 'MANDIOQUINHA', 'manga', 'maracuja', 'MELANCIA', 'MORANGO', 'OVO', 'PERA',
              'repolho', 'TANGERINA', 'TOMATE', 'UVA_ITALIA', 'UVA_NIAGARA', 'UVA_RUBI']
    
    dfs = {}
    for sheet in sheets:
        df = pd.read_excel(path, sheet_name=sheet, header = 2, index_col = 1)
        df = df.fillna(method='ffill')
        df = compound_prohort(df)
        dfs['prohort_'+sheet] = df
    
    return pd.DataFrame(dfs).fillna(method='ffill')


def compound_prohort(df):
    ref_prohort, ipca_pond = prohort_pond()
    df_out = {}
    for uf in ref_prohort:
        df_out[uf] = pd.Series(np.mean(df.loc[:, ref_prohort[uf]], axis=1), index=df.index,
                               name=uf)
        
    df_out = pd.DataFrame(df_out)
        
    ipca_aux = pd.DataFrame(ipca_pond, index=[df_out.index[0]])
    ipca_aux = ipca_aux.reindex(df_out.index, method='ffill')
    ipca_aux = ipca_aux.loc[:, df_out.columns]
    
    df_out = df_out.multiply(ipca_aux, axis=1)
    
    pond_fin = pd.Series(index=ipca_aux.index)
    for i in pond_fin.index:
        pond_fin.loc[i] = np.sum(ipca_aux.loc[i, df_out.loc[i,:].dropna().index])
        
    
    return pd.Series(np.sum(df_out, axis=1)/pond_fin, index=df_out.index)


    
    
    
    
    
    
    
    
    
    
    