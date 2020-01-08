# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25 15:35:23 2019

@author: marcgut
"""
import sys
sys.path.append(r'F:\SISTDAD\MEMPGRP\BMORIER\python\lib')
sys.path.append(r'Z:\Macroeconomia\codes\Projetos\MLEco')
sys.path.append(r'Z:\Macroeconomia\databases')
import statsmodels.api as sm
import numpy as np
import pandas as pd
# import xlwings as xw


df_raw = pd.read_excel(
         r'F:\DADOS\ASSET\MACROECONOMIA\DADOS\Atividade\INDUSTRIA\IBGE\PIM_MODELOS.xlsm',
         sheet_name='modelos_juliano', index_col=0)

y = df_raw.iloc[:,0]; X = df_raw.iloc[:,1:]


x_1 = X.loc[:, ['Anfavealev', 'Anfaveapes', 'abpo', 'abcr', 'isa_fgv',
                'epe', 'du', 's01', 's02', 's03', 's04', 's05', 's06', 's07'
                , 's08', 's09', 's10', 's11', 's12']].dropna() # MODELO MA(1)

x_2 = X.loc[:, ['Anfavealev', 'Anfaveapes', 'abpo', 'abcr', 'isa_fgv',
                 'du', 's01', 's02', 's03', 's04', 's05', 's06', 's07'
                , 's08', 's09', 's10', 's11', 's12']].dropna() # MODELO MA(1)

x_3 = X.loc[:, ['Anfavealev', 'Anfaveapes', 'abcr', 'isa_fgv',
                 'du', 's01', 's02', 's03', 's04', 's05', 's06', 's07'
                , 's08', 's09', 's10', 's11', 's12']].dropna() # MODELO SEM MA

x_4 = X.loc[:, ['Anfavealev', 'Anfaveapes', 'ie_fgv',
                 'du', 's01', 's02', 's03', 's04', 's05', 's06', 's07'
                , 's08', 's09', 's10', 's11', 's12']].dropna() # MODELO MA(1)

predict_1 = []
predict_2 = []
predict_3 = []
predict_4 = []
aic_1 = []
aic_2 = []
aic_3 = []
aic_4 = []

for i in range(30,0,-1):
    # treino
    x_i1 = x_1.iloc[:-i,:]
    x_i2 = x_2.iloc[:-i,:]
    x_i3 = x_3.iloc[:-i,:]
    x_i4 = x_4.iloc[:-i,:]

    model_i1 = sm.tsa.statespace.SARIMAX(endog=y.align(x_i1, join='inner')[0], exog=x_i1,
                                    order=(0,0,1),trend=None).fit(maxiter=300, method='nm')
    model_i2 = sm.tsa.statespace.SARIMAX(endog=y.align(x_i2, join='inner')[0], exog=x_i2,
                                    order=(0,0,1),trend=None).fit(maxiter=300, method='nm')
    model_i3 = sm.tsa.statespace.SARIMAX(endog=y.align(x_i3, join='inner')[0], exog=x_i3,
                                    order=(0,0,0),trend=None).fit(maxiter=300, method='nm')
    model_i4 = sm.tsa.statespace.SARIMAX(endog=y.align(x_i4, join='inner')[0], exog=x_i4,
                                    order=(0,0,1),trend=None).fit(maxiter=300, method='nm')

    # guardando aic
    aic_1.append(model_i1.aic)
    aic_2.append(model_i2.aic)
    aic_3.append(model_i3.aic)
    aic_4.append(model_i4.aic)
    
    # previsão
    predict_1.append(model_i1.forecast(steps=1, exog=pd.DataFrame(x_1.iloc[-i,:]).T))
    predict_2.append(model_i2.forecast(steps=1, exog=pd.DataFrame(x_2.iloc[-i,:]).T))
    predict_3.append(model_i3.forecast(steps=1, exog=pd.DataFrame(x_3.iloc[-i,:]).T))
    predict_4.append(model_i4.forecast(steps=1, exog=pd.DataFrame(x_4.iloc[-i,:]).T))

# Montando projeções
predict_1 = pd.concat(predict_1, axis=0)
predict_2 = pd.concat(predict_2, axis=0)
predict_3 = pd.concat(predict_3, axis=0)
predict_4 = pd.concat(predict_4, axis=0)

for i in range(len(aic_1)):
    aic_1[i] = pd.Series(aic_1[i], index=[predict_1.index[i]])
    aic_2[i] = pd.Series(aic_2[i], index=[predict_2.index[i]])
    aic_3[i] = pd.Series(aic_3[i], index=[predict_3.index[i]])
    aic_4[i] = pd.Series(aic_4[i], index=[predict_4.index[i]])

aic_1 = pd.concat(aic_1, axis=0)
aic_2 = pd.concat(aic_2, axis=0)
aic_3 = pd.concat(aic_3, axis=0)
aic_4 = pd.concat(aic_4, axis=0)


predict_final = predict_1.copy()
for i,el in predict_final.iteritems():
    aic = abs(np.array([aic_1[i], aic_2[i], aic_3[i], aic_4[i]]))
    pred = np.array([predict_1[i], predict_2[i], predict_3[i], predict_4[i]])
    predict_final[i] = np.dot(aic, pred)/sum(aic)
    

# wb = xw.Book(r'F:\DADOS\ASSET\MACROECONOMIA\DADOS\Atividade\INDUSTRIA\IBGE\PIM_MODELOS.xlsm')
# sheet = wb.sheets('mjxbbg')
# sheet.range('A1').value = predict_final




