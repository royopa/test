import sys
import pandas as pd
import numpy as np
import xlwings as xw
sys.path.append(r'F:\SISTDAD\MEMPGRP\BMORIER\python\lib')


from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import RidgeClassifierCV, Perceptron
from sklearn.linear_model import PassiveAggressiveClassifier, SGDClassifier
from sklearn.linear_model import LogisticRegressionCV
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier


class all_classifier:
    def __init__(self, fit_int = False, norm_X = False,
                 cv_method = TimeSeriesSplit(12)):
        self.ridge  = make_pipeline(StandardScaler(), 
                                RidgeClassifierCV(fit_intercept=fit_int,cv=cv_method))
        self.percep = make_pipeline(StandardScaler(), Perceptron(fit_intercept=fit_int))
        self.passag = make_pipeline(StandardScaler(), 
                                PassiveAggressiveClassifier(fit_intercept=fit_int, shuffle=False))
        self.sgdcls = make_pipeline(StandardScaler(), SGDClassifier(loss = 'log', 
                                penalty='elasticnet', shuffle=False, fit_intercept=fit_int))
        self.logreg = make_pipeline(StandardScaler(), LogisticRegressionCV(
                    cv=TimeSeriesSplit(12), penalty='l2', fit_intercept=fit_int))
        self.svc    = make_pipeline(StandardScaler(), SVC(probability=True))
        self.gausnb = make_pipeline(StandardScaler(), GaussianNB())
        self.random = make_pipeline(StandardScaler(), RandomForestClassifier())
        
    def calculate(self, X, y, train_size = None):
    
        X_train = X.iloc[:-train_size]
        y_train = y.iloc[:-train_size]
        
        self.ridge.fit(X_train, y_train)
        self.percep.fit(X_train, y_train)
        self.passag.fit(X_train, y_train)
        self.sgdcls.fit(X_train, y_train)
        self.logreg.fit(X_train, y_train)
        self.svc.fit(X_train, y_train)
        self.gausnb.fit(X_train, y_train)
        self.random.fit(X_train, y_train)

        pred = {}
        pred['ridge']  = self.ridge.predict(X)
        pred['percep'] = self.percep.predict(X)
        pred['passag'] = self.passag.predict(X)
        pred['sgdcls'] = self.sgdcls.predict(X)
        pred['logreg'] = self.logreg.predict(X)
        pred['svc']    = self.svc.predict(X)
        pred['gausnb'] = self.gausnb.predict(X)
        pred['random'] = self.random.predict(X)
        
        pred = pd.DataFrame.from_dict(pred)
        avg  = pred.mean(axis=1)
        avg = avg.rename('media')
        pred = pd.concat([avg, pred], axis=1)
        self.pred = pred.set_index(pd.DatetimeIndex(X.index))


file = r'F:\DADOS\ASSET\MACROECONOMIA\INTERNACIONAL\(1) ESTUDOS - DIVERSOS\Recession\data_recession.xlsx'

for sheet in ['mom','yoy']:
    for eco in [True, False]:
        df_raw = pd.read_excel(file, sheet_name=sheet, index_col=0).dropna()
        
        new_month = pd.Series(pd.date_range(start=df_raw.index[-1], periods=4, freq='MS'))
        df_raw.loc[new_month[1], :] = np.nan
        df_raw.loc[new_month[2], :] = np.nan
        df_raw.loc[new_month[3], :] = np.nan
        
        y = df_raw.loc[: , 'recession']; X = df_raw.iloc[: , 1:]
        fin_var = ['aaa','baa','wti_vol','spx_vol','incl103'] + [series + '_' + sheet 
                  for series in ['wti','m1','m2','usd','gold','spx']]
        eco_var = [series + '_' + sheet 
                  for series in ['ism_inv','ism_man','ism_prices','jobl_claims']]
        
        if eco == False: X = X.drop(eco_var, axis=1)
        
        for series in X.columns:
            series_3 = X[series].shift(3);    series_3.name = series+'_3'
            series_6 = X[series].shift(6);    series_6.name = series+'_6'
            series_12 = X[series].shift(12);  series_12.name = series+'_12'
            X = pd.concat([X, series_3, series_6, series_12], axis=1, join='inner')
        
        if eco == True:  X = X.drop(fin_var + eco_var, axis=1)
        else:            X = X.drop(fin_var, axis=1)
            
        X = X.dropna();  y = y.align(X, join='inner')[0]
        
        crisis_its = all_classifier(); crisis_its.calculate(X,y,10)
        crisis_ots = all_classifier(); crisis_ots.calculate(X,y,228)
        
        est = pd.concat([crisis_its.pred.iloc[:,0],crisis_ots.pred.iloc[:,0]], axis=1)
        if eco == True:  
            est.columns = ['eco_in','eco_out']
            out = est.copy()
        else:            
            est.columns = ['fin_in','fin_out']
            out = pd.concat([out, est],axis=1)
        
    out = pd.concat([out, y], axis=1)
    wb = xw.Book(file)
    sh = wb.sheets('est_'+sheet); sh.range('A1').value = out

