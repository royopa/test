# -*- coding: utf-8 -*-
"""
Created on Tue Apr 30 15:46:12 2019

@author: marcgut
"""
import pandas as pd
import sys
import xlwings as xw
sys.path.append(r'Z:\Macroeconomia\codes')
import econuteis as eu

base = pd.read_excel(
        r'F:\DADOS\ASSET\MACROECONOMIA\DADOS\Atividade\TRABALHO\PNAD\Desemprego por Escolaridade.xlsx',
        sheet_name='python', header=0, index_col=0)

base_desemp = base.iloc[:, :8]

base_renda = base[base.columns[9:]]

base_desemp_sa = eu.dessaz_df(base_desemp)

base_renda_sa = eu.dessaz_df(eu.deflate_df(base_renda))

wb = xw.Book(r'F:\DADOS\ASSET\MACROECONOMIA\DADOS\Atividade\TRABALHO\PNAD\Desemprego por Escolaridade.xlsx')
sht = wb.sheets['dessaz python']
sht.range('A1').value = base_desemp_sa
sht.range('K1').value = base_renda_sa


