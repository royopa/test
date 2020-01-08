# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 11:07:46 2019

@author: marcgut
"""

#import sys  # Funcionalidades do sistema (incluindo caminhos)
#sys.path.append(r'Z:\Macroeconomia\codes')
#sys.path.append(r'Z:\Macroeconomia\databases\MCM')
#sys.path.append(r'Z:\Macroeconomia\databases')
#sys.path.append(r'F:\SISTDAD\MEMPGRP\BMORIER\python\lib')
from mDataStore.bloomberg.remote import rBLP
from datetime import datetime as dt
from mongo_load import mongo_load
import pandas as pd
import xlwings as xw
import econuteis as eu
import statsmodels.api as sm


# Dados Balança
search_dict = {'table' : 'exportacoes por produto', 'type' : 'value'}
df = mongo_load(search_dict, transform='12m sum')[0]
df = df.dropna(axis=0, how='all').dropna(axis=1, how='all')
exp_total = pd.Series(index=df.index)
exp_total.name = 'total exportacoes'
df = df.fillna(0)
df_prop = df.copy()
for i in range(len(exp_total)):
    exp_total[i] = sum(df.iloc[i, :])
    for j in range(len(df.columns)):
        df_prop.iloc[i, j] = df.iloc[i, j]/exp_total[i]


# Dados Bloomberg (commodities)
blp1 = rBLP()
bbg = blp1.getHistoricData(['CO1 Comdty', 'IOE1 COMB Comdty', 'RBT1 COMB Comdty',
                            'S 1 COMB Comdty', 'LC1 COMB Comdty',
                            'XAU BGN Curncy', 'KC1 Comdty', 'SB1 Comdty',
                      'CT1 Comdty', 'CNY REGN Curncy'],['PX_LAST'], startDate=dt(1997, 1, 1),
                     endDate=dt(2100, 1, 1))

names = ['petroleo', 'minerio', 'aco', 'soja', 'boi', 'ouro', 'cafe', 'acucar',
         'algodao', 'cny']

bbg_dic = {}

for i in range(len(bbg)):
    bbg_dic[names[i]] = bbg[i].rename(columns={'PX_LAST' : names[i]})

bbg_month = {}

for i in bbg_dic.keys():
    bbg_month[i] = eu.month_mma(bbg_dic[i])

cny_min = bbg_month['cny'].loc[bbg_month['minerio'].index, :]
cny_min = cny_min.rename(columns={'cny' : 'minerio'})
bbg_month['minerio'] = bbg_month['minerio'].div(cny_min)
cny_aco = bbg_month['cny'].loc[bbg_month['aco'].index, :]
cny_aco = cny_aco.rename(columns={'cny' : 'aco'})
bbg_month['aco'] = bbg_month['aco'].div(cny_aco)
bbg_month.pop('cny')

# PEGANDO DADO DE MINÉRIO PARA TRÁS
mmetbul = pd.read_excel(r'F:\DADOS\ASSET\MACROECONOMIA\DADOS\Setor_Externo\FUNCEX\PRECOS_DE_EXPORTACAO_SAFRA.xlsx',
                        sheet_name='minerio')
mmetbul = mmetbul.set_index('datas')
mmX = mmetbul.loc[bbg_month['minerio'].index, :].dropna().pct_change().dropna()
mY = bbg_month['minerio'].loc[mmX.index, :].dropna().pct_change().dropna()
mmX = mmX.iloc[1:, :]
ols_min = sm.OLS(mY, mmX).fit()
pred_min = ols_min.predict(mmetbul)
minerio = bbg_month['minerio'].reindex(pred_min.index)
minerio = pd.DataFrame(minerio.iloc[:, 0].fillna(pred_min))
extra_idx = bbg_month['minerio'].index.difference(minerio.index)
if len(extra_idx) > 0:
    idx1 = pd.Series(minerio.index)
    idx2 = pd.Series(extra_idx)
    idx3 = pd.concat([idx1, idx2], axis=0)
    idx3 = idx3.reset_index(drop=True)
    minerio = pd.concat([minerio.reset_index(drop=True),
                         idx3], axis=1).set_index(0)
    minerio = pd.Series(minerio.iloc[:, 0]).fillna(pd.Series(
                        bbg_month['minerio'].iloc[:, 0]))
    bbg_month['minerio'] = minerio


# PEGANDO DADOS DE CELULOSE
celulose = pd.read_excel(r'F:\DADOS\ASSET\MACROECONOMIA\DADOS\Setor_Externo\FUNCEX\PRECOS_DE_EXPORTACAO_SAFRA.xlsx',
                        sheet_name='celulose')
celulose = celulose.set_index('datas')
bbg_dic['celulose'] = pd.DataFrame(celulose.loc[:, 'China'])
bbg_month['celulose'] = eu.month_mma(bbg_dic['celulose'])


# MONTANDO DATAFRAME
for key in bbg_month:
    if isinstance(bbg_month[key], pd.DataFrame):
        bbg_month[key] = pd.Series(bbg_month[key].iloc[:, 0])
prices_df = pd.DataFrame.from_dict(bbg_month)
prices_diff = prices_df.pct_change().dropna()

col_ref = {}
col_ref['aco'] = ['exportacoes por produto_USD_Produtos metalicos, n.e.p.']
col_ref['petroleo'] = ['exportacoes por produto_USD_Petroleo, produtos petroliferos e materiais relacionados']
col_ref['celulose'] = ['exportacoes por produto_USD_Papel, cartao e artigos de pasta de celulose, de papel ou de cartao',
                       'exportacoes por produto_USD_Celulose e residuos de papel']
col_ref['ouro'] = ['exportacoes por produto_USD_Ouro, nao monetario (excluindo minerios de ouro e seus concentrados)']
col_ref['minerio'] = ['exportacoes por produto_USD_Minerios metalicos e sucata']

col_ref['soja'] = ['exportacoes por produto_USD_Gorduras e oleos vegetais, em bruto, refinados ou fracionados',
                   'exportacoes por produto_USD_Cereais e preparacoes de cereais', 'exportacoes por produto_USD_Alimentos para animais (nao incluindo cereais nao moidos)',
                   'exportacoes por produto_USD_Sementes e frutos oleaginosos', 'exportacoes por produto_USD_Oleos e gorduras animais'
                   ]

col_ref['aco'] = ['exportacoes por produto_USD_Ferro e aco', 'exportacoes por produto_USD_Equipamentos metalurgicos'
                   ]
col_ref['cafe'] = ['exportacoes por produto_USD_Cafe, cha, cacau, especiarias, e respectivos produtos'
                   ]
col_ref['boi'] = ['exportacoes por produto_USD_Animais vivos nao incluidos no capitulo 03',
                  'exportacoes por produto_USD_Carne e preparacoes de carne']
col_ref['acucar'] = ['exportacoes por produto_USD_Acucares, preparacoes de acucar e mel']
col_ref['algodao'] = ['exportacoes por produto_USD_Fibras texteis(exc. tops de la e outra la penteada)e seus residuos(nao transformados em fios/tecido)']

wgt_df = prices_diff.copy()
for col in wgt_df:
    df_aux = df_prop.loc[prices_diff.index, col_ref[col]].fillna(method='ffill')
    for i in range(len(df_aux.columns)):
        if i == 0:
            soma = df_aux.loc[:, df_aux.columns[i]]
        else:
            soma = soma + df_aux.loc[:, df_aux.columns[i]]
    wgt_df[col] = soma

for i in range(len(wgt_df)):
    wgt_df.iloc[i, :] = wgt_df.iloc[i, :] / sum(wgt_df.iloc[i, :])

compos_df = prices_diff.mul(wgt_df)

price_index_diff = compos_df.sum(axis=1)
price_index_diff.name = 'diff'
price_index = pd.Series(index=price_index_diff.index)
price_index.name = 'indice'
for i in range(len(price_index)):
    if i == 0:
        price_index[i] = 100
    else:
        price_index[i] = price_index[i-1]*(1 + price_index_diff[i])

final_df = pd.concat([price_index, price_index_diff], axis=1)

wb = xw.Book(r'F:\DADOS\ASSET\MACROECONOMIA\DADOS\Setor_Externo\FUNCEX\PRECOS_DE_EXPORTACAO_SAFRA.xlsx')
sht = wb.sheets('dados exportacao')
sht.range('A1').value = df
sht.range('BP1').value = df_prop
sht2 = wb.sheets('IPE')
sht2.range('a1').value = final_df

