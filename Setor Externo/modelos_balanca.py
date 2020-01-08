# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 13:59:28 2019

@author: marcgut
"""


import pandas as pd
from mDataStore.bloomberg.remote import rBLP
from datetime import datetime as dt
import numpy as np
import econuteis as eu
from mongo_load import mongo_load
from mDataStore.globalMongo import mds
from S_linear_model_vp import S_all_estimator as S_model
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
import xlwings as xw

def load_db():
    # Dados Excel
    df_excel = pd.read_excel(r'F:\DADOS\ASSET\MACROECONOMIA\DADOS\Setor_Externo\Estudos\MODELO_BALANCA.xlsm',
                             sheet_name='dados', index_col=0)
    df_excel = df_excel.pct_change(1, fill_method=None)
    idx = list(df_excel.index)
    new_idx = idx.copy()
    for i in range(len(idx)):
        new_idx[i] = idx[i].replace(day=1)
    new_idx = pd.Series(new_idx, index=df_excel.index)
    df_excel = pd.concat([df_excel, new_idx], axis=1)
    df_excel = df_excel.set_index(df_excel.columns[-1])
    
    x_exoil = df_excel.loc[:,'x_exoil'].copy().dropna()
    x_oil = df_excel.loc[:,'x_oil'].copy().dropna()
    m_exoil = df_excel.loc[:,'m_exoil'].copy().dropna()
    m_oil = df_excel.loc[:,'m_oil'].copy().dropna()
    
    
    df_l = df_excel.iloc[:,4:].shift(3)
    
    names = list(df_l.columns)
    names_dic = dict(zip(names,np.zeros(len(names))))
    for key in names_dic:
        names_dic[key] = str(key)+'_3'
    df_l = df_l.rename(columns=names_dic)
    
    idx = list(df_l.index)
    new_idx = idx.copy()
    for i in range(len(idx)):
        new_idx[i] = idx[i].replace(day=1)
    new_idx = pd.Series(new_idx, index=df_l.index)
    df_l = pd.concat([df_l, new_idx], axis=1)
    df_l = df_l.set_index(df_l.columns[-1])
    
    
    
    # Dados Bloomberg (commodities)
    blp1 = rBLP()
    bbg = blp1.getHistoricData(['CO1 Comdty',
                                'S 1 COMB Comdty', 'LC1 COMB Comdty',
                                'XAU BGN Curncy', 'KC1 Comdty', 'SB1 Comdty',
                          'CT1 Comdty', 'CNY REGN Curncy'],['PX_LAST'],
                            startDate=dt(2000, 1, 1), endDate=dt(2100, 1, 1))
    bbg_names = ['petroleo', 'soja', 'boi', 'ouro', 'cafe', 'acucar',
             'algodao', 'cny']
    bbg_dic = {}
    
    for i in range(len(bbg)):
        bbg_dic[bbg_names[i]] = bbg[i].rename(columns={'PX_LAST' : bbg_names[i]})
    bbg_month = {}
    
    for i in bbg_dic.keys():
        bbg_month[i] = pd.Series(eu.month_mma(bbg_dic[i]).iloc[:,0])
    
    bbg_month = pd.DataFrame(bbg_month)
    
    bbg_month = bbg_month.pct_change(1).shift(3)
    names = list(bbg_month.columns)
    names_dic = dict(zip(names,np.zeros(len(names))))
    for key in names_dic:
        names_dic[key] = str(key)+'_3'
    bbg_month = bbg_month.rename(columns=names_dic)
    
    
    # Dados de Atividade (PMC e PIM)
    pmc_list = mds.find(library=mds.econVS, **{'table' : 'pmc'})
    pim_list = mds.find(library=mds.econVS, **{'table' : 'pim'})
    
    all_list = pmc_list + pim_list
    
    m_list = [i for i in all_list if i['real']=='yes' and i['seasonality']=='nsa']
    
    activ_df,_ = mongo_load(m_list=m_list)
    activ_df = activ_df.pct_change(1).shift(3)
    names = list(activ_df.columns)
    names_dic = dict(zip(names,np.zeros(len(names))))
    for key in names_dic:
        names_dic[key] = str(key)+'_3'
    activ_df = activ_df.rename(columns=names_dic)
    
    activ_df = activ_df.loc['2002-05-01':,:]
    activ_df = activ_df.dropna(how='any', axis=1)
    
    # Juntando tudo e fazendo lags
    
    X = pd.concat([activ_df, df_l, bbg_month], axis=1)
    
    for series in X:
        series_6 = X[series].shift(3)
        series_6.name = series[:-2]+'_6'
        series_9 = X[series].shift(6)
        series_9.name = series[:-2]+'_9'
        series_12 = X[series].shift(9)
        series_12.name = series[:-2]+'_12'
        series_15 = X[series].shift(12)
        series_15.name = series[:-2]+'_15'
        series_18 = X[series].shift(15)
        series_18.name = series[:-2]+'_18'
        
        X = pd.concat([X, series_6, series_9, series_12, series_15, series_18],
                       axis=1)
    
    return X, x_exoil, x_oil, m_exoil, m_oil


def estimate_model():
    X, x_exoil, x_oil, m_exoil, m_oil = load_db()
    
    X = X.dropna()
    
    # Rodando modelos
    # Importação Ex petroleo
    m_exoil = m_exoil.align(X, join='inner', axis=0)[0]
    model_m_exoil = S_model(m_exoil, X, saz=True, work_days=True, country='br',
                            transf='mom')
    model_m_exoil.calculate()
    model_m_exoil.strname = 'm_exoil'
    mds.obj.save(name='model_m_exoil', obj=model_m_exoil, path='economia')
    
    # Exportação Ex petroleo
    x_exoil = x_exoil.align(X, join='inner', axis=0)[0]
    model_x_exoil = S_model(x_exoil, X, saz=True, work_days=True, country='br',
                            transf='mom')
    model_x_exoil.calculate()
    model_x_exoil.strname = 'x_exoil'
    mds.obj.save(name='model_x_exoil', obj=model_x_exoil, path='economia')
    
    # Importação petroleo
    m_oil = m_oil.align(X, join='inner', axis=0)[0]
    model_m_oil = S_model(m_oil, X, saz=True, work_days=True, country='br',
                            transf='mom')
    model_m_oil.calculate()
    model_m_oil.strname = 'm_oil'
    mds.obj.save(name='model_m_oil', obj=model_m_oil, path='economia')
    
    # Importação petroleo
    x_oil = x_oil.align(X, join='inner', axis=0)[0]
    model_x_oil = S_model(x_oil, X, saz=True, work_days=True, country='br',
                            transf='mom')
    model_x_oil.calculate()
    model_x_oil.strname = 'x_oil'
    mds.obj.save(name='model_x_oil', obj=model_x_oil, path='economia')
    
    # Colando resultados
    wb = xw.Book(r'F:\DADOS\ASSET\MACROECONOMIA\DADOS\Setor_Externo\Estudos\MODELO_BALANCA.xlsm')
    
    for model in [model_m_exoil, model_x_exoil, model_m_oil, model_x_oil]:
        sheet = wb.sheets(model.strname)
        preds = {}
        for el in model.results:
            preds[el.model_name] = el.pred
        
        preds = pd.DataFrame(preds)
        sheet.range('A1').values = preds


def forecast():
    model_m_exoil = mds.obj.load('model_m_exoil', path='economia')
    model_x_exoil = mds.obj.load('model_x_exoil', path='economia')
    model_m_oil = mds.obj.load('model_m_oil', path='economia')
    model_x_oil = mds.obj.load('model_x_oil', path='economia')
    
    model_m_exoil.strname = 'm_exoil'
    model_x_exoil.strname = 'x_exoil'
    model_m_oil.strname = 'm_oil'
    model_x_oil.strname = 'x_oil'
    
    X, _, _, _, _ = load_db()
    
    X = X.loc['2003-08-01':,:] # pegando apenas a partir dos primeiros valores
    
    X = pd.DataFrame(IterativeImputer().fit_transform(X), index=X.index,
                     columns=X.columns)
    wb = xw.Book(r'F:\DADOS\ASSET\MACROECONOMIA\DADOS\Setor_Externo\Estudos\MODELO_BALANCA.xlsm')
    
    
    for model in [model_m_exoil, model_x_exoil, model_m_oil, model_x_oil]:
        df_pred = pd.read_excel(r'F:\DADOS\ASSET\MACROECONOMIA\DADOS\Setor_Externo\Estudos\MODELO_BALANCA.xlsm',
                                sheet_name=model.strname, header=0, index=0)
        preds = {}
        for el in model.results:
            preds[el.model_name] = pd.Series(el.model.predict(X), 
                                             index=X.index)
        preds = pd.DataFrame(preds)
        
        df_ex = df_pred.iloc[:model.n_end,:].copy()
        X_pred = preds.iloc[model.n_end:, :].copy()
        df_out = pd.concat([df_ex, X_pred], axis=0)
        
        wb.sheets(model.strname).range('A1').values = df_out
    











