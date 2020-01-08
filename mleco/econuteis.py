# PACOTES GERAIS
import pandas as pd
import sys  # Funcionalidades do sistema (incluindo caminhos)
import numpy as np
from statsmodels.tsa.stattools import adfuller
import statsmodels.api as sm
from datetime import date, datetime
import xlwings as xw

# PATHS DO SISTEMA
sys.path.append(r'Z:\Macroeconomia\databases\MCM')  # Para utilizar as funções
sys.path.append(r'F:\SISTDAD\MEMPGRP\BMORIER\python\lib')  # Para utilizar as funções
sys.path.append(r'C:\Program Files (x86)\WinX13')
sys.path.append(r'Z:\Macroeconomia\databases')
sys.path.append(r'Z:\Macroeconomia\codes')

# PACOTES DO R
from rpy2.robjects.packages import importr, data
from rpy2.robjects import r, pandas2ri, IntVector
import rpy2.robjects as ro

stats = importr('stats')
base = importr('base')
utils = importr('utils')
#utils.install_packages('seasonal')  # Para instalar o pacote de dessaz
seasonal = importr('seasonal')

# PACOTES USER-MADE
import funcoes_data_mcm_mult as mcm  # Função que abre a planilha
import mUtil as uu
#from mDataStore.bloomberg.remote import rBLP
#from mongo_load import transform_series


