import sys
import numpy as np
import pandas as pd
sys.path.append(r'F:\SISTDAD\MEMPGRP\BMORIER\python\lib')
sys.path.append(r'Z:\Macroeconomia\codes\Projetos\MLEco')
sys.path.append(r'Z:\Macroeconomia\codes')
sys.path.append(r'Z:\Macroeconomia\databases')
from mongo_load import transform_series
from mDataStore.globalMongo import mds
import mDataStore.freqHelper as f
from S_clean_db import S_clean_db
from S_univariate_selection import S_univariate_selection
from S_linear_model_vp import S_all_estimator
from bokeh.plotting import figure, show
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer

# PACOTES DO R
from rpy2.robjects.packages import importr
from rpy2.robjects import r, pandas2ri
import rpy2.robjects as ro
stats = importr('stats')
base = importr('base')
utils = importr('utils')
#utils.install_packages('MCS')  # Para instalar o pacote
mcs = importr('MCS')


class S_complete:
    def __init__(self, series, transformation='mom', frequency='monthly'):
       
        self.series = series
        self.transformation = transformation 
        self.warnings = []
        if frequency == 'monthly':
            self.freq = f.monthBegin
        elif frequency == 'quarterly':
            self.freq =  f.quarterBegin
        
        self.name = series + '_' + transformation + '_' + frequency
        self.old_obj = mds.obj.load(self.name, path='economia')
        self.db = mds.read(name=series, freq=self.freq, library=mds.econVS)
        self.summary = {}
        self.accuracy = pd.DataFrame()
        self.country = self.db.md['country']
        self.proj_ponta = None
        
        #### pensar nos casos em que:
        #### 1. pegamos variaveis com frequencia mensal e as transformamos para trimestral
        #### 2. pegamos variáveis com frequencia trimestral
        if  self.old_obj == (None, None):
            self.update = False
            self.tested_lags_y = None
            self.tested_lags_x = None
            self.models_par = []
            self.models_npar = []
            self.prediction = {}
            self.avg_y = None
            self.y = {}
            self.x = {}
            self.selected_dict = {}
            self.n_start = None
            self.n_end = None
            self.config = {}
            self.mcs = []
            self.models = {}
            self.mongo_list = []
            self.colsorder = None
            
        else:
            self.update = True
            obj = self.old_obj[1]['obj']
            self.models_par = obj.models_par
            self.models_npar = obj.models_npar
            self.prediction = obj.prediction
            self.avg_y = obj.avg_y
            self.y = obj.y
            self.x = obj.x
            self.selected_dict = obj.selected_dict
            self.n_start = obj.n_start
            self.n_end = obj.n_end
            self.config = obj.config
            self.mcs = obj.mcs
            self.models = obj.models
            self.mongo_list = obj.mongo_list
            self.colsorder = self.x['select'].columns.to_list()


    def run_(self, delete=False, **kwargs):
        if delete:
            self.__delete()
            
        else:    
            if self.update:
                config = self.config
                for key, value in kwargs.items(): 
                    config[key] = value
                if config != self.config:
                    print('You are trying to run the model with different configuration.')
                    return
                # Sempre recupera a séries e roda o estimate (se não houver nada de novo não roda nada)
                self.__recover_series()
                self.__estimate(saz=config['saz'], min_est_prop=config['min_est_prop'], work_days=config['work_days'])
                if self.x['select'].index[-1] != self.x['recover'].index[-1]:
                    self.__proj()
            
            else:
                # Configuração default
                config = {'check_real':True, 'check_seas':True, 'min_y_sample':0.8, 'mongo_list':None,
                          'lags_y':1, 'lags_x':(0, 4), 'k':None, 'prop':0.8, 'method':'mutual_info_regression',
                          'saz':True, 'min_est_prop':.8, 'work_days': True}
                for key, value in kwargs.items():
                    config[key] = value
                self.config = config
                self.__clean(check_real=config['check_real'], check_seas=config['check_seas'], min_y_sample=config['min_y_sample'], mongo_list=config['mongo_list'], 
                             lags_y=config['lags_y'], lags_x=config['lags_x'])
                self.__select(k=config['k'], prop=config['prop'], method=config['method'])
                self.__estimate(saz=config['saz'], min_est_prop=config['min_est_prop'], work_days=config['work_days'])
            
            mds.obj.save(name=self.name, obj=self, path='economia')


    def __clean(self, check_real=True, check_seas=True, min_y_sample=0.8, mongo_list=None, lags_y=1, lags_x=(0, 4)):
        alpha = S_clean_db(target=self.db)
        self.y['raw'] = alpha.y_data
        alpha.transform_y(transform=self.transformation)
        alpha.get_db(check_real=check_real, check_seas=check_seas, min_y_sample=min_y_sample, mongo_list=mongo_list)
        alpha.make_lags(lags_y=lags_y, lags_x=lags_x)

        self.tested_lags_y = lags_y
        self.tested_lags_x = lags_x
        
        if lags_y == 0 and lags_x == (0, 0):
            with_lags = False
            alpha.check_rel_date(with_lags=with_lags, new_output=False, update_mongo_list=True)
            self.x['clean'] = alpha.x_df
        else:
            with_lags = True
            alpha.check_rel_date(with_lags=with_lags, new_output=False, update_mongo_list=True)
            self.x['clean'] = alpha.x_df_l

        self.y['clean'] = alpha.y_data
        self.mongo_list = alpha.x_mongo_list


    def __select(self, k=None, prop=0.8, method='mutual_info_regression'):
        beta = S_univariate_selection(y=self.y['clean'], x=self.x['clean'])
        beta.select(k=k, prop=prop, method=method)

        self.y['select'] = beta.y
        self.x['select'] = beta.x_select
        self.selected_dict = beta.selected_dict
        self.colsorder = self.x['select'].columns.to_list()

        mongo_list = []
        for el in self.mongo_list:
            iname = el['name']
            for var_i in self.selected_dict.keys():
                if var_i == iname:
                    mongo_list.append(el)

        self.mongo_list = mongo_list
        
        
    def __estimate(self, saz=False, min_est_prop=.8, models_par=None, models_npar=None, work_days=False):
        gamma = S_all_estimator(y=self.y['select'], x=self.x['select'], saz=saz, work_days=work_days, country=self.country, transf=self.transformation)
        new = True
        if self.update:
            prediction = self.prediction
            avg_y = self.avg_y
        
            # Fazendo projeções para os novos modelos desde o início
            new_par = [s for s in list(gamma.models_par.keys()) if s not in self.models_par]
            new_npar = [s for s in list(gamma.models_npar.keys()) if s not in self.models_npar]  # NÃO ESTÁ ATUALIZANDO MODELOS QUE FORAM RODADOS MAS NÃO FORAM SALVOS
            if new_par == [] and new_npar == []: 
                new = False

            if new:
                gamma.calculate(n_start=self.n_start, models_par_names=new_par, models_npar_names=new_npar)
                
                # Salvando os resultados dos novos modelos no dicionário
                for el in gamma.results:
                    self.models[el.model_name] = el.model
                    if len(np.argwhere(np.isnan(el.pred))) == 0:            
                        prediction[el.model_name] = el.pred
                    else:
                        self.warnings.append([el.model_name])
            
            # Fazendo projeções para os modelos já existentes a partir do último ponto
            old_par = [s for s in list(gamma.models_par.keys()) if s not in new_par]
            old_npar = [s for s in list(gamma.models_npar.keys()) if s not in new_npar]

            if self.n_end < len(self.y['select']):
                gamma.calculate(n_start=self.n_end, models_par_names=old_par, models_npar_names=old_npar)
                # Salvando os resultados dos modelos antigos nas pontas do dicionário
                for el in gamma.results:
                    self.models[el.model_name] = el.model
                    # Tira os modelos que geraram nan
                    if len(np.argwhere(np.isnan(el.pred))) == 0:
                        for i in range(len(el.pred)):
                            prediction[el.model_name][el.pred.index[i]] = el.pred[i]
                    else:
                        self.warnings.append([el.model_name])
                avg_y1 = gamma.results[0].avg_y

                if len(np.argwhere(np.isnan(avg_y1))) != 0:
                    for i in range(len(avg_y1)):
                        avg_y[avg_y1.index[i]] = avg_y1[i]
                self.avg_y = avg_y
                self.n_end = gamma.n_end
            
        else:
            prediction = {}
            gamma.calculate()
            for el in gamma.results:
                self.models[el.model_name] = el.model
                if len(np.argwhere(np.isnan(el.pred))) == 0:
                    prediction[el.model_name] = el.pred
                    self.avg_y = el.avg_y
                else:
                    self.warnings.append([el.model_name])
            self.n_start = gamma.n_start
            self.n_end = gamma.n_end
            
        # Atualiza a lista dos modelos rodados para guardar no objeto
        self.prediction = prediction
        self.models_par = [s for s in prediction.keys() if s in gamma.models_par.keys()]
        self.models_npar = [s for s in prediction.keys() if s in gamma.models_npar.keys()]


    def __recover_series(self):
