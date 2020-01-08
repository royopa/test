# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 12:34:33 2019

@author: marcgut

PCA de Atividade Brasil
"""

import pandas as pd   # Pacote de análise de dados (inclusive leitura de excel)
import sys  # Funcionalidades do sistema (incluindo caminhos)
sys.path.append(r'Z:\Macroeconomia\databases\MCM')
sys.path.append(r'Z:\Macroeconomia\codes')  # Modulo com funções úteis
import econuteis as eu
import numpy as np
from funcoes_data_mcm_mult import mcm_base
from statsmodels.multivariate.pca import PCA
import xlwings as xw
import seaborn as sns
from scrapping_MCM import download_mcm_db

###############################################################################
############################### F U N Ç Õ E S #################################
###############################################################################
# FUNÇÃO QUE PEGA AS SÉRIES USADAS NO PCA E RETORNA UM DATAFRAME ÚNICO
def pca_dataf(data_base, list_plan_ref):
    """FUNÇÃO PEGA A BASE DE DADOS EM DICIONÁRIO (COMO OUTPUT DA FUNÇÃO
    MCM_BASE) E JUNTA OS DADOS QUE SERÃO UTILIZADOS EM UM DATA FRAME ÚNICO"""

    # Planilha 120: Estoque de crédito
    ref = list_plan_ref[0]
    sheet = 'PF'

    try:
        number = ref[0]
    except TypeError:
        number = ref

    df = eu.name_df(data_base[ref][sheet][0], str(number) + '_' + sheet)

    df = df[df.columns.drop(list(df.filter(regex='Total')))]  # Dropa as totais

    sheet = 'PJ'

    df = pd.concat([df, eu.name_df(data_base[ref][sheet][0],
                                   str(number) + '_' + sheet)], axis=1)

    df = df[df.columns.drop(list(df.filter(regex='Total')))]  # Dropa as totais

    df = eu.dessaz_df(eu.deflate_df(df))  # Deflaciona e dessaz as séries

    # Planilha 116: Concessão
    ref = list_plan_ref[1]

    try:
        number = ref[0]
    except TypeError:
        number = ref

    sheet = ref[1]

    df_aux = data_base[ref][sheet][0]

    df_aux = eu.dessaz_df(eu.deflate_df(df_aux))  # Deflaciona e dessaz as
    #                                               séries

    df = pd.concat([df, eu.name_df(df_aux, str(number) + '_' + sheet)],
                   axis=1)

    sheet = ref[2]

    df_aux = data_base[ref][sheet][0]

    df_aux = eu.dessaz_df(eu.deflate_df(df_aux))  # Deflaciona e dessaz as
    #                                               séries

    df = pd.concat([df, eu.name_df(df_aux, str(number) + '_' + sheet)],
                   axis=1)

    for i in range(3, len(ref)):
        sheet = ref[i]
        df_aux = data_base[ref][sheet][0]
        df = pd.concat([df, eu.name_df(df_aux, str(number) + '_' + sheet)],
                       axis=1)

    df = df[df.columns.drop(list(df.filter(regex='Total')))]

    # Planilha 25
    ref = list_plan_ref[2]

    try:
        number = ref[0]
    except TypeError:
        number = ref

    sheet = ref[1]

    df_aux = data_base[ref][sheet][0]

    df_aux = eu.dessaz_df(df_aux)  # dessaz as séries

    df = pd.concat([df, eu.name_df(df_aux, str(number) + '_' + sheet)],
                   axis=1)

    # Planilha 52
    ref = list_plan_ref[3]

    try:
        number = ref[0]
    except TypeError:
        number = ref

    sheet = 'Serasa'

    df_aux = data_base[ref][sheet][0]

    df_aux = df_aux[df_aux.columns.drop(list(df_aux.filter(regex='Concordatas'
                                                           )))]

    df_aux = df_aux[df_aux.columns.drop(list(df_aux.filter(regex='Recuperações'
                                                           )))]

    df_aux = eu.dessaz_df(df_aux)  # dessaz as séries

    df = pd.concat([df, eu.name_df(df_aux, str(number) + '_' + sheet)],
                   axis=1)

    # Planilha 18
    ref = list_plan_ref[4]

    try:
        number = ref[0]
    except TypeError:
        number = ref

    for i in range(1, len(ref)):
        sheet = ref[i]
        df_aux = data_base[ref][sheet][0]
        df_aux = eu.dessaz_df(df_aux)  # dessaz as séries
        df = pd.concat([df, eu.name_df(df_aux, str(number) + '_' + sheet)],
                       axis=1)

    df = df[df.columns.drop(list(df.filter(regex='TOTAL')))]

    # Planilha 24
    ref = list_plan_ref[5]

    try:
        number = ref[0]
    except TypeError:
        number = ref

    sheet = 'Indic. do Mercado de Trabalho'

    df_aux = data_base[ref][sheet][0]

    df_aux = eu.dessaz_df(df_aux)  # dessaz as séries

    df = pd.concat([df, eu.name_df(df_aux, str(number) + '_' + sheet)],
                   axis=1)

    # Planilha 253
    ref = list_plan_ref[6]

    try:
        number = ref[0]
    except TypeError:
        number = ref

    sheet = 'ICE'

    df_aux = data_base[ref][sheet][0]
    df_aux = df_aux.iloc[:, -2:]  # Dropa as duas últimas col
    df_aux = eu.dessaz_df(df_aux)  # dessaz as séries

    df = pd.concat([df, eu.name_df(df_aux, str(number) + '_' + sheet)],
                   axis=1)

    # Planilha 237
    ref = list_plan_ref[7]

    try:
        number = ref[0]
    except TypeError:
        number = ref

    sheet = 'IIE-Br'

    df_aux = data_base[ref][sheet][0]
    df_aux = eu.dessaz_df(df_aux)  # dessaz as séries

    df = pd.concat([df, eu.name_df(df_aux, str(number) + '_' + sheet)],
                   axis=1)

    # Planilha 228
    ref = list_plan_ref[8]

    try:
        number = ref[0]
    except TypeError:
        number = ref

    sheet = 'Serviços'

    df_aux = data_base[ref][sheet][0]
    df_aux = df_aux.iloc[:, 4:6]
    df_aux = eu.dessaz_df(df_aux)  # dessaz as séries

    df = pd.concat([df, eu.name_df(df_aux, str(number) + '_' + sheet)],
                   axis=1)

    # Planilha 227
    ref = list_plan_ref[9]

    try:
        number = ref[0]
    except TypeError:
        number = ref

    sheet = 'Indústria'

    df_aux = data_base[ref][sheet][0]
    df_aux = df_aux[df_aux.columns.drop(list(df_aux.filter(
             regex='Com Ajuste')))]
    df_aux = df_aux[df_aux.columns.drop(list(df_aux.filter(
             regex='com Ajuste')))]
    df_aux = df_aux.iloc[:, 1:]
    df_aux = eu.dessaz_df(df_aux)  # dessaz as séries

    df = pd.concat([df, eu.name_df(df_aux, str(number) + '_' + sheet)],
                   axis=1)

    # Planilha 198
    ref = list_plan_ref[10]

    try:
        number = ref[0]
    except TypeError:
        number = ref

    sheet = 'Mov. do Comércio'

    df_aux = data_base[ref][sheet][0]

    df_aux = df_aux[df_aux.columns.drop(list(df_aux.filter(
             regex='Geral')))]

    df_aux = eu.dessaz_df(df_aux)  # dessaz as séries

    df = pd.concat([df, eu.name_df(df_aux, str(number) + '_' + sheet)],
                   axis=1)

    # Planilha 224
    ref = list_plan_ref[11]

    try:
        number = ref[0]
    except TypeError:
        number = ref

    sheet = 'Construção'
    
    df_aux = data_base[ref][sheet][0]

    df_aux = df_aux.iloc[:, 4:6]

    df_aux = eu.dessaz_df(df_aux)  # dessaz as séries

    df = pd.concat([df, eu.name_df(df_aux, str(number) + '_' + sheet)],
                   axis=1)

    # Planilha 225
    ref = list_plan_ref[12]

    try:
        number = ref[0]
    except TypeError:
        number = ref

    sheet = 'Comércio'
    
    df_aux = data_base[ref][sheet][0]

    df_aux = df_aux.iloc[:, 4:]

    df_aux = eu.dessaz_df(df_aux)  # dessaz as séries

    df = pd.concat([df, eu.name_df(df_aux, str(number) + '_' + sheet)],
                   axis=1)

    # Planilha 14
    ref = list_plan_ref[13]

    try:
        number = ref[0]
    except TypeError:
        number = ref

    sheet = 'Expectativa'
    
    df_aux = data_base[ref][sheet][0]

    df_aux = df_aux.iloc[:, :21]

    df_aux = df_aux[df_aux.columns.drop(list(df_aux.filter(
             regex='Total')))]

    df_aux = eu.dessaz_df(df_aux)  # dessaz as séries

    df = pd.concat([df, eu.name_df(df_aux, str(number) + '_' + sheet)],
                   axis=1)

    # Planilha 20
    ref = list_plan_ref[14]

    try:
        number = ref[0]
    except TypeError:
        number = ref

    sheet = 'Índice de Confiança Consumidor'

    df_aux = data_base[ref][sheet][0]

    df_aux = df_aux.iloc[:, 1:3]

    df_aux = eu.dessaz_df(df_aux)  # dessaz as séries

    df = pd.concat([df, eu.name_df(df_aux, str(number) + '_' + sheet)],
                   axis=1)

    # Planilha 13
    ref = list_plan_ref[15]

    try:
        number = ref[0]
    except TypeError:
        number = ref

    sheet = 'Geral'

    df_aux = data_base[ref][sheet][0]

    df_aux = df_aux.dropna(axis=1, how='any')

    df_aux = eu.dessaz_df(df_aux)  # dessaz as séries

    df = pd.concat([df, eu.name_df(df_aux, str(number) + '_' + sheet)],
                   axis=1)

    # Planilha 9
    ref = list_plan_ref[16]

    try:
        number = ref[0]
    except TypeError:
        number = ref

    sheet = 'ICEI - Condições Atuais'

    df_aux = data_base[ref][sheet][0]

    df_aux = df_aux.dropna(axis=1, how='all')

    df_aux = df_aux.drop(df_aux.columns[[0, 1, 5, 6, 8, 18, 20, 32, 35]],
                         axis=1)

    df_aux = eu.dessaz_df(df_aux)  # dessaz as séries

    df = pd.concat([df, eu.name_df(df_aux, str(number) + '_' + sheet)],
                   axis=1)

    sheet = 'ICEI - Expectativas'

    df_aux = data_base[ref][sheet][0]

    df_aux = df_aux.dropna(axis=1, how='all')

    df_aux = df_aux.drop(df_aux.columns[[0, 1, 5, 6, 8, 18, 32, 35]], axis=1)

    df_aux = eu.dessaz_df(df_aux)  # dessaz as séries

    df = pd.concat([df, eu.name_df(df_aux, str(number) + '_' + sheet)],
                   axis=1)

    sheet = 'ICEI - Grandes empresas'

    df_aux = data_base[ref][sheet][0]

    df_aux = df_aux.dropna(axis=1, how='all')

    df_aux = df_aux.drop(df_aux.columns[[0]], axis=1)

    df_aux = df_aux[df_aux.columns.drop(list(df_aux.filter(
             regex='Geral')))]

    df_aux = eu.dessaz_df(df_aux)  # dessaz as séries

    df = pd.concat([df, eu.name_df(df_aux, str(number) + '_' + sheet)],
                   axis=1)

    sheet = 'ICEI - Médias empresas'

    df_aux = data_base[ref][sheet][0]

    df_aux = df_aux.dropna(axis=1, how='all')

    df_aux = df_aux.drop(df_aux.columns[[0]], axis=1)

    df_aux = df_aux[df_aux.columns.drop(list(df_aux.filter(
             regex='Geral')))]

    df_aux = eu.dessaz_df(df_aux)  # dessaz as séries

    df = pd.concat([df, eu.name_df(df_aux, str(number) + '_' + sheet)],
                   axis=1)

    sheet = 'ICEI - Pequenas empresas'

    df_aux = data_base[ref][sheet][0]

    df_aux = df_aux.dropna(axis=1, how='all')

    df_aux = df_aux.drop(df_aux.columns[[0]], axis=1)

    df_aux = df_aux[df_aux.columns.drop(list(df_aux.filter(
             regex='Geral')))]

    df_aux = eu.dessaz_df(df_aux)  # dessaz as séries

    df = pd.concat([df, eu.name_df(df_aux, str(number) + '_' + sheet)],
                   axis=1)

    # Planilha 49
    ref = list_plan_ref[17]

    try:
        number = ref[0]
    except TypeError:
        number = ref

    sheet = 'Sem Ajuste Sazonal'

    df_aux = data_base[ref][sheet][0]

    df_aux = df_aux[df_aux.columns.drop(list(df_aux.filter(
             regex='Geral')))]

    df_aux = eu.dessaz_df(df_aux)  # dessaz as séries

    df = pd.concat([df, eu.name_df(df_aux, str(number) + '_' + sheet)],
                   axis=1)

    # Planilha 133
    ref = list_plan_ref[18]

    try:
        number = ref[0]
    except TypeError:
        number = ref

    sheet = 'Importações'

    df_aux = data_base[ref][sheet][0]

    df_aux = df_aux.filter(regex='Quantum')

    df_aux = df_aux.iloc[:, 1:]

    df_aux = eu.dessaz_df(df_aux)  # dessaz as séries

    df = pd.concat([df, eu.name_df(df_aux, str(number) + '_' + sheet)],
                   axis=1)

    # Planilha 59
    ref = list_plan_ref[19]

    try:
        number = ref[0]
    except TypeError:
        number = ref

    sheet = 'ABPO - Nova Base'

    df_aux = data_base[ref][sheet][0]

    df_aux = df_aux[df_aux.columns.drop(list(df_aux.filter(
             regex='TOTAL')))]
    
    df_aux = eu.dessaz_df(df_aux)  # dessaz as séries

    df = pd.concat([df, eu.name_df(df_aux, str(number) + '_' + sheet)],
                   axis=1)

    # Planilha 71
    ref = list_plan_ref[20]

    try:
        number = ref[0]
    except TypeError:
        number = ref

    sheet = 'Consumo aparente de cimento'

    df_aux = data_base[ref][sheet][0]

    df_aux = eu.dessaz_df(df_aux)  # dessaz as séries

    df = pd.concat([df, eu.name_df(df_aux, str(number) + '_' + sheet)],
                   axis=1)

    # Planilha 64
    ref = list_plan_ref[21]

    try:
        number = ref[0]
    except TypeError:
        number = ref

    sheet = 'ABCR'

    df_aux = data_base[ref][sheet][0]

    df_aux = df_aux[df_aux.columns.drop(list(df_aux.filter(
             regex='Dessazonalizada')))]

    df_aux = df_aux[df_aux.columns.drop(list(df_aux.filter(
             regex='Total')))]

    df_aux = eu.dessaz_df(df_aux)  # dessaz as séries

    df = pd.concat([df, eu.name_df(df_aux, str(number) + '_' + sheet)],
                   axis=1)

    # Planilha 61
    ref = list_plan_ref[22]

    try:
        number = ref[0]
    except TypeError:
        number = ref

    sheet = 'Produção'

    df_aux = data_base[ref][sheet][0]

    df_aux = df_aux[df_aux.columns.drop(list(df_aux.filter(
             regex='Total')))]
    
    df_aux = df_aux.loc['1990-01-01':, :]
    
    df_aux = eu.dessaz_df(df_aux)  # dessaz as séries

    df = pd.concat([df, eu.name_df(df_aux, str(number) + '_' + sheet)],
                   axis=1)

    sheet = 'Vendas ao Mercado Interno'

    df_aux = data_base[ref][sheet][0]

    df_aux = df_aux[df_aux.columns.drop(list(df_aux.filter(
             regex='Total')))]

    df_aux = df_aux[df_aux.columns.drop(list(df_aux.filter(
             regex='Importados')))]
    
    df_aux = df_aux.loc['1990-01-01':, :]
    
    df_aux = eu.dessaz_df(df_aux)  # dessaz as séries

    df = pd.concat([df, eu.name_df(df_aux, str(number) + '_' + sheet)],
                   axis=1)

    sheet = 'Emprego no setor'

    df_aux = data_base[ref][sheet][0]

    df_aux = df_aux[df_aux.columns.drop(list(df_aux.filter(
             regex='Total')))]
    
    df_aux = df_aux.loc['1990-01-01':, :]
    
    df_aux = eu.dessaz_df(df_aux)  # dessaz as séries

    df = pd.concat([df, eu.name_df(df_aux, str(number) + '_' + sheet)],
                   axis=1)
    
    # Planilha 205
    ref = list_plan_ref[23]

    try:
        number = ref[0]
    except TypeError:
        number = ref

    sheet = 'Produção'

    df_aux = data_base[ref][sheet][0]

    df_aux = eu.dessaz_df(df_aux)  # dessaz as séries

    df = pd.concat([df, eu.name_df(df_aux, str(number) + '_' + sheet)],
                   axis=1)

    sheet = 'Refino'

    df_aux = data_base[ref][sheet][0]

    df_aux = eu.dessaz_df(df_aux)  # dessaz as séries

    df = pd.concat([df, eu.name_df(df_aux, str(number) + '_' + sheet)],
                   axis=1)
    
    # Planilha 60
    ref = list_plan_ref[24]

    try:
        number = ref[0]
    except TypeError:
        number = ref

    sheet = 'ABRAS'
    
    df_aux = data_base[ref][sheet][0]

    df_aux = df_aux.iloc[:, 1]
    
    df_aux = eu.deflate_df(eu.dessaz_df(df_aux))  # dessaz as séries
    
    df = pd.concat([df, eu.name_df(df_aux, str(number) + '_' + sheet)],
                   axis=1)

    # Planilha 75
    ref = list_plan_ref[25]

    try:
        number = ref[0]
    except TypeError:
        number = ref

    sheet = 'ABAL'

    df_aux = data_base[ref][sheet][0]

    df_aux = df_aux.iloc[:, 0]

    df_aux = eu.dessaz_df(df_aux)  # dessaz as séries

    df = pd.concat([df, eu.name_df(df_aux, str(number) + '_' + sheet)],
                   axis=1)

    # Planilha 73
    ref = list_plan_ref[26]

    try:
        number = ref[0]
    except TypeError:
        number = ref

    sheet = 'IBS'

    df_aux = data_base[ref][sheet][0]

    df_aux = df_aux.drop(df_aux.columns[[4, 5, 6]], axis=1)
    
    df_aux = df_aux.loc['1990-01-01':, :]

    df_aux = eu.dessaz_df(df_aux)  # dessaz as séries

    df = pd.concat([df, eu.name_df(df_aux, str(number) + '_' + sheet)],
                   axis=1)
    
    # Planilha 117
    ref = list_plan_ref[27]

    try:
        number = ref[0]
    except TypeError:
        number = ref

    sheet = ref[1]

    df_aux = data_base[ref][sheet][0]
    
    df_aux = df_aux.loc['1996-01-01':, '_Meios de pagamento (A+B)']

    df_aux = eu.deflate_df(eu.dessaz_df(df_aux))
    
    df = pd.concat([df, eu.name_df(df_aux, str(number) + '_' + sheet)],
                   axis=1)

    return df

def update_db(list_plan_ref):
    plan_list = []
    for el in list_plan_ref:
        if isinstance(el, tuple):
            plan_list.append(el[0])
        else:
            plan_list.append(el)
    
    for plan in plan_list:
        download_mcm_db(plan)

###############################################################################
############################## CÓDIGO DE FATO #################################
###############################################################################
# Planilhas utilizadas
list_plan_ref = [120, (116, 'Concessões (Livres)', 'Concessões (Direcionados)',
                       'Taxas de Juros (Livres)',
                       'Taxas de Juros (Direcionados)', 'Spreads',
                       'Atrasos (Livres)', 'Atrasos (Direcionados)',
                       'Inadimplência (Livres)',
                       'Inadimplência (Direcionados)'), 
                 (25, 'Setores - Originais'), 52,
                 (18, 'Confiança do Consumidor', 'Condições Atuais',
                 'Expectativas do Consumidor'),
                 24, 253, 237, 228, 227,
                 (198, 'Mov. do Comércio'), 224,
                 225, (14, 'Expectativa'), 20, (13, 'Geral'), 9,
                 (49, 'Sem Ajuste Sazonal'), (133, 'Exportações',
                 'Importações'),
                 (59, 'ABPO - Nova Base'), (71, 'Consumo aparente de cimento')
                 , 64, (61, 'Produção', 'Vendas ao Mercado Interno',
                 'Emprego no setor'), (205, 'Produção', 'Refino'),
                 (60, 'ABRAS'), 75, (73, 'IBS'),
                 (117, 'M1 - Média dos saldos (R$)')]


# Atualiza Base de dados
update_db(list_plan_ref)

# Base de dados "crua"
data_base = mcm_base(list_plan_ref)

# Base de dados trabalhada e unificada num DF
df = pca_dataf(data_base, list_plan_ref)  # Essa parte demora bem
df = df.loc['1996-01-01':, :]
#adf_res = eu.adf_test(df)  # resultados do teste adf para cada série
df_t = df.copy()  # copia da df para os dados transformados

for i, series in enumerate(df):
    if any(df[series]<=0):
        df_t[series] = df[series].diff()
    else:
        df_t[series] = df[series].pct_change(fill_method=None)

df_t = df_t.dropna(axis=0, how='all')

pc = PCA(df, ncomp=1, standardize=True, missing='fill-em')
pc_t = PCA(df_t, ncomp=1, standardize=True, missing='fill-em')

wb = xw.Book(r'F:\DADOS\ASSET\MACROECONOMIA\DADOS\Atividade\PCA\PCA_ativ.xlsm')
sht = wb.sheets['pca']
sht_d = wb.sheets['pca_d']
sht.range('A1').value = pc.scores
sht_d.range('A1').value = pc_t.scores


# ANÁLISE DE DADOS QUE JÁ SAÍRAM
last = pd.DataFrame(df.iloc[-1, :]).T
last = last.dropna(axis=1)

df_last = df.filter(items=last.columns)
df_tlast = df_last.copy()
for i, series in enumerate(df_last):
    if any(df_last[series]<=0):
        df_tlast[series] = df_last[series].diff()
    else:
        df_tlast[series] = df_last[series].pct_change(fill_method=None)

df_tlast = df_tlast.dropna(axis=0, how='all')
pc_last = PCA(df_tlast, ncomp=1, standardize=True, missing='fill-em')

sht_d.range('D1').value = pc_last.scores


# SINCRONIA
normalize_df = (df_t - df_t.mean())/df_t.std()
sinc = normalize_df.std(axis=1)
sht_s = wb.sheets['sinc']
sht_s.range('A2').value = sinc

# HEATMAP




