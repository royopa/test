# -*- coding: utf-8 -*-
"""
Created on Fri Jan  3 09:07:16 2020

@author: marcgut
"""


import pandas as pd
import sys
import xlwings as xw
sys.path.append(r'Z:\Macroeconomia\codes')
import econuteis as eu

base = pd.read_excel(
        r'F:\DADOS\ASSET\MACROECONOMIA\DADOS\Atividade\VEÍCULOS\FENABRAVE_diario.xlsx',
        sheet_name='dessaz', header=0, index_col=0)

base = base.iloc[:, 0:4]

auto = base.loc[:, 'Auto']/base.loc[:, 'DU']
auto.name = 'auto'
leves = base.loc[:, 'CL']/base.loc[:, 'DU']
leves.name = 'leves'
caminhoes = base.loc[:, 'Caminhões']/base.loc[:, 'DU']
caminhoes.name = 'caminhoes'

auto_leves = auto + leves
auto_leves.name = 'auto_leves'

df = pd.concat([auto, leves, auto_leves, caminhoes], axis=1)

df_out = eu.dessaz_df(df)


wb = xw.Book(r'F:\DADOS\ASSET\MACROECONOMIA\DADOS\Atividade\VEÍCULOS\FENABRAVE_diario.xlsx')
wb.sheets('dessaz').range('G1').value = df_out
























