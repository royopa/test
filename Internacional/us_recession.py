import pandas as pd
from datetime import datetime
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import RidgeClassifierCV, Perceptron
from sklearn.linear_model import PassiveAggressiveClassifier, SGDClassifier
from sklearn.linear_model import LogisticRegressionCV
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
import xlwings as xw
import numpy as np

df_raw = pd.read_excel(
        r'F:\DADOS\ASSET\MACROECONOMIA\INTERNACIONAL\(1) ESTUDOS - DIVERSOS\Recession\data_recession.xlsx',
        sheet_name='mom', index_col=0).dropna()

y = df_raw.loc[: , 'recession']
X = df_raw.iloc[: , 1:].align(y, axis=0,join='inner')[0]

X_ext = pd.date_range(start=X.index.min(), freq="MS", periods=len(X)+5)

new_month = pd.date_range(start=X.index[-1], periods=4, freq='MS')
new_month = pd.Series(new_month)
X_ext = X.copy()
X_ext.loc[new_month[1], :] = np.nan
X_ext.loc[new_month[2], :] = np.nan
X_ext.loc[new_month[3], :] = np.nan

for series in X.columns:
    name_3 = series+'_3'
    name_6 = series+'_6'
    name_12 = series+'_12'

    series_3 = X_ext[series].shift(3)
    series_3.name = name_3
    series_6 = X_ext[series].shift(6)
    series_6.name = name_6
    series_12 = X_ext[series].shift(12)
    series_12.name = name_12
    X = pd.concat([X, series_3, series_6, series_12], axis=1, join='inner')
    X_ext = pd.concat([X_ext, series_3, series_6, series_12], axis=1)
    

X = X.dropna()
y = y.align(X, join='inner')[0]
X = X.drop(['aaa','baa','wti_mom','incl103','m1_mom','m2_mom','usd_mom',
            'ism_inv_mom','ism_man_mom','ism_prices_mom','jobl_claims_mom',
            'gold_mom','spx_mom','wti_vol','spx_vol'], axis=1)
X_ext = X_ext.drop(['aaa','baa','wti_mom','incl103','m1_mom','m2_mom','usd_mom',
                    'ism_inv_mom','ism_man_mom','ism_prices_mom','jobl_claims_mom',
                    'gold_mom','spx_mom','wti_vol','spx_vol'], axis=1)
X_ext = X_ext.dropna()

X_test = X.loc[:datetime(1999, 12, 1), :]
y_test = y.align(X_test, join='inner')[0]


reg1 = make_pipeline(StandardScaler(), RidgeClassifierCV(fit_intercept=False,
                            normalize=False, cv=TimeSeriesSplit(12)))
reg2 = make_pipeline(StandardScaler(), Perceptron(fit_intercept=False))
reg3 = make_pipeline(StandardScaler(), 
                     PassiveAggressiveClassifier(fit_intercept=False))
reg4 = make_pipeline(StandardScaler(), 
                     SGDClassifier(loss = 'log', penalty='elasticnet', fit_intercept=False))
reg5 = make_pipeline(StandardScaler(), 
                     LogisticRegressionCV(cv=TimeSeriesSplit(12), 
                                          penalty='l2', fit_intercept=False))
reg6 = make_pipeline(StandardScaler(), SVC(probability=True))
reg7 = make_pipeline(StandardScaler(), GaussianNB())
reg8 = make_pipeline(StandardScaler(), RandomForestClassifier())

reg1.fit(X_test, y_test)
reg2.fit(X_test, y_test)
reg3.fit(X_test, y_test)
reg4.fit(X_test, y_test)
reg5.fit(X_test, y_test)
reg6.fit(X_test, y_test)
reg7.fit(X_test, y_test)
reg8.fit(X_test, y_test)

prob = {}

prob['Ridge'] = reg1.predict(X)
prob['Perceptron'] = reg2.predict(X)
prob['PassiveAgressive'] = reg3.predict(X)
prob['SGDC'] = reg4.predict_proba(X)[:,1]
prob['LogReg'] = reg5.predict_proba(X)[:,1]
prob['svc'] = reg6.predict_proba(X)[:,1]
prob['gaunb'] = reg7.predict_proba(X)[:,1]
prob['randforclass'] = reg8.predict_proba(X)[:,1]

predict = {}

predict['Ridge'] = reg1.predict(X)
predict['Perceptron'] = reg2.predict(X)
predict['PassiveAg'] = reg3.predict(X)
predict['SGDC'] = reg4.predict(X)
predict['LogReg'] = reg5.predict(X)
predict['SVC'] = reg6.predict(X)
predict['GaussianNB'] = reg7.predict(X)
predict['RandomForest'] = reg8.predict(X)

predict_df = pd.DataFrame(predict)
predict_df.index = y.index
avg_pred = np.mean(predict_df, axis=1)
avg_pred.name = 'media dos modelos'
predict_df = pd.concat([predict_df, avg_pred, y], axis=1)

prob_df = pd.DataFrame(prob)
prob_df.index = y.index
prob_df = pd.concat([prob_df, y], axis=1)

predict_df.to_excel(r'C:\Users\pietcon\Desktop\classifiers.xlsx')
prob_df.to_excel(r'C:\Users\pietcon\Desktop\probabilities.xlsx')

wb = xw.Book(r'F:\DADOS\ASSET\MACROECONOMIA\INTERNACIONAL\(1) ESTUDOS - DIVERSOS\Recession\us_recession.xlsx')
sheet = wb.sheets('output_ots')

sheet.range('A1').value = predict_df

######## IN THE SAMPLE
X_its = X.iloc[:-12, :]
y_its = y.iloc[:-12]

reg1.fit(X_its, y_its)
reg2.fit(X_its, y_its)
reg3.fit(X_its, y_its)
reg4.fit(X_its, y_its)
reg5.fit(X_its, y_its)
reg6.fit(X_its, y_its)
reg7.fit(X_its, y_its)
reg8.fit(X_its, y_its)

predict_its = {}

predict_its['Ridge'] = reg1.predict(X_ext)
predict_its['Perceptron'] = reg2.predict(X_ext)
predict_its['PassiveAgressive'] = reg3.predict(X_ext)
predict_its['SGDC'] = reg4.predict(X_ext)
predict_its['LogReg'] = reg5.predict(X_ext)
predict_its['svc'] = reg6.predict(X_ext)
predict_its['gaunb'] = reg7.predict(X_ext)
predict_its['randforclass'] = reg8.predict(X_ext)

predict_its_df = pd.DataFrame(predict_its)
predict_its_df.index = X_ext.index
avg_pred = np.mean(predict_its_df, axis=1)
avg_pred.name = 'media dos modelos'
predict_its_df = pd.concat([predict_its_df, avg_pred, y], axis=1)

sheet = wb.sheets('output_its')

sheet.range('A1').value = predict_its_df