def deflate_df(df):
    """DEFLACIONA TODAS AS SÉRIES DE UM DATAFRAME (A PREÇOS DO ÚLTIMO
    MÊS DIVULGADO DE IPCA).
    UTILIZA A SÉRIE DE IPCA."""

    ipca = mcm.mcm_base([(257, 'IPCA (Var)')])[(257,
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
    idx = df.index

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


class Armax:
    def __init__(self, y, order=(1, 0), exog=None, trend='c'):
        self.y = y
        self.order = order
        if isinstance(exog, pd.Series):
            exog = pd.DataFrame(exog, index=exog.index)
        self.exog = exog
        self.trend = trend

    def fit(self):
        self.result = sm.tsa.ARMA(self.y, order=self.order,
                                  exog=self.exog).fit(trend=self.trend)

    def predict(self, exog=None):
        if exog is None:
            self.predicted = self.result.predict()
        else:
            ots_sample = len(exog) - len(self.y)
            y_its = self.result.predict()
            y_predict = y_its.align(exog, join='outer', axis=0)[0]
            y_iter = self.y.copy()
            for i in range(ots_sample):
                if i == 0:
                    forc_aux = self.result.forecast(
                                exog=exog.iloc[len(y_its)])
                    indx = y_predict.index[len(y_its)]
                    y_iter.loc[indx] = forc_aux[0][0]
                else:
                    arma = sm.tsa.ARMA(y_iter, order=self.order,
                                       exog=exog.align(y_iter, join='inner',
                                                       axis=0)[0]
                                       ).fit(trend=self.trend)
                    forc_aux = arma.forecast(exog=exog.iloc[len(y_its)+i])
                    indx = y_predict.index[len(y_its)+i]
                    y_iter.loc[indx] = forc_aux[0][0]
            y_predict.iloc[-ots_sample:] = y_iter[-ots_sample:]
            self.predicted = y_predict


def fmt_releasedate(dfs):
    df_list = dfs.iloc[0, 0]
    date_time_series = []
    for el in df_list:
        date_time_series.append(pd.to_datetime(el, errors='coerce')[0])
    date_time_series = pd.Series(date_time_series).dropna()
    return date_time_series


def gen_rdate_month(df, rel_date, clear_fut=True):
    # Equilibrando as datas de release
    if clear_fut:
        rel_drop = rel_date[rel_date <= pd.Timestamp(date.today()).replace(hour=23, minute=59)]
    else:
        rel_drop = rel_date.copy()
    if not isinstance(rel_drop, pd.Series):
        rel_drop = pd.Series(rel_drop)
    rel_drop = rel_drop.reset_index(drop=True)
    rel_drop.name = 'rel_drop'
    idx = pd.Series(df.index)
    idx.name = 'idx'
    if len(rel_drop) >= len(idx):
        idx.index = rel_drop.index[-idx.shape[0]:]
        df_out = pd.concat([rel_drop, idx], axis=1, join='inner')
        df_out = df_out.set_index(df_out.columns[1])
    else:
        diff = len(idx) - len(rel_drop)
        for i in range(diff):
            date_dict = {}
            if rel_drop[-i].month == 1:
                date_dict['month'] = 12
            else:
                date_dict['month'] = rel_drop[-i].month - 1
            date_dict['day'] = rel_drop[-i].day
            date_dict['hour'] = rel_drop[-i].hour
            if date_dict['month'] == 12:
                date_dict['year'] = rel_drop[-i].year - 1
            else:
                date_dict['year'] = rel_drop[-i].year
            rel_drop[-(i+1)] = pd.to_datetime(pd.DataFrame(date_dict,
                                              index=[0]))[0]
        rel_drop = rel_drop.sort_index()
        rel_drop.index = rel_drop.reset_index().index
        rel_drop.name = 'rel_drop'
        df_out = pd.concat([rel_drop, idx], axis=1)
        df_out = df_out.set_index(df_out.columns[1])

    df_out = df_out.rename(columns={'rel_drop' : 'release_date'})
    return df_out


def fix_rel_seq(rel_date_raw):
    rel_date_raw.index = rel_date_raw.reset_index().index
    rel_date = []

    def diff_month(d1, d2):
        return (d1.year - d2.year)*12 + d1.month - d2.month

    for i in range(len(rel_date_raw)):
        if i == 0:
            pass
        elif i == rel_date_raw.index[-1]:
            rel_date.append(rel_date_raw[i])
        else:
            if rel_date_raw[i].month - rel_date_raw[i-1].month == 1 or \
               rel_date_raw[i].month - rel_date_raw[i-1].month == -11:
                rel_date.append(rel_date_raw[i])
            else:
                num_miss = diff_month(rel_date_raw[i], rel_date_raw[i-1]) - 1
                seq_dates = pd.date_range(start=rel_date_raw[i-1],
                                          end=rel_date_raw[i],
                                          periods=num_miss+2)
                seq_dates = seq_dates[1:]
                for k in seq_dates:
                    rel_date.append(k)
    rel_date = pd.Series(rel_date)
    return rel_date


def make_reldate(df_series, day):
    start = {}
    start['year'] = df_series.index[0].year
    start['month'] = df_series.index[0].month+1
    start['day'] = day
    start = pd.to_datetime(pd.DataFrame(start, index=[0]))[0]
    rel_date = []
    rel_date.append(start)
    for i in range(1, len(df_series)):
        rel_date.append(rel_date[i-1]+pd.DateOffset(months=1))
    rel_date = pd.Series(rel_date, index=df_series.index)
    rel_date.name = 'release_date'
    return rel_date






def month_mma(df):
    """Pega um df ou série e devolve um df com a média móvel mensal dos dados,
    usando o padrão de datas no índice. Feito para séries menores que mensal."""
    if isinstance(df, pd.Series):
        df = pd.DataFrame(df, index=df.index)

    start_date = datetime(df.index[0].year, df.index[0].month, 1)
    end_date = datetime(df.index[-1].year, df.index[-1].month, 1)

    idx = pd.date_range(start=start_date, end=end_date, freq='MS')
    mma_df = pd.DataFrame(index=idx)
    

    for i in range(len(idx)):
        month = idx[i].month
        year = idx[i].year
        df_m = df.loc[df.index.month==month, :]
        df_my = df_m.loc[df_m.index.year==year, :]
        mma_df.loc[idx[i], 0] = np.mean(df_my.iloc[:, 0])

    mma_df = mma_df.rename(columns={0 : df.columns[0]})
    return mma_df


def quarter_mma(df):
    """Pega um df ou série e devolve um df com a média móvel trimestral dos dados,
    usando o padrão de datas no índice. Feito para séries menores que mensal."""
    if isinstance(df, pd.Series):
        df = pd.DataFrame(df, index=df.index)

    q_begin = df.index[0].quarter
    q_end = df.index[-1].quarter

    if q_begin == 1:
        m_begin = 3
    elif q_begin == 2:
        m_begin = 6
    elif q_begin == 3:
        m_begin = 9
    else:
        m_begin = 12
    if q_end == 1:
        m_end = 3
    elif q_end == 2:
        m_end = 6
    elif q_end == 3:
        m_end = 9
    else:
        m_end = 12

    start_date = datetime(df.index[0].year, m_begin, 1)
    end_date = datetime(df.index[-1].year, m_end, 1)

    periods = int(((end_date.year - start_date.year)*12 + end_date.month - \
               start_date.month)/3)

    idx = []

    for i in range(periods):
        if i == 0:
            idx.append(start_date)
        elif i == periods-1:
            idx.append(end_date)
        else:
            date_i = idx[i-1]
            if date_i.month == 12:
                m_i = 3
                y_i = date_i.year + 1
            else:
                m_i = date_i.month + 3
                y_i = date_i.year
            idx.append(datetime(y_i, m_i, 1))

    mma_df = pd.DataFrame(index=idx)

    for i in range(len(idx)):
        month_3 = idx[i].month
        month_2 = month_3 - 1
        month_1 = month_2 - 1
        year = idx[i].year
        df_m = df.loc[(df.index.month==month_3) | (df.index.month==month_2) | 
                      (df.index.month==month_1), :]
        df_my = df_m.loc[df_m.index.year==year, :]
        mma_df.loc[idx[i], 0] = np.mean(df_my.iloc[:, 0])

    mma_df = mma_df.rename(columns={0 : df.columns[0]})

    return mma_df
    

def update_mongo_rout(table, ref=None, source=None, mcm=True, quit_=True):
    wb = xw.Book(r'F:\DADOS\ASSET\MACROECONOMIA\DADOS\Base de Dados\MONGO_ROUT.xlsm')
    sheet = wb.sheets('TABLES')
    row_ = 0
    for row in range(2, 100):
        if sheet.range(row, 1).value == table:
            row_ = row
            break
    if row_ == 0:
        # não encontrou a tabela (apenas na primeira vez que roda ou se foi apagada)
        # usa a última linha em branco
        row_ = sheet.range('A'+str(sheet.cells.last_cell.row)).end('up').row + 1
        sheet.range(row_,1).value = table
        sheet.range(row_,2).value = ref
        sheet.range(row_,3).value = source
        sheet.range(row_,4).value = mcm
        sheet.range(row_,5).value = date.today()
    else:
        # se a entrada da table já existe, basta salvar a data de update
        # (desconsidera os outros imputs, só são necessários na primeira vez)
        sheet.range(row_,5).value = date.today()

    wb.save(r'F:\DADOS\ASSET\MACROECONOMIA\DADOS\Base de Dados\MONGO_ROUT.xlsm')

    if quit_:
        wb.close()

    return
    

def add_label_df(df, label, prefix=True):
    """Adiciona um label ao nome de todas as colunas no dataframe. 
    Se prefix = True, o label é adicionado no prefixo do nome. Se for falso, 
    no sufixo."""
    names = list(df.columns)
    dic_ch = {}
    
    for el in names:
        if prefix:
            dic_ch[el] = label+el
        else:
            dic_ch[el] = el+label
        
    df_out = df.rename(columns=dic_ch)
    
    return df_out


def index_to_datetime(df, idx_format):
    """Transforma indices de strings em datetime de acordo com o formato."""
    old_idx = df.index
    new_idx = []
    for el in old_idx:
        if isinstance(el, str):
            new_idx.append(datetime.strptime(el, idx_format))
        else:
            new_idx.append(el)
    
    df_out = df.copy()
    df_out.index = new_idx

    return df_out


def get_fst_date_idx(df, as_loc=True):
    """Pega o primeiro valor do índice do DF que seja igual a um datetime.
    Caso as_loc = False, retorna a posição do índice (para utilização com iloc).
    SÓ FUNCIONA PARA TIMESTAMP."""
    idx = list(df.index)

    for i, el in enumerate(idx):
        if isinstance(el, pd._libs.tslibs.timestamps.Timestamp):
            if as_loc:
                return el
            else:
                return i
        elif isinstance(el, datetime):
            if not str(el) == 'NaT':
                if as_loc:
                    return el
                else:
                    return i            
            
    
def rename_duplicate_columns(df):
    """Renomeia as colunas."""
    
    cols=pd.Series(df.columns)

    for dup in cols[cols.duplicated()].unique(): 
        cols[cols[cols == dup].index.values.tolist()] = [dup + '_' + str(i) + 'type' if i != 0 else dup for i in range(sum(cols == dup))]

    # rename the columns with the cols list.
    df.columns=cols
    
    return df
    
 
    
    

