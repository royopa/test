import sys
sys.path.append(r'F:\SISTDAD\MEMPGRP\BMORIER\python\lib')
sys.path.append(r'Z:\Macroeconomia\codes\Projetos\MLEco\backup10.09')
sys.path.append(r'Z:\Macroeconomia\databases')
from mDataStore.globalMongo import mds
import mDataStore.freqHelper as f
from mongo_load import mongo_load, check_freq, numerate_freq
from S_clean_db import S_clean_db as sl_clean
from S_univariate_selection import S_univariate_selection as sl_select
from S_linear_model import S_all_estimator as sl_estimate
from datetime import datetime

import time

import pandas as pd

#=BDS('ticker';"CALENDAR_NON_SETTLEMENT_DATES";"SETTLEMENT_CALENDAR_CODE";'country';"CALENDAR_START_DATE=20180101";"CALENDAR_END_DATE=20181231";"Dir=H";"cols=11;rows=1")

#idx_drop = pd.DatetimeIndex([datetime(2018,5,1), datetime(2019,5,1)])

df_raw = pd.read_excel(
         r'F:\DADOS\ASSET\MACROECONOMIA\DADOS\Atividade\INDUSTRIA\IBGE\PIM_MODELOS.xlsm',
         sheet_name='python', index_col=0).dropna()
y_bench_mom = df_raw.iloc[:,-1]
y_bench_yoy = df_raw.iloc[:,-2]

df_raw = pd.read_excel(
         r'F:\DADOS\ASSET\MACROECONOMIA\DADOS\Atividade\INDUSTRIA\IBGE\PIM_MODELOS.xlsm',
         sheet_name='mjxbbg', index_col=0).dropna()
yy_bench_mom = df_raw.iloc[:,-1]
yy_bench_yoy = df_raw.iloc[:,-2]

#Y_eco = df_raw.iloc[:,0]; X_eco = df_raw.iloc[:,1:-1]
#Y_eco = Y_eco.drop(index=idx_drop)
#X_eco = X_eco.drop(index=idx_drop)

## Teste
# test = make_pipeline(DropFeatures(['PIM_1']), StandardScaler(),
#                              SelectFromModel(DecisionTreeRegressor(), prefit = False),
#                              S_avg_arima())
# test.fit(X_eco.iloc[:-1,:],Y_eco.iloc[:-1])
# test.predict(pd.DataFrame(X_eco.iloc[-1,:]).T)



## APENAS ARIMA
# test = S_avg_arima()
# tic = time.clock()
# test.fit(X_eco.iloc[:-1, 1:], Y_eco.iloc[:-1])
# toc = time.clock()
# time_arima = toc - tic
# test.predict(pd.DataFrame(X_eco.iloc[-1, 1:]).T)




#eco = sl_estimate(y=Y_eco, X=X_eco)
#tic = time.clock()
#eco.calculate(al=True)
#toc = time.clock()
#time_eco = toc - tic
#print('Eco model (10 variables) elapsed time:'+str(toc-tic)+'seconds')
#eco.bench(bench=y_bench)
#eco.plotP(md='avg_mcs',bench=y_bench)
#eco.stats()





db_pim = mds.read(name='pim_1 Industria geral', freq=f.monthBegin, library=mds.econVS)


alpha = sl_clean(target=db_pim)
alpha.transform_y(transform='yoy')
alpha.get_db()
alpha.make_lags()
alpha.check_rel_date()

Y  = alpha.y_data
X  = alpha.X_df_l
#Xl = alpha2.X_df_l

beta = sl_select(y = Y, X = X)
#beta_eco.select_prop(proportion = 0.8, method = 'f_regression') #mutual_info_regression
beta.select_prop(proportion = 0.8, method = 'mutual_info_regression')      #mutual_info_regression

Ym    = beta.y
Xm    = beta.X_prop
#vrs = beta_eco.selected_feat

#Y = Y.drop(index=idx_drop)
#X_k = X_k.drop(index=idx_drop)

tic = time.clock()
gamma_eco = sl_estimate(y = Ym, X = Xm)
gamma_eco.calculate()
toc = time.clock()
time_gamma_eco = toc - tic
print('Gamma Eco model (constrained) elapsed time:'+str(toc-tic)+'seconds')











gamma_eco.bench(bench=y_bench)
#gamma_eco.plotP(md='avg_mcs',bench=y_bench)
gamma_eco.stats()



tic = time.clock()

alpha = sl_clean(target=db_pim)
alpha.transform_y('yoy')
alpha.get_db(check_real=True, check_seas=True, min_y_sample=0.8, mongo_list=None)
alpha.make_lags(lags_y=1, lags_X=(0, 4))
alpha.check_rel_date(with_lags=True, new_output=False, update_mongo_list=True)

Y  = alpha.y_data
#X  = alpha.X_df
Xl = alpha.X_df_l

beta = sl_select(y = Y, X = Xl)
beta.select_prop(prop = 0.8, method = 'f_regression') #mutual_info_regression
#beta.select_k(k = 120, method = 'f_regression')      #mutual_info_regression

Y      = beta.y
X_prop = beta.X_prop
vars_prop = beta.selected_prop

#Y = Y.drop(index=idx_drop)
#X_prop = X_prop.drop(index=idx_drop)

gamma = sl_estimate(y = Y, X = X_prop)
tic = time.clock()
gamma.calculate()
toc = time.clock()
time_gamma = toc - tic
print('Gamma model (standard) elapsed time:'+str(toc-tic)+'seconds')
gamma.bench(bench=y_bench)
#gamma.plotP(md='avg_mcs',bench=y_bench)
gamma.stats()

toc = time.clock()
toc - tic




#db_pim = mds.read(name='pim_1 Industria geral', freq=f.monthBegin, library=mds.econVS)

#alpha1 = sl_clean(target=db_pim)
#alpha1.transform_y('yoy')
#alpha1.get_db(check_real=True, check_seas=True, min_y_sample=0.8, mongo_list=None)
#alpha1.make_lags(lags_y=0, lags_X=(0, 0))
#alpha1.check_rel_date(with_lags=False, new_output=False, update_mongo_list=True)

#Y  = alpha1.y_data
#X  = alpha1.X_df
#Xl = alpha1.X_df_l

#beta1 = sl_select(y = Y, X = X)
#beta1.select_prop(proportion = 0.8, method = 'f_regression') #mutual_info_regression
#beta1.select_k(k = 120, method = 'f_regression')             #mutual_info_regression

#Y      = beta1.y
#X_prop = beta1.X_prop

#Y = Y.drop(index=idx_drop)
#X_prop = X_prop.drop(index=idx_drop)

#gamma1 = sl_estimate()
#gamma1.calculate(y = Y, X = X_prop)

#gamma1.bench(bench=y_bench)
#gamma1.plotP('avg_mcs')
#gamma1.stats()

selected = {}

look_for_variables = selected_feat
i = 0
while len(look_for_variables) != 0:
    var = look_for_variables[0]
    
    try:
        int(var[-1])
        var = var[:-2]
    except:
        pass
    
    ids = [s for s in range(len(look_for_variables)) if var in look_for_variables[s]]
    vars = [look_for_variables[s] for s in ids]
    look_for_variables = [look_for_variables[s] for s in range(len(look_for_variables)) if s not in ids]
    
    try:
        lags = [int(s[-1]) for s in vars]
    except ValueError:
        lags = [0] + [int(s[-1]) for s in vars[1:]]
    
    selected[var] = lags