#        if vars_dict is None:
        mongo_list = self.mongo_list.copy()
        alpha = S_clean_db(target=self.db)
        alpha.transform_y(transform=self.transformation)
        alpha.get_db(mongo_list=mongo_list)
        alpha.make_lags(lags_y=self.config['lags_y'], lags_x=self.config['lags_x'])
        x = alpha.x_df_l.dropna(axis=0, how='any')
        y = alpha.y_data
        y = y.align(x, axis=0, join='inner')[0]
        
        # Fazendo lista com nomes de variáveis (key + lag)
        var_names = []
        for el in self.selected_dict:
            for lag in self.selected_dict[el]:
                if lag == 0:
                    var_names.append(el)
                else:
                    var_names.append(el+'_'+str(lag))
        
        x_recover = alpha.x_df_l.loc[x.index[0]:, var_names]
        y_recover = alpha.y_data.loc[x.index[0]:]
        x_recover = x_recover.reindex(columns=self.colsorder)
        x_select = x.loc[:, var_names]
        x_select = x_select.reindex(columns=self.colsorder)
        self.x['select'] = x_select
        self.x['recover'] = x_recover
        self.y['select'] = y
        self.y['recover'] = y_recover
        
#        else:
#            # Recuperando o y formatado  
#            y_data = self.db.iloc[:,0]
#            y = pd.DataFrame(y_data)
#            y = transform_series(df=y, transf= self.transformation)            
#            #### as funções ainda nao estao conversando 100% e portanto estou precisando fazer alguns ajustes
#            l = len(self.y['select'])
#    
#            # Recuperando os X formatado
#            if 'y' in list(vars_dict.keys()):
#                vars_dict[self.series] = vars_dict.pop('y')
#    
#            df_out = pd.DataFrame()
#            for var, lags in vars_dict.items():
#                db = mds.read(name=var, freq=self.freq, library=mds.econVS)
#                data = db.iloc[:,0]
#                df = pd.DataFrame(data)
#                df = transform_series(df=df, transf= self.transformation)
#            
#                for i in range(len(lags)):
#                # Cria os lags de X e anexa a matriz
#                    if lags[i] == 0:
#                        df_l = df.rename(columns={list(df.columns)[0]:var})
#                    else:
#                        df_l = df.shift(lags[i])
#                        df_l = df_l.rename(columns={list(df.columns)[0]:var+'_'+str(lags[i])})
#              
#                    df_out = pd.concat([df_out, df_l], axis=1)
#            
#            df_out = df_out.dropna(axis=0, how='any')
#            self.x['select'] = df_out.iloc[(len(df_out)-l):]
#            self.y['select'] = y.align(self.x['select'], axis=0, join='inner')[0]


    def __proj(self):
        x = pd.DataFrame(IterativeImputer().fit_transform(self.x['recover']),
                            index=self.x['recover'].index,
                            columns=self.x['recover'].columns)
        # Cria o objeto gamma para poder recuperar o x com dummies sazonais e work_days quando é o caso
        y = self.y['recover'].align(x, join='outer', axis=0)[0]
        gamma = S_all_estimator(y=y, x=x, saz=self.config['saz'], work_days=self.config['work_days'],
                                country=self.country, transf=self.transformation)
        x = gamma.x.copy()

        models = self.models
        y_pred = {}
        for el in models:
            y_pred[el] = pd.Series(models[el].predict(x), index=x.index)
        
        self.proj_ponta = y_pred


    def __delete(self):
        mds.obj.delete(self.name, path='economia')


    def __summary_measures(self):    
        pred = pd.DataFrame.from_dict(self.prediction)
        if self.proj_ponta is not None:
            ponta = pd.DataFrame.from_dict(self.proj_ponta)
            pred = pd.concar([pred, ponta])
        
        window = 12
        qe_inv = self.__eqm(pred, window)[0]**(-1)
        errors_out = self.__eqm(pred, window)[1]
        rsq_out = self.__rsq_out(pred, window)
        
        qe_inv[np.isinf(qe_inv)] = 0

        w_eqm = qe_inv.divide(qe_inv.sum(axis=1), axis=0)
        w_eqm = w_eqm.rolling(window).mean()
        w_rqo = rsq_out.divide(rsq_out.sum(axis=1), axis=0)
        w_rqo = w_rqo.dropna(axis=0, how='any')
        
        if self.mcs == []:
            mcs_out = self.__model_confidence_set(errors_out)
            self.mcs = mcs_out
        else: 
            mcs_out = self.mcs

        est_mean = pred.mean(axis=1)
        est_ols = pred.loc[:,[x for x in pred.keys() if 'ols' in x]].mean(axis=1)
        est_ada = pred.loc[:,[x for x in pred.keys() if 'bag' in x]].mean(axis=1)
        est_bag = pred.loc[:,[x for x in pred.keys() if 'ada' in x]].mean(axis=1)           
        est_ari = pred.loc[:,[x for x in pred.keys() if 'arima' in x]].mean(axis=1)
        est_med = pred.median(axis=1)

        est_eqm = w_eqm*pred
        est_eqm = est_eqm.sum(axis=1)
        est_rqo = w_rqo*pred
        est_rqo = est_rqo.sum(axis=1)
        est_mcs = pred.loc[:, mcs_out].mean(axis=1)

        ests = pd.concat([est_mean, est_ols, est_ada, est_bag, est_ari, est_med, est_eqm, est_rqo, est_mcs], axis=1)
        ests.columns = ['avg', 'avg_ols', 'avg_ada', 'avg_bag', 'avg_ari', 'med', 'EQM', 'RSQ', 'MCS']        
        
        estimators = pd.concat([ests, pred], axis=1)
        estimators = estimators.iloc[window:,]
        
        errors_out = pd.concat([self.__eqm(ests, window)[1], errors_out], axis=1)
        errors_out = errors_out.iloc[window:,]

        rsq_out = self.__rsq_out(estimators, window = window)
        self.summary['estimators'] = estimators 
        self.summary['errors_out'] = errors_out
        self.summary['rsq_out'] = rsq_out
        
        # convertendo as estimativas MoM em YoY para comparar as projeções
        y_lvl = self.y['raw']
        y_lvl = y_lvl.align(estimators, join='outer')[0]
        if self.transformation == 'mom':
            y_shift_1 = y_lvl.shift(periods=1)
            data_old = y_shift_1.align(estimators, join='inner')
            y_proj = data_old[0].add(data_old[1])
            
            y_shift_12 =  y_lvl.shift(periods=12)
            data_new = y_shift_12.align(y_proj, join='inner')
            est_new = data_new[1].sub(data_new[0])
            self.summary['alt_est_yoy'] = est_new
            
        else:
            y_shift_12 = y_lvl.shift(periods=12)
            data_old = y_shift_12.align(estimators, join='inner')
            y_proj = data_old[0].add(data_old[1])
            
            y_shift_1 =  y_lvl.shift(periods=1)
            data_new = y_shift_1.align(y_proj, join='inner')
            est_new = data_new[1].sub(data_new[0])
            self.summary['alt_est_mom'] = est_new

        
