import sys
import pandas as pd
import numpy as np
#sys.path.append(r'F:\SISTDAD\MEMPGRP\BMORIER\python\lib')
#sys.path.append(r'Z:\Macroeconomia\codes')
#sys.path.append(r'Z:\Macroeconomia\codes\Projetos\MLEco')
from bokeh.plotting import figure, show
from econuteis import freq_df
from mongo_load import workdays_series
from threading import Thread
from S_arima import S_avg_arima, DropFeatures

#from py_init import *
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectFromModel, RFECV
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import LarsCV, LassoCV, LassoLarsCV, ElasticNetCV, OrthogonalMatchingPursuitCV, RidgeCV
from sklearn.linear_model import LinearRegression, BayesianRidge, ARDRegression, HuberRegressor
from sklearn.linear_model import SGDRegressor, PassiveAggressiveRegressor, OrthogonalMatchingPursuit
from sklearn.ensemble import BaggingRegressor, RandomForestRegressor, AdaBoostRegressor, GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import WhiteKernel, ConstantKernel, RBF, Matern, RationalQuadratic
from sklearn.gaussian_process.kernels import ExpSineSquared, DotProduct
from sklearn.decomposition import PCA, KernelPCA

# PACOTES DO R
from rpy2.robjects.packages import importr
from rpy2.robjects import r, pandas2ri
import  rpy2.robjects as ro
stats = importr('stats')
base  = importr('base')
utils = importr('utils')
#utils.install_packages('MCS')  # Para instalar o pacote
mcs   = importr('MCS')

# CLASSE GENÉRICA DE MODELOS LINEARES
class S_linear_model(Thread):
    ''' Objetivo: a classe valida os modelos fora da amostra para uma determinada sample
    e guarda algumas caracteristicas do modelo
    '''
    def __init__(self, y, x, md_name, model, min_est_prop = .8, n_start = None):
        Thread.__init__(self)
        
        if n_start == None:
            self.n_start = int(len(x)*min_est_prop)
        else:
            self.n_start = n_start
                
        # separação de amostra de treino e de teste
        self.y_train = y[:self.n_start].copy()
        self.y_test = y[self.n_start:].copy()
        self.x_train = x.iloc[:self.n_start, :].copy()
        self.x_test = x.iloc[self.n_start:, :].copy()
        self.n_end = len(y)

        # definindo os espaços para salvar as 
        # caracteristicas desejáveis das variáveis
        self.model = model
        self.model_name = md_name
        self.avg_y = None
        self.pred = None

    def run(self):
        model = self.model
        x_train = self.x_train.copy()
        x_test = self.x_test.copy()
        y_train = self.y_train.copy()
        y_test = self.y_test.copy()
        pred0 = []
        avg0 = []
        
        for i in range(len(x_test)):
            if i == 0:
                model.fit(x_train, y_train)
                pred0_i = model.predict(pd.DataFrame(x_test.iloc[i, :]).T)
                pred0.append(pred0_i[0])
                avg0.append(np.mean(y_train.values))
                
            else:
                X_i = pd.concat([x_train, x_test.iloc[:i, :]], axis=0)
                y_i = pd.concat([y_train, y_test[:i]])

                model.fit(X_i, y_i)
                pred0_i = model.predict(pd.DataFrame(x_test.iloc[i, :]).T)
                pred0.append(pred0_i[0])
                avg0.append(np.mean(y_i[i:]))

        self.pred = pd.Series(pred0, index=x_test.index)
        self.avg_y = pd.Series(avg0, index=x_test.index)
        self.model = model

class pipe_transf(Pipeline):
    # classe para a cross-validação do estimador RFECV, 
    # pois ele não admite transformação nos dados
    def fit(self, x, y=None, **fit_params):
        super(pipe_transf, self).fit(x, y, **fit_params)
        self.coef_ = self.steps[1][1].coef_
        return self        

