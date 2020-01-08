import sys
import pandas as pd
import numpy as np
sys.path.append(r'F:\SISTDAD\MEMPGRP\BMORIER\python\lib')
import itertools
import statsmodels.api as sm
import random
from sklearn.base import BaseEstimator, TransformerMixin
from threading import Thread


class S_arimax:
    def __init__(self, arima_order=(1, 0, 0), seas_order=(0, 0, 0), trend=None,
                 freq=12):
        self.arima_order = arima_order
        self.seas_order = seas_order
        self.trend = trend
        self.freq = freq
        self.is_fitted = False

    def fit(self, y, X=None):
        arima_order = self.arima_order
        seas_order = self.seas_order
        trend = self.trend
        freq = self.freq
        if isinstance(y, np.ndarray):
            y = pd.Series(y)
        if X is not None:
            if isinstance(X, np.ndarray):
                X = pd.DataFrame(X)
        seas_order = seas_order + (freq,)

        self.model = sm.tsa.statespace.SARIMAX(endog=y, exog=X, order=arima_order,
                                               seasonal_order=seas_order,
                                               trend=trend)
        self.model_fit = self.model.fit(maxiter=100, method='nm')
        
        self.is_fitted = True

        return self

    def predict(self, X=None, steps=None):
        if steps is None:
            if X is None:
                steps = 1
            else:
                steps = len(X)
        return np.array(self.model_fit.forecast(steps=steps, exog=X))

class S_avg_arima:
    def __init__(self, arima_upbound=(3, 1, 3), seas_upbound=(3, 1, 3), n_models=70,
                 trend_grid=('c', 't', 'ct'), freq=12, use_X=True, always_ar=True):
        if always_ar:
            p = range(1, arima_upbound[0]+1)
        else:
            p = range(0, arima_upbound[0]+1)
        d = range(0, arima_upbound[1]+1)
        q = range(0, arima_upbound[2]+1)
        self.arima_iter = list(itertools.product(p, d, q))
        if (0, 0, 0) in self.arima_iter:
            self.arima_iter.remove((0, 0, 0))
        p_s = range(0, seas_upbound[0]+1)
        d_s = range(0, seas_upbound[1]+1)
        q_s = range(0, seas_upbound[2]+1)
        self.seas_iter = list(itertools.product(p_s, d_s, q_s))
        self.trend_grid = trend_grid
        self.freq = freq
        self.use_X = use_X
        self.n_models = n_models
        
        self.model_fit_list = []

    def fit(self, X, y):
        self.model_fit_list = []
        if isinstance(y, np.ndarray):
            y = pd.Series(y)
        if self.use_X:
            if isinstance(X, np.ndarray):
                X = pd.DataFrame(X)
                y = y.reset_index(drop=True)
        else:
            X = None
        arima_iter = self.arima_iter
        seas_iter = self.seas_iter
        trend_grid = self.trend_grid
        freq = self.freq
        model_list = (S_arimax(arima_order=a, seas_order=b,
                               trend=c, freq=freq) for a in arima_iter for b in seas_iter
                      for c in trend_grid)
        model_sample = random.sample(list(model_list), self.n_models)
        
#        for el in model_sample:
#            try:
#                model_fit_list.append(el.fit(y, X))
#            except:
#                continue
#            model_fit_list.append(el.fit(y, X))        

        result_list = []        
        
        for el in model_sample:
            t = FitThread(el, X, y)
            t.start()
            result_list.append(t)
            
        for el in result_list:
            el.join()

        
        for el in result_list:
            if el.model.is_fitted:
                self.model_fit_list.append(el.model)
         
        return self
        

    def predict(self, X, method='avg'):
        model_fit_list = self.model_fit_list
        if self.use_X:
            if isinstance(X, np.ndarray):
                X = pd.DataFrame(X)
            steps=None
        else:
            steps = len(X)
            X = None

        if method == 'avg_aic':
            aic_list = []
            for el in model_fit_list:
                aic_list.append(el.model_fit.aic + 100000)

            pond_=(1/np.array(aic_list))/sum(1/np.array(aic_list))
        elif method == 'avg':
            pond_ = np.ones(len(model_fit_list))/len(model_fit_list)

        pred_ = []
        for el in model_fit_list:
            pred_.append(el.predict(X=X, steps=steps))

        pred_fin = []
        isna = []
        for predi in pred_:
            if True in np.isnan(predi):
                isna.append(True)
            else:
                isna.append(False)

        pred_ = np.delete(pred_, np.nonzero(isna)[0])
        pond_ = np.delete(pond_, np.nonzero(isna)[0])
        pond_ = pond_ / sum(pond_)

        for i, el in enumerate(pred_):
            pred_fin.append(el*pond_[i])

        pred_fin = np.array([sum(pred_fin)])

        return pred_fin


class DropFeatures(BaseEstimator, TransformerMixin):
    def __init__(self, features):
        self.features = features

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        return X.drop(self.features, axis=1)


class FitThread(Thread):
    def __init__(self, model, X, y):
        Thread.__init__(self)
        self.model = model
        self.X = X
        self.y = y

    def run(self):
        # fita
        try:
            self.model.fit(self.y, self.X)
        except:
            pass