#        # Gerando séries de intervalos de confiança
#        c_int = pd.DataFrame()
#        for model in pred.columns:
#            c_int[model] = self.__make_cinterval(estimators[model])
#        self.summary['c_int'] = c_int
    
    def __rsq_out(self, df, window = 12):
        rol_avg_y = self.avg_y
        y = self.y['select']
        
        alg = y.align(df, axis=0, join='inner')
        y = alg[0]
        df = alg[1]
        alg = rol_avg_y.align(df, axis=0, join='inner')
        rol_avg_y = alg[0]
        
        errors_out = df.sub(y, axis=0)
        qe = errors_out**2
        
        qt = (rol_avg_y - y)**2
                
        rsq_out = 1 - qe.rolling(window).sum().divide(qt.rolling(window).sum(), axis=0)
        rsq_out[rsq_out < 0] = 0
        
        return rsq_out
    
    def __eqm(self, df, window = 12):    
        y = self.y['select']

        alg = y.align(df, axis=0, join='inner')
        y = alg[0]
        df = alg[1]
        
        errors_out = df.sub(y, axis=0)
        eqm = errors_out**2
        
        return eqm, errors_out

      
    def __model_confidence_set(self, Loss, alpha=0.20, statistic='Tmax'):
        pandas2ri.activate()
        ro.r('''
        # Criando uma função do R:
       
        rmcs = function(Loss=Loss, alpha=alpha, statistic=statistic) {
            mcs_out = MCSprocedure(Loss)
            set = mcs_out@Info["model.names"]
            return(set)
        }'''
        )
        rmcs = ro.r['rmcs']
        output = list(rmcs(Loss=Loss, alpha=alpha, statistic=statistic)[0])
        return output

    def __bench(self, bench):
        if self.summary == {}:   self.__summary_measures()
            
        y_test = self.y['select']
        # Calculando os desvios do bench em relação ao número efetivo
        y_test = y_test.iloc[self.n_start:self.n_end,]
        alg = bench.align(y_test, axis=0, join='inner')
        bench = alg[0]
       
        dif = len(y_test) - len(bench)
        if dif > 0:
            bench.name = bench.name + '_' + str(dif)
       
        accuracy = {}
        for el in self.summary['estimators'].columns:
            predi = self.summary['estimators'][el]
            alg = bench.align(predi, axis=0, join='inner')
            bench = alg[0]
            predi = alg[1]
            y_test = y_test.align(predi, axis=0, join='inner')[0]
            # vezes que o estimado acertou o vies da BBG para cima
            up_bias = sum((y_test > bench) & (predi > bench))
            # vezes que o estimado acertou o vies da BBG para baixo
            down_bias = sum((y_test < bench) & (predi < bench))
            # frequencia transformada em proporcao
            accuracy[el] = (up_bias + down_bias) / len(bench)
        
        self.accuracy = accuracy
        self.summary['accuracy'] = accuracy
        
    def plotE(self, md):
        if self.summary == {}:   self.__summary_measures()
             
        plot_data = pd.DataFrame.from_dict(self.summary['errors_out'][md])
        from bokeh.palettes import Blues8 as pallete
        nc = plot_data.shape[1]
        p = figure(width = 1000, height = 400, x_axis_type = "datetime")
        mypalette = pallete[20][0:nc]
        for (colr, leg, x, y) in zip(
                mypalette, 
                [name for name in plot_data], 
                [plot_data.index.values] * nc, 
                [plot_data[name].values for name in plot_data]):
            p.line(x, y, color= colr, legend= leg)
        show(p)
        
    def plotP(self, md, ic=True, bench=None):
        if self.summary == {}:   self.__summary_measures()
        
        data = pd.DataFrame.from_dict(self.summary['estimators'][md])
        #data = pd.DataFrame(data = data[md])
        test = self.y['select']
        from bokeh.palettes import Blues8 as pallete
        nc = data.shape[1]
        bpalette = pallete[0:nc]        
        
        plot_data = pd.concat([data, test], axis=1)
        plot_data.columns = md + ['test_variable']
        mypalette = bpalette + ['red']

        if bench is not None:
            plot_data = pd.concat([bench, plot_data], axis=1)
            mypalette = ['orange'] + mypalette

        plot_data = plot_data.iloc[-16:,]
        nc = len(plot_data)
        p = figure(width = 1000, height = 400, x_axis_type = "datetime")
        for (colr, leg, x, y) in zip(
                mypalette, 
                [name for name in plot_data], 
                [plot_data.index.values] * nc, 
                [plot_data[name].values for name in plot_data]):
            p.line(x, y, color= colr, legend= leg)
