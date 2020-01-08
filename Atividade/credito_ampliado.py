# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 17:41:23 2019

@author: marcgut
"""


import pandas as pd
import econuteis as eu
from mDataStore.globalMongo import mds
from mongo_load import mongo_load, check_freq, numerate_freq, transform_series
from datetime import timedelta
import mDataStore.freqHelper as f
from mongo_load import mongo_load
from funcoes_data_mcm_mult import mcm_base
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.feature_selection import SelectKBest, RFECV, SelectFromModel, f_regression, mutual_info_regression
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import LarsCV, LassoCV, LassoLarsCV, ElasticNetCV, OrthogonalMatchingPursuitCV, RidgeCV
from sklearn.linear_model import LinearRegression, BayesianRidge, ARDRegression, HuberRegressor
from sklearn.linear_model import SGDRegressor, PassiveAggressiveRegressor, OrthogonalMatchingPursuit
from sklearn.ensemble import BaggingRegressor, RandomForestRegressor, AdaBoostRegressor, GradientBoostingRegressor



df = mcm_base([(264,'Empresas e famílias')])
df = df[list(df.keys())[0]]['Empresas e famílias'][0]
df = df.drop(columns=df.columns[6])
df = eu.deflate_df(df)
df = df.diff(12).dropna(axis=0, how='all')


ibc = pd.read_excel(r'F:\DADOS\ASSET\MACROECONOMIA\DADOS\Base de Dados\MCM\ATVIBC1.xls',
                   sheet_name='IBC-Br')
ibc = ibc.iloc[2:, 0:2]
ibc = ibc.set_index(keys=ibc.columns[0])
ibc = ibc.iloc[:-6, :]
ibc = ibc.diff(12).dropna(axis=0, how='all')
ibc = ibc.loc[df.index[0]:, ]
ibc = ibc.rename(columns={'Unnamed: 1' : 'ibc_br'})

ind_cred_list = mds.find(library=mds.econVS, **{'table' : 'ind_credito'})
saldo_cred_list = mds.find(library=mds.econVS, **{'table' : 'estoque_credito'})


data_list = []
for table in [ind_cred_list, saldo_cred_list]:
    for i_dic in table:
        if i_dic['real'] == 'yes' and i_dic['seasonality'] == 'nsa':
            data_list.append(i_dic)

credito, _ = mongo_load(m_list=data_list)

credito = credito.diff(12).dropna(axis=0, how='all')

df_general = pd.concat([df, credito], axis=1, join='inner')

for series in df_general:
    series_1 = df_general[series].shift(1).rename(series+'_1')
    series_2 = df_general[series].shift(2).rename(series+'_2')
    series_3 = df_general[series].shift(3).rename(series+'_3')
    series_4 = df_general[series].shift(4).rename(series+'_4')
    series_5 = df_general[series].shift(5).rename(series+'_5')
    series_6 = df_general[series].shift(6).rename(series+'_6')
    df_general = pd.concat([df_general, series_1, series_2, series_3, series_4,
                            series_5, series_6], axis=1, join='outer')

df_general = df_general.dropna()
ibc = ibc.align(df_general, axis=0, join='inner')[0]

n_splits = (len(df_general)-50)

models = {}

models[1] = make_pipeline(StandardScaler(), SelectFromModel(DecisionTreeRegressor(),
                        prefit=False)).fit(df_general,ibc)
models[2] = make_pipeline(StandardScaler(), SelectFromModel(ElasticNetCV(normalize=False,
                                      cv=TimeSeriesSplit(n_splits)), prefit=False)).fit(df_general,ibc)
models[3] = make_pipeline(StandardScaler(), SelectFromModel(LarsCV(normalize=False,
                                      cv=TimeSeriesSplit(n_splits)), prefit=False)).fit(df_general,ibc)
models[4] = make_pipeline(StandardScaler(), SelectFromModel(BayesianRidge(normalize=False),
                        prefit=False)).fit(df_general,ibc)
models[5] = make_pipeline(StandardScaler(), RFECV(LinearRegression(), cv=TimeSeriesSplit(n_splits))).fit(df_general,ibc)
models[6] = make_pipeline(StandardScaler(), SelectKBest(mutual_info_regression, 1)).fit(df_general,ibc)
models[7] = make_pipeline(StandardScaler(), SelectKBest(mutual_info_regression, 3)).fit(df_general,ibc)
models[8] = make_pipeline(StandardScaler(), SelectKBest(mutual_info_regression, 5)).fit(df_general,ibc)
models[9] = make_pipeline(StandardScaler(), SelectKBest(mutual_info_regression, 10)).fit(df_general,ibc)


masks_ = {}
for i in models:
    masks_[i] = models[i].steps[1][1].get_support()

var_ = {}

for i in masks_:
    var_[i] = list(df_general.columns[masks_[i]])







