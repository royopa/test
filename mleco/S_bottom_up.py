import sys
sys.path.append(r'F:\SISTDAD\MEMPGRP\BMORIER\python\lib')
sys.path.append(r'Z:\Macroeconomia\codes\Projetos\MLEco')
sys.path.append(r'Z:\Macroeconomia\databases')
from mDataStore.globalMongo import mds
import mDataStore.freqHelper as f
from sklearn.linear_model import LinearRegression
from mongo_load import mongo_load, check_freq, numerate_freq
from S_clean_db import S_clean_db as sl_clean
from S_univariate_selection import S_univariate_selection as sl_select
from S_linear_model import S_all_estimator as sl_estimate
import time
import pandas as pd


YS = ['pim_1 Industria geral',
      'pim_1 Bens de capital', 
      'pim_2 Bens intermediarios',
      'pim_3 Bens de consumo']
YS = ['pim_1 Industria geral',
      'pim_2 Industrias extrativas',
      'pim_3 Industrias de transformacao']


supreme = S_bottom_up(YS)
tic1 = time.clock()
supreme.clean()
tic2 = time.clock()
supreme.select()
tic3 = time.clock()
supreme.estimate(al = False)
tic4 = time.clock()


class S_bottom_up:
    def __init__(self, y_all):   
        self.y_all = y_all
        
        YX = pd.DataFrame()
        for el in y_all:
            X = mds.read(name=el, freq=f.monthBegin, library=mds.econVS)
            YX = pd.concat([YX, X.iloc[:, 0]], axis=1)
        YX.columns = y_all
       
        YX = YX.diff(periods=1).dropna()
        
        weights = LinearRegression(fit_intercept = False).fit(YX.iloc[:,1:], YX.iloc[:,0]).coef_
        self.weights = weights/sum(weights)
        
        self.alpha = {}
        self.beta  = {}
        self.gamma = {}
        
        
    
    def clean(self, transf='mom', min_y_sample=.8, lags_y=1, lags_X=(0, 4)):
        if lags_y == 0 and lags_X == (0,0):
            with_lags = False
        else: 
            with_lags = True
        
        for el in self.y_all:
            db = mds.read(name=el, freq=f.monthBegin, library=mds.econVS)
            alpha = sl_clean(target=db)
            alpha.transform_y(transf)
            alpha.get_db(check_real=True, check_seas=True, min_y_sample=min_y_sample, mongo_list=None)
            alpha.make_lags(lags_y=lags_y, lags_X=lags_X)
            alpha.check_rel_date(with_lags=with_lags, new_output=False, update_mongo_list=True)
            self.alpha[el] = alpha        
        
        self.with_lags = with_lags
        
        

    def select(self, min_est_prop=.8):         
        for el in self.y_all:
            Y  = self.alpha[el].y_data
            if self.with_lags:
                X  = self.alpha[el].X_df_l
            else:
                X  = self.alpha[el].X_df
            beta = sl_select(y = Y, X = X, min_est_prop = min_est_prop)
            beta.select(prop = 0.8, method = 'f_regression')
            self.beta[el] = beta


    def estimate(self, al = True):         
        for el in self.y_all:
            Y = self.beta[el].y
            X = self.beta[el].X_select

            gamma = sl_estimate(y = Y, X = X, al = al)
            gamma.calculate()
            self.gamma[el] = gamma




