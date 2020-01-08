# -*- coding: utf-8 -*-
"""
Created on Fri May 10 15:18:00 2019

@author: marcgut

Modulo que calcula o PIB potencial pela ótica da função de produção.
"""
import pandas as pd  # leitura (em excel) e análise de dados
import numpy as np
import sys  # Funcionalidades do sistema (incluindo caminhos)
sys.path.append(r'Z:\Macroeconomia\codes')  # Para utilizar as funções
import xlwings as xw
import statsmodels.api as sm


base = pd.read_excel(
        r'F:\DADOS\ASSET\MACROECONOMIA\DADOS\Atividade\PIB\PIB potencial\FUNCAO_DE_PRODUCAO.xlsx',
        sheet_name='python', header=0, index_col=0)

alpha = 0.35
gamma = 1
phi = 0.1

emp_t = base['EMP'].mean()

part_t = base['PARTS'].mean()

hour_c, hour_t = sm.tsa.filters.hpfilter(base['HOURST'], 6.25)

nuci_t = base['NUCI'].mean()

LP_t = base['POPW']*part_t*emp_t*hour_t

LP = base['POPW']*base['PARTS']*base['EMP']*base['HOURST']

h_1 = np.exp(phi*base['SAEB_pond']/100)

h_2 = np.exp(phi*base['SAEB_n_pond']/100)

h_3 = np.exp(phi*base['PISA']/100)

h_4 = np.exp(phi*base['avg_sc'])

# Cálculo da TFP com diversas formas funcionais
##################### Y = A((nuciK)^alpha)((hourstL)^(1-alpha)) ##############
######### lnY = lnA + alpha*(lnnuci + lnK) + (1-alpha)*(lnL)#######

# SEM SUAVIZAÇÃO (PIB não potencial)
# sem capital humano
ln_A_1 = np.log(base['Y']) - alpha*(np.log(base['NUCI'])+np.log(base['K']))-\
        (1-alpha)*(np.log(LP))
# com capital humano
# SAEB Ponderado
ln_A_2 = np.log(base['Y']) - alpha*(np.log(base['NUCI'])+np.log(base['K']))-\
        (1-alpha)*(np.log(LP) + np.log(h_1))
# SAEB não ponderado
ln_A_3 = np.log(base['Y']) - alpha*(np.log(base['NUCI'])+np.log(base['K']))-\
        (1-alpha)*(np.log(LP) + np.log(h_2))
# PISA
ln_A_4 = np.log(base['Y']) - alpha*(np.log(base['NUCI'])+np.log(base['K']))-\
        (1-alpha)*(np.log(LP) + np.log(h_3))
# Anos de escolaridade
ln_A_5 = np.log(base['Y']) - alpha*(np.log(base['NUCI'])+np.log(base['K']))-\
        (1-alpha)*(np.log(LP) + np.log(h_4))

# Recuperando TFP
A_1 = np.exp(ln_A_1)
A_2 = np.exp(ln_A_2)
A_3 = np.exp(ln_A_3)
A_4 = np.exp(ln_A_4)
A_5 = np.exp(ln_A_5)

# TFP filtered
hp_A_1 = sm.tsa.filters.hpfilter(A_1, 6.25)[1]
hp_A_2 = sm.tsa.filters.hpfilter(A_2, 6.25)[1]
hp_A_3 = sm.tsa.filters.hpfilter(A_3, 6.25)[1]
hp_A_4 = sm.tsa.filters.hpfilter(A_4, 6.25)[1]
hp_A_5 = sm.tsa.filters.hpfilter(A_5, 6.25)[1]

# PIB Potencial
# sem capital humano
ln_Y_1 = np.log(hp_A_1) + alpha*(np.log(nuci_t) + np.log(base['K'])) + \
         (1 - alpha)*(np.log(LP_t))
# com capital humano
ln_Y_2 = np.log(hp_A_2) + alpha*(np.log(nuci_t) + np.log(base['K'])) + \
         (1 - alpha)*(np.log(LP_t) + np.log(h_1))
ln_Y_3 = np.log(hp_A_3) + alpha*(np.log(nuci_t) + np.log(base['K'])) + \
         (1 - alpha)*(np.log(LP_t) + np.log(h_2))
ln_Y_4 = np.log(hp_A_4) + alpha*(np.log(nuci_t) + np.log(base['K'])) + \
         (1 - alpha)*(np.log(LP_t) + np.log(h_3))
ln_Y_5 = np.log(hp_A_5) + alpha*(np.log(nuci_t) + np.log(base['K'])) + \
         (1 - alpha)*(np.log(LP_t) + np.log(h_4))

# Recupera Y
Y_1 = np.exp(ln_Y_1)
Y_2 = np.exp(ln_Y_2)
Y_3 = np.exp(ln_Y_3)
Y_4 = np.exp(ln_Y_4)
Y_5 = np.exp(ln_Y_5)