#        if ic == True:
#            p.multi_line([self.data.pred_range[md].index.values,
#                          self.data.pred_range[md].index.values],
#                         [self.data.pred_range[md]['l_bound'].values,
#                          self.data.pred_range[md]['u_bound'].values], 
#                          color=bpalette[0], alpha=.3)
        show(p)
        
    def stats(self, bench):
        if self.summary == {}:   self.__summary_measures()
        self.__bench(bench)

        rsq_out = self.__rsq_out(bench)
        rsq_out = round(rsq_out.dropna().tail(1), 3).values
        eqm_bch = self.__eqm(bench)[0]
        eqm_bch = round(eqm_bch.tail(1), 3).values
        
        eqm = self.summary['errors_out'].tail(1)
        r2out = self.summary['rsq_out'].tail(1)
        accu = pd.DataFrame.from_dict([self.summary['accuracy']])
        accu.index = r2out.index.values
        
        table = pd.concat([round(eqm, 2), round(r2out, 2), round(accu, 2)], axis=0).transpose()
        table.columns = ['EQM', 'R2 out', 'Accuracy']
        
        bch = pd.DataFrame({'EQM': eqm_bch, 'R2 out': rsq_out, 'Accuracy': float('NaN')}, index=['bench'])
        table = pd.concat([bch, table], axis=0)

        return table

