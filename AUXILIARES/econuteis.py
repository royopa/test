
# PACOTES GERAIS
import pandas as pd
import sys  # Funcionalidades do sistema (incluindo caminhos)
import numpy as np
from statsmodels.tsa.stattools import adfuller

# PATHS DO SISTEMA
sys.path.append(r'Z:\Macroeconomia\databases\MCM')  # Para utilizar as funções
sys.path.append(r'F:\SISTDAD\MEMPGRP\BMORIER\python\lib')  # Para utilizar as
                                                           # funções
sys.path.append(r'C:\Program Files (x86)\WinX13')

# PACOTES DO R
from rpy2.robjects.packages import importr, data
from rpy2.robjects import r, pandas2ri, IntVector
import  rpy2.robjects as ro

stats = importr('stats')
base = importr('base')
utils = importr('utils')
#utils.install_packages('seasonal')  # Para instalar o pacote de dessaz
seasonal = importr('seasonal')

# PACOTES USER-MADE
from funcoes_data_mcm_mult import mcm_base  # Função que abre a planilha
import mUtil as uu


def deflate_df(df):
    """DEFLACIONA TODAS AS SÉRIES DE UM DATAFRAME (A PREÇOS DO ÚLTIMO
    MÊS DIVULGADO DE IPCA).
    UTILIZA A SÉRIE DE IPCA."""

    ipca = mcm_base([(257, 'IPCA (Var)')])[(257,
                       'IPCA (Var)')]['IPCA (Var)'][0].iloc[:, 0]
    # Série do IPCA desde 1996

    v = uu.rCont(ipca/100)
    deflator = np.exp(-(np.sum(v)-np.cumsum(v)))
    deflator = deflator/deflator[-1]
    # Tenho uma série de deflator do IPCA

    deflator = deflator.reindex(index = df.index)

    df = pd.DataFrame(df, index = df.index)

    df_out = df.copy()

    for series in df:
        df_out[series] = df_out[series].values / deflator.values

    return df_out


ro.r('''
     # Criando uma função do R:
     # Função será rseas(ts), terá como imput uma time series e vai cuspir
     # uma outra time series com o dado dessazonalizado.
     # Dessazonalização será PADRÃO: utilizará o carnaval, mas vai deixar
     # o modelo em aberto para o programa selecionar o melhor fit e retirar
     # outliers.
     # ATENÇÃO: É NECESSÁRIO QUE O IMPUT SEJA UMA TIME SERIES DO R (precisa
     # chamar uma transformação anterior do pandas para time series)

     # Função para dessazonalização mensal
     rseas = function(ts) {
             carnaval = 
                      read.delim("F:/DADOS/ASSET/MACROECONOMIA/DADOS/Atividade/Dessazonalizacao/X12/carnaval.txt",sep = "",
                                 header = FALSE)
                  seg = ts(carnaval$V3,start=1990,frequency = 12)
                  ter = ts(carnaval$V4,start=1990,frequency = 12)
                  qua = ts(carnaval$V5,start=1990,frequency = 12)
                  qui = ts(carnaval$V6,start=1990,frequency = 12)
                  sex = ts(carnaval$V7,start=1990,frequency = 12)
                  sab = ts(carnaval$V8,start=1990,frequency = 12)
            # Pega o arquivo de carnaval

            ts_sa = seas(ts, regression.aictest = NULL,
                 xreg = cbind(seg,ter,qua,qui,sex,sab),
                 regression.usertype = "td")$data[,"seasonaladj"]
            return(ts_sa)

     }
     # Função para dessazonalização trimestral (não tem carnaval)
     rseas_q = function(ts) {
            ts_sa = seas(ts, regression.aictest = NULL,
                 regression.usertype = "td")$data[,"seasonaladj"]
            return(ts_sa)
     }'''
     )

rseas = ro.r['rseas']  # Definindo o objeto (função) de dessaz do R
rseas_q = ro.r['rseas_q']

