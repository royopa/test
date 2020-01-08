# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 16:37:08 2019

@author: marcgut
"""

import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.linear_model import LassoCV, ElasticNetCV
from sklearn.linear_model import LinearRegression, BayesianRidge
from sklearn.ensemble import BaggingRegressor, RandomForestRegressor, AdaBoostRegressor, GradientBoostingRegressor
from sklearn.decomposition import PCA
from atacado_functions import *
from atacado_agrupamento import *
from mDataStore.globalMongo import mds





class gen_estimator():
    def __init__(self):
        
        models = {}
        models['bay_rid'] = make_pipeline(StandardScaler(),
                                          BayesianRidge(fit_intercept=False,
                                                        normalize=False))
        models['lasso'] = make_pipeline(StandardScaler(),
                                              LassoCV(fit_intercept=False,
                                              normalize=False,
                                              cv=TimeSeriesSplit()))
        models['elasnet'] = make_pipeline(StandardScaler(),
                                          ElasticNetCV(l1_ratio=[.1, .5, .7, .9, .95, .99, 1],
                                          fit_intercept=False,
                                          normalize=False,
                                          cv=TimeSeriesSplit()))
        models['ols_pca'] = GridSearchCV(make_pipeline(StandardScaler(), PCA(),
                                             LinearRegression()),
                                             param_grid={'pca__n_components': [1, 2, 3, 4, 5]},
                                             cv=TimeSeriesSplit(), refit=True)
        models['rand_for'] = GridSearchCV(make_pipeline(StandardScaler(),
                                          RandomForestRegressor()),
                                          param_grid={'randomforestregressor__n_estimators':[10, 50, 100]},
                                          cv=TimeSeriesSplit(), refit=True)
        models['bagging'] = GridSearchCV(make_pipeline(StandardScaler(),
                                         BaggingRegressor(LinearRegression(fit_intercept=False,
                                         normalize=False), max_samples=0.5, max_features=0.5)),
                                         param_grid={'baggingregressor__n_estimators': [5, 10, 20, 50]},
                                         cv=TimeSeriesSplit(), refit=True)
        models['ada'] = GridSearchCV(make_pipeline(StandardScaler(),
                                     AdaBoostRegressor(LinearRegression(fit_intercept=False,
                                     normalize=False))),
                                     param_grid={'adaboostregressor__n_estimators': [10, 50, 100],
                                                  'adaboostregressor__learning_rate': [0.1, 0.2, 0.5]},
                                     cv=TimeSeriesSplit(), refit=True)
        models['g_boost'] = GridSearchCV(make_pipeline(StandardScaler(), GradientBoostingRegressor()),
                                      param_grid={'gradientboostingregressor__n_estimators': [10, 50, 100],
                                                  'gradientboostingregressor__learning_rate': [0.1, 0.2, 0.5]},
                                      cv=TimeSeriesSplit(), refit=True)
        
        self.models = models
        
    def fit(self, X, y):
        for model in self.models:
            self.models[model].fit(X, y)
        self.X_fitted = X
        self.y_fitted = y
        
        return self
    
    def predict(self, X=None, y_lags=None):
        """y_lags deve ser uma lista de strings com o nome das defasagens e y."""
        if X is None:
            X = self.X_fitted
        
        if y_lags is None:
            pred = {}
            for model in self.models:
                pred[model] = pd.Series(self.models[model].predict(X),
                                        index=X.index)
            pred = pd.DataFrame(pred)
            
            return pred.mean(axis=1)
        else:
            n_comp = len(X) - len(self.y_fitted)
            # VOU FAZER ISSO DEPOIS
            
        
class model_creator():
    def __init__(self, ref, defasagem, ws_ponta, base_ponta, with_comm=True,
                 y_lags=None, extra_covar=None):
        self.ref = ref
        self.defas = defasagem
        self.with_comm = with_comm
        self.y_lags = y_lags
        
        groups = make_groups()
        
        if with_comm:
            covar = groups[ref] + groups['commodities_gerais']
        else:
            covar = groups[ref]
        if extra_covar is None:
            self.X = make_lags(self.adj_X(ws_ponta.loc[:, covar]), defasagem)
        else:
            self.X = make_lags(self.adj_X(ws_ponta.loc[:, covar+extra_covar]), defasagem)
        self.y = base_ponta.loc[:, int(ref[1])]
                
    def run(self, RERUN=True):
        # Fitando modelos
        y_fit, X_fit = self.y.align(self.X.dropna(), join='inner', axis=0)
        
        if RERUN:
            estimator = gen_estimator()
            
            estimator.fit(X_fit, y_fit)
            
            mds.obj.save(name='atac_'+str(self.ref[0])+'_'+str(self.ref[1]),
                         obj=estimator, path='economia')
        else:
            estimator = mds.obj.load(name='atac_'+str(self.ref[0])+'_'+str(self.ref[1]),
                                     path='economia')[1]['obj']

        X_pred = self.X.dropna()

        pred = estimator.predict(X_pred, self.y_lags)
        
        return pred

    def adj_X(self, X):
        
        # Dropando se é tudo NA
        X = X.dropna(axis=1, how='all')
        
        # Checando tamanho das séries (séries tem que ter no mínimo 360 dias)
        # e se há muitos zeros recentemente (mais da metade de zeros nos últimos 360 dias)
        dropped_size = []
        dropped_const = []
        for series in X:
            s = X[series].dropna()
            if len(s) < 360:
                dropped_size.append(series)
            elif len(s.iloc[-360:].to_numpy().nonzero()[0]) < (360/2):
                dropped_const.append(series)
        
        X_out = X.copy()
        
        X_out = X_out.drop(columns=dropped_const)
        
        if len(X_out.drop(columns=dropped_size).columns) > 0:
            X_out = X_out.drop(columns=dropped_size)
        
        
        
        return X_out
    