#    def __c_interval(self, e_series, prev, alpha=0.10, k_boot=1000):
#        # Inputs:
#        #   e_series : pd.Series, série de erros fora da amostra. Todos serão
#        #              usados.
#        #   prev : previsão PONTUAL (é um float64).
#        #   k_boot : números de sorteios do bootstrapping.
#        # A construção do intervalo de confiança se da sorteando k_boot (com
#        # reposição) de erros da série e_series. Soma-se esses erros a prev
#        # e constroi-se o intervalo de confiança da previsão a partir das
#        # frequências vistas na amostra bootstrap.
#        sampling = np.random.choice(e_series, size=k_boot, replace=True)
#        projs = sampling + prev
#        l_bound = alpha*100/2
#        u_bound = (1 - alpha/2)*100
#        return np.percentile(projs, [l_bound, u_bound])
#    
#    def __make_cinterval(self, md, min_sample=15, alpha=0.10, k_boot=1000):
#        e_series = self.summary['errors_out'][md]
#        pred_series = self.summary['estimators'][md]
#        cint_df = pd.DataFrame(data=None, index=e_series.index[min_sample:],
#                                  columns=['l_bound', 'u_bound'])
#        for i in range(len(e_series)-min_sample):
#            e_sample = e_series[:(min_sample + i)]
#            pred_i = pred_series[len(e_sample)]
#            cint_df.iloc[i, 0], cint_df.iloc[i, 1] = self.__c_interval(e_series,
#                                                     pred_i, alpha=alpha,
#                                                     k_boot=k_boot)
#        return cint_df
