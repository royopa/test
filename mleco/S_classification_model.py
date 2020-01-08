import sys
import pandas as pd
import numpy as np
sys.path.append(r'F:\SISTDAD\MEMPGRP\BMORIER\python\lib')

from py_init import *

from bokeh.plotting import figure, show
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectFromModel, RFECV
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import LinearRegression, LarsCV, LassoCV, LassoLarsCV
from sklearn.linear_model import ElasticNetCV, OrthogonalMatchingPursuitCV
from sklearn.linear_model import RidgeCV, BayesianRidge, ARDRegression, HuberRegressor
from sklearn.linear_model import SGDRegressor, PassiveAggressiveRegressor

# CLASSE GENÉRICA DE MODELOS LINEARES
# objetivo: a classe valida os modelos fora da amostra para uma determinada sample
# e guarda as caracteristicas do modelo a serem guardadas
class S_linear_model:
    def __init__(self, X, y, min_est_size = None):
        if min_est_size is None:
            self.min_est_size = int(len(X) // (10/8))
        else:
            self.min_est_size = min_est_size
        self.X_train = X.iloc[:self.min_est_size, :].copy()
        self.y_train = y[:self.min_est_size].copy()
        self.X_test  = X.iloc[self.min_est_size:, :].copy()
        self.y_test  = y[self.min_est_size:].copy()
        self.model     = {}
        self.params    = {}
        self.errors    = {}
        self.pred      = {}
        self.eqm       = {}
        self.time_eqm  = {}
        self.features  = {}

    def validate_model(self, md_name, model):
        X_train = self.X_train.copy()
        X_test  = self.X_test.copy()
        y_train = self.y_train.copy()
        y_test  = self.y_test.copy()
        pred0   = []
        
        for i in range(len(X_test)):
            if i == 0:
                model.fit(X_train, y_train)
                pred0_i = model.predict(pd.DataFrame(X_test.iloc[i, :]).T)
                pred0.append(pred0_i[0])
            else:
                X_i = pd.concat([X_train, X_test.iloc[:i, :]], axis=0)
                y_i = pd.concat([y_train, y_test[:i]])

                model.fit(X_i, y_i)
                pred0_i = model.predict(pd.DataFrame(X_test.iloc[i, :]).T)
                pred0.append(pred0_i[0])
                if md_name == 'sgd_reg':
                    params = model.steps[1][1].best_estimator_.coef_
                elif md_name == 'rfecv':
                    params = np.zeros(len(model.support_))
                    params[model.support_] = model.estimator_.coef_
                elif md_name == 'rand_for':
                    #params = np.zeros(len(model.support_))
                    params = model.steps[1][1]#.n_features_#[1].coef_
                else:
                    params = model.steps[1][1].coef_
                
        pred0     = pd.Series(pred0, index=y_test.index)
        errors0   = y_test - pred0
        eqm0      = sum(errors0**2)
        time_eqm0 = sum((errors0**2)/np.arange(len(errors0),0,-1,dtype=None)**1.1)

        self.model[md_name]    = model
        self.pred[md_name]     = pred0
        self.params[md_name]   = params
        self.features[md_name] = X_train.columns.values
        self.errors[md_name]   = errors0
        self.eqm[md_name]      = eqm0
        self.time_eqm[md_name] = time_eqm0     

class pipe_transf(Pipeline):
    def fit(self, X, y=None, **fit_params):
        super(pipe_transf, self).fit(X, y, **fit_params)
        self.coef_ = self.steps[1][1].coef_
        return self        

class all_estimator:
    def __init__(self, fit_int = False, norm_X = False, parallel = None, 
                 cv_method = TimeSeriesSplit(12),
                 l1_ratio = [.1, .5, .7, .9, .95, .99, 1]):
        #self.larscv   = make_pipeline(StandardScaler(), 
        #                     LarsCV(fit_intercept = fit_int, normalize = norm_X, 
        #                            n_jobs = parallel, cv = cv_method))
        #self.elasnet  = make_pipeline(StandardScaler(), 
        #                     ElasticNetCV(l1_ratio = l1_ratio, fit_intercept = fit_int,
        #                             normalize = norm_X, n_jobs = parallel, cv = cv_method))
        #self.lassocv  = make_pipeline(StandardScaler(), 
        #                     LassoCV(fit_intercept = fit_int, normalize = norm_X, 
        #                             n_jobs = parallel, cv = cv_method))
        #self.laslrscv = make_pipeline(StandardScaler(), 
        #                     LassoLarsCV(fit_intercept = fit_int, normalize = norm_X, 
        #                             n_jobs = parallel, cv = cv_method))        
        #self.ridgecv  = make_pipeline(StandardScaler(), 
        #                     RidgeCV(fit_intercept = fit_int, normalize = norm_X, 
        #                             cv = cv_method))
        #self.lin_all  = make_pipeline(StandardScaler(), 
        #                     LinearRegression(fit_intercept = fit_int, normalize = norm_X,
        #                             n_jobs = parallel))
        #self.hub_reg  = make_pipeline(StandardScaler(), 
        #                     HuberRegressor(fit_intercept = fit_int))
        #self.ort_purs = make_pipeline(StandardScaler(), 
        #                     OrthogonalMatchingPursuitCV(fit_intercept = fit_int, 
        #                             normalize = norm_X, n_jobs = parallel, cv = cv_method))
        #self.bay_rid  = make_pipeline(StandardScaler(), 
        #                     BayesianRidge(fit_intercept = fit_int, normalize = norm_X))
        #self.ard_reg  = make_pipeline(StandardScaler(),
        #                     ARDRegression(fit_intercept = fit_int, normalize = norm_X))
        #self.sgd_reg  = make_pipeline(StandardScaler(), 
        #                     GridSearchCV(SGDRegressor(fit_intercept = fit_int),
        #                       param_grid = {'l1_ratio': l1_ratio,
        #                                     'loss': ['squared_loss','huber',
        #                                          'epsilon_insensitive']},
        #                       cv = cv_method, refit = True))
        #self.pas_agg  = make_pipeline(StandardScaler(), 
        #                     PassiveAggressiveRegressor(fit_intercept = fit_int))
        self.rand_for = make_pipeline(
                             SelectFromModel(DecisionTreeRegressor(), prefit = False), 
                             LinearRegression())
        #norm_lin = pipe_transf([('std', StandardScaler()),
        #                        ('regression', LinearRegression())])
        #self.rfecv = RFECV(estimator = norm_lin, step = 1, cv = cv_method, scoring = 'r2')
        
    def calculate(self, X, y, min_est_size = None):
        data = S_linear_model(X, y, min_est_size)
        #data.validate_model(md_name = 'larscv',   model = self.larscv)
        #data.validate_model(md_name = 'elasnet',  model = self.elasnet)
        #data.validate_model(md_name = 'lasso',    model = self.lassocv)
        #data.validate_model(md_name = 'laslars',  model = self.laslrscv)
        #data.validate_model(md_name = 'ridge',    model = self.ridgecv)
        #data.validate_model(md_name = 'lin_all',  model = self.lin_all)
        #data.validate_model(md_name = 'hub_reg',  model = self.hub_reg)
        #data.validate_model(md_name = 'ort_purs', model = self.ort_purs)
        #data.validate_model(md_name = 'bay_rid',  model = self.bay_rid)
        #data.validate_model(md_name = 'ard_reg',  model = self.ard_reg)
        #data.validate_model(md_name = 'sgd_reg',  model = self.sgd_reg)
        #data.validate_model(md_name = 'pas_agg',  model = self.pas_agg)
        data.validate_model(md_name = 'rand_for', model = self.rand_for)
        #data.validate_model(md_name = 'rfecv',    model = self.rfecv)
        self.data = data
        
        pred = pd.DataFrame.from_dict(data.pred)
        eqm  = pd.DataFrame.from_dict(data.eqm, orient = 'index')
        teqm = pd.DataFrame.from_dict(data.time_eqm, orient = 'index')
        
        w_eqm  = eqm.values/sum(eqm.values)
        w_teqm = teqm.values/sum(teqm.values)
        
        w_eqm5 = w_eqm.copy();       w_teqm5 = w_teqm.copy()
        w_eqm5[w_eqm5 < .05] = 0;    w_teqm5[w_teqm5 < .05] = 0
        w_eqm5 = w_eqm5/sum(w_eqm5); w_teqm5 = w_teqm5/sum(w_teqm5)        
        
        sum(pred*w_eqm.T,axis=1)
        sum(pred*w_teqm.T,axis=1)

    def plotE(self, md):
        plot_data = self.data.errors[md].copy().to_frame()
        # from bokeh.palettes import Spectral11
        from bokeh.palettes import Category20 as pallete
        numlines = plot_data.shape[1]
        p = figure(width = 1000, height = 400, x_axis_type = "datetime")
        mypalette = pallete[20][0:numlines]
        p.multi_line(xs = [plot_data.index.values] * numlines,
                     ys = [plot_data[name].values for name in plot_data],
                     line_color = mypalette,
                     line_width = 2)
        show(p)    
        
    def plotP(self, md):
        plot_data = self.data.pred[md].copy().to_frame()
        plot_data['base'] = self.data.y_test.copy()
        # from bokeh.palettes import Spectral11
        from bokeh.palettes import Category20 as pallete
        numlines = plot_data.shape[1]
        p = figure(width = 1000, height = 400, x_axis_type = "datetime")
        mypalette = pallete[20][0:numlines]
        p.multi_line(xs = [plot_data.index.values] * numlines,
                     ys = [plot_data[name].values for name in plot_data],
                     line_color = mypalette,
                     line_width = 2)
        show(p)    
