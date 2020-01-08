import sys
import pandas as pd
import numpy as np
import xlwings as xw
sys.path.append(r'F:\SISTDAD\MEMPGRP\BMORIER\python\lib')

from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import RidgeClassifierCV, Perceptron
from sklearn.linear_model import PassiveAggressiveClassifier, SGDClassifier
from sklearn.linear_model import LogisticRegressionCV
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier, BaggingClassifier, AdaBoostClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer


# CLASSE GENÉRICA DE MODELOS LINEARES
# objetivo: a classe valida os modelos fora da amostra para uma determinada sample
# e guarda as caracteristicas do modelo a serem guardadas
class S_linear_model:
    def __init__(self, X, y, min_est_size = None, pred_ahead=1):
        self.pred_ahead = pred_ahead
        if min_est_size is None:
            self.min_est_size = int(len(X) // (10/8)) - pred_ahead + 1
        else:
            self.min_est_size = min_est_size - pred_ahead + 1
        self.X_train = X.iloc[:self.min_est_size, :].copy()
        self.y_train = y[:self.min_est_size].copy()
        self.X_test  = X.iloc[self.min_est_size:, :].copy()
        self.y_test  = y[self.min_est_size:].copy()
        self.model     = {}
        self.pred      = {}
        #self.proba     = {}

    def validate_model(self, md_name, model):
        X_train = self.X_train.copy()
        X_test  = self.X_test.copy()
        y_train = self.y_train.copy()
        y_test  = self.y_test.copy()
        pred0   = []
        
        for i in range(len(X_test)-self.pred_ahead+1):
            if i == 0:
                model.fit(X_train, y_train)
                pred0_i = model.predict(pd.DataFrame(X_test.iloc[i:i+self.pred_ahead, :]))
                pred0 = [el for el in pred0_i[:self.pred_ahead]]
            else:
                X_i = pd.concat([X_train, X_test.iloc[:i, :]], axis=0)
                y_i = pd.concat([y_train, y_test[:i]])

                model.fit(X_i, y_i)
                pred0_i = model.predict(pd.DataFrame(X_test.iloc[i:i+self.pred_ahead, :]))
                pred0.append(pred0_i[self.pred_ahead-1])
                
        pred0     = pd.Series(pred0, index=y_test.index)

        self.model[md_name]  = model
        self.pred[md_name]   = pred0
        #self.proba[md_name]  = pred0

class all_classifier:
    def __init__(self, k,fit_int = False, norm_X = False,
                 cv_method = TimeSeriesSplit(4)):
        self.ridge  = make_pipeline(StandardScaler(), 
                                RidgeClassifierCV(fit_intercept=fit_int,cv=cv_method))
        self.percep = make_pipeline(StandardScaler(), Perceptron(fit_intercept=fit_int))
        self.passag = make_pipeline(StandardScaler(), 
                                PassiveAggressiveClassifier(fit_intercept=fit_int, shuffle=False))
        self.sgdcls = make_pipeline(StandardScaler(), SGDClassifier(loss = 'log', 
                                penalty='elasticnet', shuffle=False, fit_intercept=fit_int))
        self.logreg = make_pipeline(StandardScaler(), LogisticRegressionCV(max_iter=100,
                                cv=TimeSeriesSplit(12), penalty='l2', fit_intercept=fit_int))
        self.svc    = make_pipeline(StandardScaler(), SVC(probability=True))
        self.gausnb = make_pipeline(StandardScaler(), GaussianNB())
        self.random = make_pipeline(StandardScaler(), RandomForestClassifier())
        self.bagging = GridSearchCV(make_pipeline(StandardScaler(), 
                              BaggingClassifier(max_samples=0.5, max_features=0.5)),
                                     param_grid={'baggingclassifier__n_estimators': [5, 10, 20, 50]},
                                     cv=cv_method, refit=True)
        self.ada = GridSearchCV(make_pipeline(StandardScaler(),
                               AdaBoostClassifier()),
                                     param_grid={'adaboostclassifier__n_estimators': [10, 50, 100],
                                                 'adaboostclassifier__learning_rate': [0.1, 0.2, 0.5]},
                                     cv=cv_method, refit=True)
        self.g_boost = GridSearchCV(make_pipeline(StandardScaler(),
                               GradientBoostingClassifier()),
                                     param_grid={'gradientboostingclassifier__n_estimators': [10, 50, 100],
                                                 'gradientboostingclassifier__learning_rate': [0.1, 0.2, 0.5]},
                                     cv=cv_method, refit=True)
        self.mlp = GridSearchCV(make_pipeline(StandardScaler(),
                             MLPClassifier()),
                                     param_grid={'mlpclassifier__hidden_layer_sizes':
                                     [(round(.66*k), round(.33*k)), (round(.75*k), round(.50*k), round(.25*k)),
                                      (round(.80*k), round(.60*k), round(.40*k), round(.20*k))]},
                                     cv=cv_method, refit=True)
        
    def calculate(self, X, y, min_est_size = None, pred_ahead = 1):
        data = S_linear_model(X, y, min_est_size, pred_ahead)
        data.validate_model(md_name = 'ridge',  model = self.ridge)
        data.validate_model(md_name = 'percep', model = self.percep)        
        data.validate_model(md_name = 'passag', model = self.passag)
        data.validate_model(md_name = 'sgdcls', model = self.sgdcls)
        data.validate_model(md_name = 'logreg', model = self.logreg)
        data.validate_model(md_name = 'svc',    model = self.svc)        
        data.validate_model(md_name = 'gausnb', model = self.gausnb)        
        data.validate_model(md_name = 'bagging', model = self.bagging)
        data.validate_model(md_name = 'ada', model = self.ada)
        data.validate_model(md_name = 'g_boost', model = self.g_boost)
        data.validate_model(md_name = 'mlp', model = self.mlp)
        data.validate_model(md_name = 'random', model = self.random)
        
        pred = pd.DataFrame.from_dict(data.pred)

        avg  = pred.mean(axis=1)
        avg  = avg.rename('media')
        self.pred = pred = pd.concat([avg, pred], axis=1)

file = r'F:\DADOS\ASSET\MACROECONOMIA\INTERNACIONAL\(1) ESTUDOS - DIVERSOS\Recession\data_recession.xlsx'

for sheet in ['yoy']:
    sheet = 'yoy'    
    for eco in [True]:
        eco = True
        df_raw = pd.read_excel(file, sheet_name=sheet, index_col=0)
        df_raw = df_raw.loc['1987-01-01':, :]
        
#        new_month = pd.Series(pd.date_range(start=df_raw.index[-1], periods=4, freq='MS'))
#        df_raw.loc[new_month[1], :] = np.nan
#        df_raw.loc[new_month[2], :] = np.nan
#        df_raw.loc[new_month[3], :] = np.nan
#        
#        y = df_raw.loc[: , 'recession']; X = df_raw.iloc[: , 1:]
#        fin_var = ['aaa','baa','wti_vol','spx_vol','incl103'] + [series + '_' + sheet 
#                  for series in ['wti','m1','m2','usd','gold','spx']]
#        eco_var = [series + '_' + sheet 
#                  for series in ['ism_inv','ism_man','ism_prices','jobl_claims']]
#        
#        if eco == False: X = X.drop(eco_var, axis=1)
#        
#        X = X.loc[:,['ism_man_yoy','conf_cur_comp_yoy', 'conf_cur_yoy']]
        y = df_raw.loc[:, 'recession']
        
        df_raw = df_raw.iloc[:, 1:]
        
        X = pd.DataFrame(IterativeImputer().fit_transform(df_raw),
                            index=df_raw.index,columns=df_raw.columns)
        
        for series in X.columns:
            series_3 = X[series].shift(3);    series_3.name = series+'_3'
            series_6 = X[series].shift(6);    series_6.name = series+'_6'
            series_12 = X[series].shift(12);  series_12.name = series+'_12'
            X = pd.concat([X, series_3, series_6, series_12], axis=1, join='inner')
        
        #if eco == True:  X = X.drop(fin_var + eco_var, axis=1)
        #else:            X = X.drop(fin_var, axis=1)
            
        X = X.dropna();  y = y.align(X, join='inner')[0]
        
        k = X.shape[1]
        crisis = all_classifier(k) 
        crisis.calculate(X, y, min_est_size = 239, pred_ahead = 12)
        
        if eco == True:  
            #est.columns = ['eco_in','eco_out']
            out = crisis.pred.copy()
        else:            
            #est.columns = ['fin_in','fin_out']
            out = pd.concat([out, crisis.pred],axis=1)
        
    out = pd.concat([out, y], axis=1)
    wb = xw.Book(file)
    sh = wb.sheets('other_'+sheet); sh.range('A1').value = out