def freq_df(df):
    """FUNÇÃO QUE INFERE A FREQUENCIA DE UM DATAFRAME DE FORMA MAIS SIMPLIFICADA
    QUE pd.infer_freq. DATAFRAME TEM QUE SER MINIMAMENTE PADRÃO, E O INDICE
    TEM QUE ESTAR NO FORMATO DE DATAS DO PANDAS.
    DATAFRAME TAMBÉM PRECISA TER NO MÍNIMO 2 ENTRADAS"""
    # https://stackoverflow.com/questions/35339139/where-is-the-documentation-on-pandas-freq-tags
    idx = pd.to_datetime(df.index, format='%Y %m %d')

    dt_1 = idx[0]  # Primeira data
    dt_2 = idx[1]  # Segunda data

    if dt_2.month - dt_1.month == 1 or dt_2.month - dt_1.month == -11:
        freq = 'M' #mensal
    elif dt_2.month - dt_1.month == 3 or dt_2.month - dt_1.month == -9:
        freq = 'Q' #trimestral
    elif dt_2.month - dt_1.month == 12:
        freq = 'A' #anual
    else:
        freq = 'unidentified'

    return freq


def series_to_ts(pd_ts):
    """FUNÇÃO QUE CONVERTE UMA PANDAS TIMESERIES (pd_ts) PARA UMA R TIMESERIES
    (r_ts)
    SÓ FUNCIONA COM SÉRIES MENSAIS, TRIMESTRAIS OU ANUAIS (por enquanto)."""

    r_start = ro.IntVector((pd_ts.index[0].year, pd_ts.index[0].month))

    if freq_df(pd_ts) == 'M':
        freq = 12
    elif freq_df(pd_ts) == 'Q':
        freq = 4
    elif freq_df(pd_ts) == 'A':
        freq = 1

    r_ts = stats.ts(ro.FloatVector(pd_ts.values), start=r_start,
                    frequency=freq)  # Constrói a time series
    return r_ts


def dessaz_df(df):
    """DESSAZONALIZA AS SÉRIES DE UM DATAFRAME DE DADOS MENSAIS.
    A DESSAZONALIZAÇÃO FEITA AQUI É PADRÃO, USA O CALENDÁRIO DE CARNAVAL
    E DEIXA ABERTO O MODELO ARIMA (SELEÇÃO AUTOMÁTICA)."""

    df = pd.DataFrame(df, index=df.index)  # Cria um dataframe para o caso
    # particular em que o imput é uma série única

    df_out = df.copy()

    if freq_df(df) == 'M':
        for series in df:
            py_series = df[series]
            idx = df.index[py_series.notna()]
            tseries = series_to_ts(py_series)  # Converte a série para R timeseries
            tseries_sa = rseas(tseries)  # Dessazonaliza e retorna um R timeseries
            df_out[series][pd.notna(df_out[series])] = \
                           pd.DataFrame(pandas2ri.ri2py(tseries_sa),
                                         index=idx)[0]
            # Coloca a série dessazonalizada em um dataframe de mesmo shape
    elif freq_df(df) == 'Q':
        for series in df:
            py_series = df[series]
            idx = df.index[py_series.notna()]
            tseries = series_to_ts(py_series)  # Converte a série para R timeseries
            tseries_sa = rseas_q(tseries)  # Dessazonaliza e retorna um R timeseries
            df_out[series][pd.notna(df_out[series])] = \
                           pd.DataFrame(pandas2ri.ri2py(tseries_sa),
                                         index=idx)[0]
            # Coloca a série dessazonalizada em um dataframe de mesmo shape

    return df_out


def name_df(df, string):
    """FUNÇÃO QUE ANEXA UM STRING NO NOME DAS COLUNAS DE UM DF"""

    df_out = df.copy()
    names = df.columns
    n_names = []

    for i in range(len(names)):
        n_names.append(string + names[i])

    df_out.columns = n_names

    return df_out


def adf_test(df, significance=0.05):
    """FUNÇÃO QUE APLICA O TESTE DE RAIZ UNITÁRIA ADF EM UM DATAFRAME.
    IMPUT: 
        df - dataframe ou serie (pandas)
        significance (optional) - nível de significância utilizado no teste
    OUTPUT:
        results - lista resultado (bool). 
    ATENÇÃO: Resultado do teste é um boleean onde True significa que a série
    É ESTACIONÁRIA, False que não pode ser determinada pelo teste."""
    
    df = pd.DataFrame(df, index=df.index)  # Cria um dataframe para o caso
    # particular em que o imput é uma série única
    
    results = list()
    
    for series in df:
        adf = adfuller(df[series].dropna())
        if adf[1] < significance:
            tres = True
        else:
            tres = False
        results.append(tres)
    
    return results






