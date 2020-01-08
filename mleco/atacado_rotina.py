# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 10:01:20 2019

@author: marcgut
"""

import sys
sys.path.append(r'Z:\Macroeconomia\codes\Projetos\Inflacao\Atacado')
sys.path.append(r'Z:\Macroeconomia\codes')
import xlwings as xw
from atacado_functions import *
from atacado_agrupamento import *
from atacado_models import *
import econuteis as eu
import pandas as pd
import numpy as np


###############################################################################
########################## R O D A R  M O D E L O S ###########################
############## True se sim, False se apenas carregar já rodados ###############

RERUN = True

###############################################################################




WS = import_ws_db()
ws_ponta = eu.rename_duplicate_columns(WS.rolling(7).mean().pct_change(30))
ws_media = eu.rename_duplicate_columns(WS.rolling(30).mean().pct_change(30))
base_media, base_ponta, ipca_peso, ipca_var = import_monit_db()



pred = {}
# RODANDO MODELOS
# Cereais : 1101
defasagem = [10, 15, 20, 25, 30, 45, 60]
ref = ('cereais', '1101')

pred[int(ref[1])] = model_creator(ref, defasagem, ws_ponta, base_ponta, with_comm=True,
                     y_lags=None, extra_covar=None).run(RERUN)


# Farinhas : 1102
defasagem = [10, 15, 20, 25, 30, 45, 60]
ref = ('farinhas', '1102')

pred[int(ref[1])] = model_creator(ref, defasagem, ws_ponta, base_ponta, with_comm=True,
                     y_lags=None, extra_covar=None).run(RERUN)

# Tubérculos : 1103
defasagem = [10, 15, 20, 25, 30, 45, 60]
ref = ('tuberculos', '1103')

pred[int(ref[1])] = model_creator(ref, defasagem, ws_ponta, base_ponta, with_comm=True,
                     y_lags=None, extra_covar=None).run(RERUN)

# Açúcares : 1104
defasagem = [10, 15, 20, 25, 30, 45, 60]
ref = ('açucares', '1104')

pred[int(ref[1])] = model_creator(ref, defasagem, ws_ponta, base_ponta, with_comm=True,
                     y_lags=None, extra_covar=None).run(RERUN)

# Hortaliças : 1105
defasagem = [10, 15, 20, 25, 30, 45, 60]
ref = ('hortaliças', '1105')

pred[int(ref[1])] = model_creator(ref, defasagem, ws_ponta, base_ponta, with_comm=True,
                     y_lags=None, extra_covar=None).run(RERUN)

# Frutas : 1106
defasagem = [10, 15, 20, 25, 30, 45, 60]
ref = ('frutas', '1106')

pred[int(ref[1])] = model_creator(ref, defasagem, ws_ponta, base_ponta, with_comm=True,
                     y_lags=None, extra_covar=None).run(RERUN)

# Carnes : 1107
defasagem = [10, 15, 20, 25, 30, 45, 60]
ref = ('carnes', '1107')

pred[int(ref[1])] = model_creator(ref, defasagem, ws_ponta, base_ponta, with_comm=True,
                     y_lags=None, extra_covar=None).run(RERUN)

# Pescados : 1108
defasagem = [10, 15, 20, 25, 30, 45, 60]
ref = ('pescados', '1108')

pred[int(ref[1])] = model_creator(ref, defasagem, ws_ponta, base_ponta, with_comm=True,
                     y_lags=None, extra_covar=None).run(RERUN)

# Industrializados : 1109
defasagem = [10, 15, 20, 25, 30, 45, 60]
ref = ('industrializados', '1109')

pred[int(ref[1])] = model_creator(ref, defasagem, ws_ponta, base_ponta, with_comm=True,
                     y_lags=None, extra_covar=None).run(RERUN)

# Aves : 1110
defasagem = [10, 15, 20, 25, 30, 45, 60]
ref = ('aves', '1110')

pred[int(ref[1])] = model_creator(ref, defasagem, ws_ponta, base_ponta, with_comm=True,
                     y_lags=None, extra_covar=None).run(RERUN)

# Leites : 1111
defasagem = [10, 15, 20, 25, 30, 45, 60]
ref = ('leites', '1111')

pred[int(ref[1])] = model_creator(ref, defasagem, ws_ponta, base_ponta, with_comm=True,
                     y_lags=None, extra_covar=None).run(RERUN)

# Panificados : 1112
defasagem = [10, 15, 20, 25, 30, 45, 60]
ref = ('panificados', '1112')

pred[int(ref[1])] = model_creator(ref, defasagem, ws_ponta, base_ponta, with_comm=True,
                     y_lags=None, extra_covar=None).run(RERUN)

# óleos : 1113
defasagem = [10, 15, 20, 25, 30, 45, 60]
ref = ('oleos', '1113')

pred[int(ref[1])] = model_creator(ref, defasagem, ws_ponta, base_ponta, with_comm=True,
                     y_lags=None, extra_covar=None).run(RERUN)

# Bebidas : 1114
defasagem = [10, 15, 20, 25, 30, 45, 60]
ref = ('bebidas', '1114')

pred[int(ref[1])] = model_creator(ref, defasagem, ws_ponta, base_ponta, with_comm=True,
                     y_lags=None, extra_covar=None).run(RERUN)

# Conserva : 1115
defasagem = [10, 15, 20, 25, 30, 45, 60]
ref = ('conserva', '1115')

pred[int(ref[1])] = model_creator(ref, defasagem, ws_ponta, base_ponta, with_comm=True,
                     y_lags=None, extra_covar=None).run(RERUN)

# Condimentos : 1116
defasagem = [10, 15, 20, 25, 30, 45, 60]
ref = ('condimentos', '1116')

pred[int(ref[1])] = model_creator(ref, defasagem, ws_ponta, base_ponta, with_comm=True,
                     y_lags=None, extra_covar=None).run(RERUN)


############################ COMPONDO PROJEÇÕES ###############################
pred = pd.DataFrame(pred)

pesos = ipca_peso.loc[:, pred.columns].align(pred, axis=0, join='outer', method='pad')[0]

alim_dom = pd.Series(index=pred.index, name=11)

for date in alim_dom.index:
    alim_dom.loc[date] = np.sum(pred.loc[date,:].mul(pesos.loc[date,:],axis='index'))/np.sum(pesos.loc[date,:])

pred = pd.concat([alim_dom, pred], axis=1)


##################### ACOMPANHAMENTO ATACADO GERAL (sem modelo) ###############
ref_itens = make_ref()
groups = make_groups()

atac_media = {}
atac_ponta = {}

# Compondo itens (tirando a média simples dos produtos do atacado correspondentes)
for ituple in ref_itens:
    iref = ituple[1]
    atac_media[int(iref)] = pd.Series(np.mean(ws_media.loc[:,ref_itens[ituple]], axis=1),
                                 index=ws_media.index, name=int(iref))
    atac_ponta[int(iref)] = pd.Series(np.mean(ws_ponta.loc[:,ref_itens[ituple]], axis=1),
                                 index=ws_ponta.index, name=int(iref))
    
# Compondo grupos (a partir dos itens)
for ituple in groups:
    if ituple == 'commodities_gerais':
        pass
    elif groups[ituple] == []:
        pass
    else:
        group_media = {}
        group_ponta = {}
        for item in ref_itens:
            if item[1][:4] == ituple[1]:
                group_media[int(item[1])] = atac_media[int(item[1])]
                group_ponta[int(item[1])] = atac_ponta[int(item[1])]
        group_media = pd.DataFrame(group_media)
        group_ponta = pd.DataFrame(group_ponta)
        pesos = ipca_peso.loc[:, group_media.columns].align(group_media, axis=0, join='outer', method='pad')[0]
        gmedia_fin = pd.Series(index=group_media.index, name=ituple[1])
        gponta_fin = pd.Series(index=group_ponta.index, name=ituple[1])
        for date in gmedia_fin.index:
            gmedia_fin.loc[date] = np.sum(group_media.loc[date,:].mul(pesos.loc[date,:],axis='index'))/np.sum(pesos.loc[date,:])
            gponta_fin.loc[date] = np.sum(group_ponta.loc[date,:].mul(pesos.loc[date,:],axis='index'))/np.sum(pesos.loc[date,:])
        atac_media[int(ituple[1])] = gmedia_fin
        atac_ponta[int(ituple[1])] = gponta_fin

# Compondo alimentação no domicílio geral
aux_med = {}
aux_ponta = {}
for ituple in groups:
    if ituple == 'commodities_gerais':
        pass
    else:
        iref = int(ituple[1])
        aux_med[iref] = atac_media[iref]
        aux_ponta[iref] = atac_ponta[iref]
    
aux_med = pd.DataFrame(aux_med).dropna(axis=1, how='all')
aux_ponta = pd.DataFrame(aux_ponta).dropna(axis=1, how='all')
pesos = ipca_peso.loc[:, aux_med.columns].align(aux_med, axis=0, join='outer', method='pad')[0]
pesos = pesos.dropna()
aux_med = aux_med.loc[pesos.index[0]:, :]
aux_ponta = aux_ponta.loc[pesos.index[0]:, :]

atac_geral_med = pd.Series(index=aux_med.index, name=11)
atac_geral_ponta = pd.Series(index=aux_ponta.index, name=11)

for date in atac_geral_med.index:
    atac_geral_med.loc[date] = np.sum(aux_med.loc[date,:].mul(pesos.loc[date,:],axis='index'))/np.sum(pesos.loc[date,:])
    atac_geral_ponta.loc[date] = np.sum(aux_ponta.loc[date,:].mul(pesos.loc[date,:],axis='index'))/np.sum(pesos.loc[date,:])

atac_media[11] = atac_geral_med
atac_ponta[11] = atac_geral_ponta

atac_media = pd.DataFrame(atac_media).dropna(axis=1, how='all')
atac_ponta = pd.DataFrame(atac_ponta).dropna(axis=1, how='all')



# Para os gráficos
ipca_var_align = ipca_var.align(atac_media, join='outer', axis=0)[0]
monitor_align = base_ponta.align(atac_media, join='outer', axis=0, method='pad')[0]

ipca_var_align = ipca_var_align.loc[:, atac_media.columns].dropna(axis=1, how='all')
monitor_align = monitor_align.loc[:, atac_media.columns].dropna(axis=1, how='all')

# Cálculo média histórica
atac_med_mes, atac_std_top, atac_std_min = mth_avg_hist(atac_media)


################################# PARA O EXCEL ################################
wb = xw.Book(r'F:\DADOS\ASSET\MACROECONOMIA\DADOS\Inflação\ATACADO\ATACADO.xlsm')
sheet_pred = wb.sheets('pred')
sheet_pred.range('a1').value = pred

sheet_ipca = wb.sheets('ipca_var')
sheet_ipca.range('a1').value = ipca_var_align

sheet_monit = wb.sheets('monit')
sheet_monit.range('a1').value = monitor_align

sheet_media = wb.sheets('geral_media')
sheet_media.range('a1').value = atac_media

sheet_ponta = wb.sheets('geral_ponta')
sheet_ponta.range('a1').value = atac_ponta

sheet_med_mes = wb.sheets('atac_media_mensal')
sheet_med_mes.range('a1').value = atac_med_mes

sheet_std_top = wb.sheets('atac_std_top')
sheet_std_top.range('a1').value = atac_std_top

sheet_std_min = wb.sheets('atac_std_min')
sheet_std_min.range('a1').value = atac_std_min


# Colando referências aos itens
all_ref = list(groups.keys()) + list(ref_itens.keys())
all_ref.remove('commodities_gerais')
names = []
ref = []
for ituple in all_ref:
    names.append(ituple[0])
    ref.append(ituple[1])
ref_as = pd.Series(names, index=ref, name='ref')

sheet_ref = wb.sheets('ref')
sheet_ref.range('a1').value = ref_as