# CLASSE GENÉRICA PARA OS ESTIMADORES
class S_all_estimator:
    ''' Objetivo: calcular as projecoes segundo uma lista de algoritmos e 
    guardar suas estatisticas
    '''
    def __init__(self, y, x, saz=False, work_days=False, country=None, transf=None):
        index = x.index
        k = x.shape[1]
        
        if freq_df(x) == 'M':
            self.frequency = 12
        elif freq_df(x) == 'Q':
            self.frequency = 4
            
        if saz:
            # Inclui as dummies mensais para as regressões
            d_months = pd.get_dummies(index.month, prefix='D_M', prefix_sep='')
            d_months.index = index
            x = pd.concat([x, d_months], axis=1)
         
        if work_days == True:
            # Inclui a variavel de dias uteis
            wd = workdays_series(country, transf = transf)
            x = pd.concat([x, wd], axis=1, join='inner')

        fit_int = False
        norm_X = False
        parallel = 1
        cv_method = TimeSeriesSplit(self.frequency)
        el_net_l1_ratio = [.1, .5, .7, .9, .95, .99, 1]
        bag_n_estimators = [5, 10, 20, 50]
        adab_n_estimators = [10, 50, 100]
        adab_learn_rate = [0.1, 0.2, 0.5]
        arima_n_models = 50

        self.y = y
        self.x = x
        self.ar_elem = self.__check_ar_elem()

        models_par = {}
        models_npar = {}

        models_par['mlp_reg'] = GridSearchCV(make_pipeline(StandardScaler(),
                              MLPRegressor()),
                                      param_grid={'mlpregressor__hidden_layer_sizes':
                                      [(round(.66*k), round(.33*k)), (round(.75*k), round(.50*k), round(.25*k)),
                                       (round(.80*k), round(.60*k), round(.40*k), round(.20*k))]},
                                      cv=cv_method, refit=True, n_jobs=parallel)
        models_par['gp_reg'] = GridSearchCV(make_pipeline(StandardScaler(),
                              GaussianProcessRegressor(normalize_y=norm_X)),
                                      param_grid={'gaussianprocessregressor__kernel':
                                          [WhiteKernel(), ConstantKernel(), RBF(),
                                           Matern(), RationalQuadratic(), DotProduct()]},
                                      cv=cv_method, refit=True, n_jobs=parallel)
        models_par['ridgecv'] = make_pipeline(StandardScaler(),
                             RidgeCV(fit_intercept=fit_int, normalize=norm_X, cv=cv_method))
        models_par['bay_rid'] = make_pipeline(StandardScaler(),
                              BayesianRidge(fit_intercept=fit_int, normalize=norm_X))
        models_par['lassocv'] = make_pipeline(StandardScaler(),
                              LassoCV(fit_intercept=fit_int, normalize=norm_X, n_jobs=parallel, cv=cv_method))
        models_par['laslrscv'] = make_pipeline(StandardScaler(),
                              LassoLarsCV(fit_intercept=fit_int, normalize=norm_X,
                                      n_jobs=parallel, cv=cv_method))
        models_par['larscv'] = make_pipeline(StandardScaler(),
                              LarsCV(fit_intercept=fit_int, normalize=norm_X, n_jobs=parallel, cv=cv_method))
        models_par['elasnet'] = make_pipeline(StandardScaler(),
                              ElasticNetCV(l1_ratio=el_net_l1_ratio, fit_intercept=fit_int,
                                      normalize=norm_X, n_jobs=parallel, cv=cv_method))
        models_par['hub_reg'] = GridSearchCV(make_pipeline(StandardScaler(),
                              HuberRegressor(fit_intercept=fit_int)),
                                      param_grid={'huberregressor__epsilon': [1.1, 1.2, 1.35],
                                                  'huberregressor__alpha': [0.0001, 0.01, 0.1, 0.3]},
                                      cv=cv_method, refit=True, n_jobs=parallel)
        models_par['ort_purs'] = make_pipeline(StandardScaler(),
                              OrthogonalMatchingPursuitCV(fit_intercept=fit_int,
                                      normalize=norm_X, n_jobs=parallel, cv=cv_method))
        models_par['ard_reg'] = make_pipeline(StandardScaler(),
                              ARDRegression(fit_intercept=fit_int, normalize=norm_X))
        models_par['sgd_reg'] = GridSearchCV(make_pipeline(StandardScaler(),
                              SGDRegressor(fit_intercept=fit_int, shuffle=False)),
                                      param_grid={'sgdregressor__l1_ratio': el_net_l1_ratio,
                                                  'sgdregressor__loss': ['squared_loss','huber','epsilon_insensitive']},
                                      cv=cv_method, refit=True, n_jobs=parallel)
        models_par['pas_agg'] = make_pipeline(StandardScaler(),
                                 PassiveAggressiveRegressor(fit_intercept=fit_int, shuffle=False))
        models_par['lin_all'] = make_pipeline(StandardScaler(),
                                  LinearRegression(fit_intercept=fit_int, normalize=norm_X, n_jobs=parallel))
        models_par['ols1'] = make_pipeline(StandardScaler(),
                                 SelectFromModel(DecisionTreeRegressor(), prefit=False), LinearRegression())
        models_par['ols2'] = make_pipeline(StandardScaler(),
                                 SelectFromModel(ElasticNetCV(l1_ratio=el_net_l1_ratio, fit_intercept=fit_int,
                                      normalize=norm_X, n_jobs=parallel, cv=cv_method), prefit=False),
                                      LinearRegression())
        models_par['ols3'] = make_pipeline(StandardScaler(),
                               SelectFromModel(LarsCV(fit_intercept=fit_int, normalize=norm_X, n_jobs=parallel,
                                     cv=cv_method), prefit=False),
                                     LinearRegression())
        models_par['ols4'] = make_pipeline(StandardScaler(),
                              SelectFromModel(BayesianRidge(fit_intercept=fit_int, normalize=norm_X), prefit=False),
                                     LinearRegression())
        models_par['ols5'] = GridSearchCV(make_pipeline(StandardScaler(), PCA(), LinearRegression()),
                                     param_grid={'pca__n_components': [1, 2, 3, 4, 5]},
                                     cv=cv_method, refit=True, n_jobs=parallel)
        models_par['d_tree'] = make_pipeline(StandardScaler(), DecisionTreeRegressor())
        models_par['rand_for'] = GridSearchCV(make_pipeline(StandardScaler(),
                                  RandomForestRegressor()),
                                      param_grid={'randomforestregressor__n_estimators':[10, 50, 100]},
                                      cv=cv_method, refit=True, n_jobs=parallel)
        models_par['bag1'] = GridSearchCV(make_pipeline(StandardScaler(),
                               BaggingRegressor(max_samples=0.5, max_features=0.5)),
                                      param_grid={'baggingregressor__n_estimators': bag_n_estimators},
                                      cv=cv_method, refit=True)
        models_par['bag2'] = GridSearchCV(make_pipeline(StandardScaler(),
                               BaggingRegressor(LinearRegression(fit_intercept=fit_int,
                                      normalize=norm_X, n_jobs=parallel), max_samples=0.5, max_features=0.5)),
                                      param_grid={'baggingregressor__n_estimators': bag_n_estimators},
                                      cv=cv_method, refit=True, n_jobs=parallel)
        models_par['bag3'] = GridSearchCV(make_pipeline(StandardScaler(),
                                  BaggingRegressor(PassiveAggressiveRegressor(fit_intercept=fit_int, shuffle=False),
                                      max_samples=0.5, max_features=0.5)),
                                      param_grid={'baggingregressor__n_estimators': bag_n_estimators},
                                      cv=cv_method, refit=True)
        models_par['bag4'] = GridSearchCV(make_pipeline(StandardScaler(),
                               BaggingRegressor(ARDRegression(fit_intercept=fit_int,normalize = norm_X),
                                      max_samples=0.5, max_features=0.5)),
                                      param_grid={'baggingregressor__n_estimators': bag_n_estimators},
                                      cv=cv_method, refit=True)
        models_par['bag5'] = GridSearchCV(make_pipeline(StandardScaler(),
                                BaggingRegressor(OrthogonalMatchingPursuit(fit_intercept=fit_int, normalize=norm_X),
                                      max_samples=0.5, max_features=0.5)),
                                      param_grid={'baggingregressor__n_estimators': bag_n_estimators},
                                      cv=cv_method, refit=True)
        models_par['ada1'] = GridSearchCV(make_pipeline(StandardScaler(),
                                AdaBoostRegressor()),
                                      param_grid={'adaboostregressor__n_estimators': adab_n_estimators,
                                                  'adaboostregressor__learning_rate': adab_learn_rate},
                                      cv=cv_method, refit=True, n_jobs=parallel)
        models_par['ada2'] = GridSearchCV(make_pipeline(StandardScaler(),
                                AdaBoostRegressor(LinearRegression(fit_intercept=fit_int,
                                      normalize=norm_X, n_jobs=parallel))),
                                      param_grid={'adaboostregressor__n_estimators': adab_n_estimators,
                                                  'adaboostregressor__learning_rate': adab_learn_rate},
                                      cv=cv_method, refit=True, n_jobs=parallel)
        models_par['ada3'] = GridSearchCV(make_pipeline(StandardScaler(),
                                AdaBoostRegressor(PassiveAggressiveRegressor(
                                      fit_intercept=fit_int, shuffle=False))),
                                      param_grid={'adaboostregressor__n_estimators': adab_n_estimators,
                                                  'adaboostregressor__learning_rate': adab_learn_rate},
                                      cv=cv_method, refit=True, n_jobs=parallel)
        models_par['ada4'] = GridSearchCV(make_pipeline(StandardScaler(),
                                AdaBoostRegressor(ARDRegression(fit_intercept=fit_int,
                                      normalize=norm_X))),
                                      param_grid={'adaboostregressor__n_estimators': adab_n_estimators,
                                                  'adaboostregressor__learning_rate': adab_learn_rate},
                                      cv=cv_method, refit=True, n_jobs=parallel)
        models_par['ada5'] = GridSearchCV(make_pipeline(StandardScaler(),
                                AdaBoostRegressor(OrthogonalMatchingPursuit(fit_intercept=fit_int, normalize=norm_X))),
                                      param_grid={'adaboostregressor__n_estimators': adab_n_estimators,
                                                  'adaboostregressor__learning_rate': adab_learn_rate},
                                      cv=cv_method, refit=True, n_jobs=parallel)
        models_par['g_boost'] = GridSearchCV(make_pipeline(StandardScaler(),
                                GradientBoostingRegressor()),
                                      param_grid={'gradientboostingregressor__n_estimators': adab_n_estimators,
                                                  'gradientboostingregressor__learning_rate': adab_learn_rate},
                                      cv=cv_method, refit=True, n_jobs=parallel)
        norm_lin = pipe_transf([('std', StandardScaler()),
                                 ('regression', LinearRegression())])
        models_par['rfecv'] = RFECV(estimator=norm_lin, step=1, cv=cv_method, scoring='r2')
        models_npar['arima1'] = make_pipeline(DropFeatures(self.ar_elem), StandardScaler(),
                              SelectFromModel(DecisionTreeRegressor(), prefit=False),
                              S_avg_arima(freq=self.frequency, n_models=arima_n_models))
        models_npar['arima2'] = make_pipeline(DropFeatures(self.ar_elem), StandardScaler(),
                              SelectFromModel(ElasticNetCV(l1_ratio=el_net_l1_ratio, n_jobs=parallel,
                                      fit_intercept=fit_int, normalize=norm_X, cv=cv_method), prefit=False),
                              S_avg_arima(freq=self.frequency, n_models=arima_n_models))
        models_npar['arima3'] = make_pipeline(DropFeatures(self.ar_elem), StandardScaler(),
                              SelectFromModel(LarsCV(fit_intercept=fit_int, normalize=norm_X, n_jobs=parallel,
                                      cv=cv_method), prefit=False),
                              S_avg_arima(freq=self.frequency, n_models=arima_n_models))
        models_npar['arima4'] = make_pipeline(DropFeatures(self.ar_elem), StandardScaler(),
                              SelectFromModel(BayesianRidge(fit_intercept=fit_int, normalize=norm_X), prefit=False),
                              S_avg_arima(freq=self.frequency, n_models=arima_n_models))
        models_npar['arima5'] = S_avg_arima(freq=self.frequency, use_X=False, n_models=arima_n_models)
        self.models_par = models_par
        self.models_npar = models_npar
        
    def calculate(self, n_start=None, models_par_names=None, models_npar_names=None):
        y = self.y.copy()
        x = self.x.copy()
        results = []
        
        if models_par_names == None:
            models_par_names = list(self.models_par.keys())
        if models_npar_names == None:
            models_npar_names = list(self.models_npar.keys())
        
        if models_par_names != []:
            # Modelos em paralelo
            for el in models_par_names:
                t = S_linear_model(y, x, el, self.models_par[el], n_start=n_start)
                t.start()
                results.append(t)
        
            for el in results:
                el.join()
        
        if models_npar_names != []:
            # Modelos sem paralelizar (arima, já paralelizam internamente)
            for el in models_npar_names:
                t = S_linear_model(y, x, el, self.models_npar[el], n_start=n_start)
                t.run()
                results.append(t)
        
        self.results = results
        self.n_start = self.results[-1].n_start
        self.n_end = self.results[-1].n_end
        
    def __check_ar_elem(self):
        X = self.x.copy()
        y = self.y.copy()
        columns = list(X.columns)
        if isinstance(y, pd.core.series.Series):
            y_name = y.name
        elif isinstance(y, pd.core.frame.DataFrame):
            y_name = list(y.columns)[0]
        else:
            y_name = 'nparray_with_no_name'  # Coloco um nome genérico proposital para não haver match

        ar_elem = []
        for i in range(1, 13):
            if 'y_'+str(i) in columns:
                ar_elem.append('y_'+str(i))
            if y_name+'_'+str(i) in columns:
                ar_elem.append(y_name+'_'+str(i))
            if 'D_M'+str(i) in columns:
                ar_elem.append('D_M'+str(i))
        return ar_elem




 
    
    
    
    
    
    
    
    
    