# Salva Dataframes
A = pd.concat([hp_A_1, hp_A_2, hp_A_3, hp_A_4, hp_A_5], axis=1)
Y = pd.concat([Y_1, Y_2, Y_3, Y_4, Y_5], axis=1)

# Salva output
wb = xw.Book(r'F:\DADOS\ASSET\MACROECONOMIA\DADOS\Atividade\PIB\PIB potencial\FUNCAO_DE_PRODUCAO.xlsx')
sht = wb.sheets['output_padrao']

sht.range('A1').value = A
sht.range('I1').value = Y


# COM TERMOS DE TROCA
# Cálculo da TFP com diversas formas funcionais
##################### Y = TA((nuciK)^alpha)((hourstL)^(1-alpha)) ##############
######### lnY = lnT + lnA + alpha*(lnnuci + lnK) + (1-alpha)*(lnL) #######

# SEM SUAVIZAÇÃO (PIB não potencial)
# sem capital humano
ln_tA_1 = np.log(base['Y']) - alpha*(np.log(base['NUCI'])+np.log(base['K']))-\
        (1-alpha)*(np.log(LP)) - np.log(base['ttrade'])
# com capital humano
# SAEB Ponderado
ln_tA_2 = np.log(base['Y']) - alpha*(np.log(base['NUCI'])+np.log(base['K']))-\
        (1-alpha)*(np.log(LP) + np.log(h_1)) - np.log(base['ttrade'])
# SAEB não ponderado
ln_tA_3 = np.log(base['Y']) - alpha*(np.log(base['NUCI'])+np.log(base['K']))-\
        (1-alpha)*(np.log(LP) + np.log(h_2)) - np.log(base['ttrade'])
# PISA
ln_tA_4 = np.log(base['Y']) - alpha*(np.log(base['NUCI'])+np.log(base['K']))-\
        (1-alpha)*(np.log(LP) + np.log(h_3)) - np.log(base['ttrade'])
# Anos de escolaridade
ln_tA_5 = np.log(base['Y']) - alpha*(np.log(base['NUCI'])+np.log(base['K']))-\
        (1-alpha)*(np.log(LP) + np.log(h_4)) - np.log(base['ttrade'])

# Recuperando TFP
tA_1 = np.exp(ln_tA_1)
tA_2 = np.exp(ln_tA_2)
tA_3 = np.exp(ln_tA_3)
tA_4 = np.exp(ln_tA_4)
tA_5 = np.exp(ln_tA_5)

# TFP filtered
hp_tA_1 = sm.tsa.filters.hpfilter(tA_1, 6.25)[1]
hp_tA_2 = sm.tsa.filters.hpfilter(tA_2, 6.25)[1]
hp_tA_3 = sm.tsa.filters.hpfilter(tA_3, 6.25)[1]
hp_tA_4 = sm.tsa.filters.hpfilter(tA_4, 6.25)[1]
hp_tA_5 = sm.tsa.filters.hpfilter(tA_5, 6.25)[1]

# PIB Potencial
# sem capital humano
ln_tY_1 = np.log(hp_tA_1) + alpha*(np.log(nuci_t) + np.log(base['K'])) + \
         (1 - alpha)*(np.log(LP_t)) + np.log(base['ttrade'])
# com capital humano
ln_tY_2 = np.log(hp_tA_2) + alpha*(np.log(nuci_t) + np.log(base['K'])) + \
         (1 - alpha)*(np.log(LP_t) + np.log(h_1)) + np.log(base['ttrade'])
ln_tY_3 = np.log(hp_tA_3) + alpha*(np.log(nuci_t) + np.log(base['K'])) + \
         (1 - alpha)*(np.log(LP_t) + np.log(h_2)) + np.log(base['ttrade'])
ln_tY_4 = np.log(hp_tA_4) + alpha*(np.log(nuci_t) + np.log(base['K'])) + \
         (1 - alpha)*(np.log(LP_t) + np.log(h_3)) + np.log(base['ttrade'])
ln_tY_5 = np.log(hp_tA_5) + alpha*(np.log(nuci_t) + np.log(base['K'])) + \
         (1 - alpha)*(np.log(LP_t) + np.log(h_4)) + np.log(base['ttrade'])

# Recupera Y
tY_1 = np.exp(ln_tY_1)
tY_2 = np.exp(ln_tY_2)
tY_3 = np.exp(ln_tY_3)
tY_4 = np.exp(ln_tY_4)
tY_5 = np.exp(ln_tY_5)

# Salva Dataframes
tA = pd.concat([hp_tA_1, hp_tA_2, hp_tA_3, hp_tA_4, hp_tA_5], axis=1)
tY = pd.concat([tY_1, tY_2, tY_3, tY_4, tY_5], axis=1)

# Salva output
shtt = wb.sheets['output_ttrade']

shtt.range('A1').value = tA
shtt.range('I1').value = tY



