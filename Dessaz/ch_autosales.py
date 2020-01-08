# -*- coding: utf-8 -*-
"""
Created on Mon Jul 29 09:28:51 2019

@author: marcgut
"""

import pandas as pd
import sys
import xlwings as xw
sys.path.append(r'Z:\Macroeconomia\codes')
import econuteis as eu

base = pd.read_excel(
        r'F:\DADOS\ASSET\MACROECONOMIA\INTERNACIONAL\China\CH - Auto Sales.xlsx',
        sheet_name='Dess', header=0, index_col=0)

sales = base.loc[:, 'Sales']
sales_sa = eu.dessaz_df(sales)

wb = xw.Book(r'F:\DADOS\ASSET\MACROECONOMIA\INTERNACIONAL\China\CH - Auto Sales.xlsx')
sht = wb.sheets['Dess']
sht.range('E1').value = sales_sa

