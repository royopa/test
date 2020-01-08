import pandas as pd  # leitura (em excel) e analise de dados
import sys           # Funcionalidades do sistema (incluindo caminhos)
#sys.path.append(r'Z:\Macroeconomia\codes')  # Para utilizar as funÃ§Ãµes
#sys.path.append(r'Z:\Macroeconomia\databases')
#sys.path.append(r'F:\SISTDAD\MEMPGRP\BMORIER\python\lib')
#sys.path.append(r'Z:\Macroeconomia\codes\Projetos\MLEco')
from mDataStore.globalMongo import mds
from mongo_load import mongo_load, check_freq, numerate_freq, transform_series
from datetime import timedelta
import mDataStore.freqHelper as f
import swifter #o python acusa arreoneamente que o pacote nao esta sendo utilizado

class S_clean_db:
    ''' Objetivo: filtro inicial da variavel a ser explicada de interesse,
    inputada como mongo series.
    '''
    def __init__(self, target):
        # input: mongo series que possui um atributo metadado (md)
        self.y_md = target.md
        self.y_freq = target.md['freq_']
        if check_freq(self.y_freq):
            # checa se a frequencia dos dados NAO está adequada
            return
        elif numerate_freq(self.y_freq) == 0:
            # verifica se a frequencia dos dados esta diaria
            self.y_data = pd.Series(target)
            self.y_rel_date = None
        else:
            # se tudo esta corretamente especificado, seta a data de referencia e de release
            self.y_data = pd.Series(target.iloc[:, 0])
            self.y_rel_date = pd.Series(target.iloc[:, 1])
        self.y_transformation = None
        self.y_stDT = target.md['stDT_econVS']
        self.y_endDT = target.md['endDT_econVS']

    def transform_y(self, transform):
        # Aplica transformação em y, salva em y_transformation e ajusta as datas
        
        self.y_data = transform_series(df = self.y_data, transf = transform)
        self.y_rel_date = self.y_rel_date.align(self.y_data, join='inner')[0]
        self.y_transformation = transform
        self.y_stDT = self.y_data.index[0]
        self.y_endDT = self.y_data.index[-1]

    def get_db(self, transform='transform_y', check_real=True, check_seas=True,
               min_y_sample=0.8, mongo_list=None):
        # Coleta as variaveis da base de dados que atingem os criterios de
        # compatibilidade em relacao a variavel de interesse
        md = self.y_md

        if transform == 'transform_y':
            self.x_transformation = self.y_transformation

        if mongo_list is not None:
            # se a mongo list nao esta vazia, busca um conjunto especifico de variaveis
            data_df, rel_date_df = mongo_load(m_list=mongo_list, transform=self.x_transformation, freq=md['freq_'])
            self.x_df, self.x_rel_date = data_df, rel_date_df
            return
        
        # calcula o tamanho minimo das variaveis explicativas
        if md['freq_'] == f.monthBegin:
            min_sample = round(((self.y_endDT.year - self.y_stDT.year)*12 +
                        self.y_endDT.month - self.y_stDT.month)*min_y_sample)
        elif md['freq_'] == f.quarterBegin:
            min_sample = round(((self.y_endDT.year - self.y_stDT.year)*4 +
                        self.y_endDT.quarter - self.y_stDT.quarter)*min_y_sample)
            
        # calcula a data minima de inicio da serie desejada
        min_stDT = self.y_data.index[len(self.y_data) - min_sample]

        # lista com a busca de todas as séries
        m_list = mds.find(library=mds.econVS)
        series_ref = []

        for series_md in m_list:
            # coleta o metadado da serie
            #series_md = series[2]
            include = True

            # performa os checks
            if check_real:
                if series_md['currency'] == md['currency']:
                    if series_md['real'] != md['real']:
                        include = False
                        continue
            
            if check_seas:
                if series_md['seasonality'] != md['seasonality']:
                    include = False
                    continue
            
            if series_md['stDT_econVS'] > min_stDT: 
                include = False
                continue
            
            if series_md['endDT_econVS'] - self.y_endDT < timedelta(days=-1):
                include = False
                continue
            
            if include:
                series_ref.append(series_md)

        # faz o download da serie no mongo
        data_df, rel_date_df = mongo_load(m_list=series_ref, transform=self.x_transformation,
                                          freq=md['freq_'])

        self.x_df, self.x_rel_date = data_df, rel_date_df
        self.x_mongo_list = series_ref

    def make_lags(self, lags_y=1, lags_x=(0, 4)):
        # Expande a matriz X para incluir lags
        x = self.x_df.copy()
        y = self.y_data.copy()
        x_rel_date = self.x_rel_date.copy()
        y_rel_date = self.y_rel_date.copy()
        x_lags = x.copy()
        x_lags_rel_date = x_rel_date.copy()
        features = list(x.columns)

        if lags_y > 0:
            # Se inclui lag de y
            y_lags = {}
            y_rel_lags = {}
            
            for i in range(lags_y):
                y_l = y.shift(i+1)
                y_l.name = 'y_'+str(i+1)
                y_lags[y_l.name] = y_l
                y_rel_l = y_rel_date.shift(i+1)
                y_rel_l.name = 'y_'+str(i+1)
                y_rel_lags[y_rel_l.name] = y_rel_l

            y_lags = pd.DataFrame(y_lags)
            y_rel_lags = pd.DataFrame(y_rel_lags)
            x_lags = pd.concat([x_lags, y_lags], axis=1, join='outer')
            x_lags_rel_date = pd.concat([x_lags_rel_date, y_rel_lags], axis=1)

        for i in range(lags_x[0], lags_x[1]+1):
            # Cria os lags de X e anexa a matriz (inclusive ajustando as release dates)
            if i == 0:
                continue
            else:
                x_l = x.shift(i)
                rel_l = x_rel_date.shift(i)
                names_dic = dict(zip(features, [el+'_'+str(i) for el in features]))
                x_l = x_l.rename(columns=names_dic)
                rel_l = rel_l.rename(columns=names_dic)
                x_lags = pd.concat([x_lags, x_l], axis=1)
                x_lags_rel_date = pd.concat([x_lags_rel_date, rel_l], axis=1)

        if lags_x[0] != 0:
            # Se user definiu X sem contemporâneas, dropa as variáveis não lagged.
            x_lags = x_lags.drop(columns=features)
            x_lags_rel_date = x_lags_rel_date.drop(columns=features)

        self.x_df_l, self.x_rel_date_l = x_lags, x_lags_rel_date

    def check_rel_date(self, with_lags=True, new_output=False, update_mongo_list=True, delta_days=1):
        # Checa as release dates para incluir apenas séries divulgadas antes do target
        if with_lags:
            # Se a checagem deve ser feita na matriz com lags ou não
            x_adj_rel = self.x_rel_date_l.copy()
        else:
            x_adj_rel = self.x_rel_date.copy()
            
        for series in x_adj_rel:
            x_adj_rel[series] = x_adj_rel[series].swifter.apply(pd.to_datetime,
                                 **{'format': '%Y-%m-%d %H:%M:%S',
                                    'errors': 'coerce'})
        y_adj_rel = self.y_rel_date.swifter.apply(pd.to_datetime,
                                 **{'format': '%Y-%m-%d %H:%M:%S',
                                    'errors': 'coerce'})
        if isinstance(y_adj_rel, pd.core.frame.DataFrame):
            y_adj_rel = pd.Series(y_adj_rel.iloc[:, 0])
            
        x_adj_rel = x_adj_rel.align(y_adj_rel, axis=0, join='inner')[0]
        diff = x_adj_rel.sub(y_adj_rel, axis=0)
        max_d = pd.Series(index=diff.columns)

        for series in diff:
            max_d[series] = max(diff[series].dropna())

        self.to_include = max_d < timedelta(days=-int(delta_days))

        if new_output:
            # Se deve retornar matriz nova
            if with_lags:
                x_out = self.x_df_l.copy()
            else:
                x_out = self.x_df.copy()
            x_out = x_out.loc[:, self.to_include]
            return x_out
        else:
            # Do contrário, sobrescreve
            if with_lags:
                self.x_df_l = self.x_df_l.loc[:, self.to_include]
            else:
                self.x_df = self.x_df.loc[:, self.to_include]

        if update_mongo_list:
            # Atualiza a mongo_list apenas com os dados utilizados os elementos desta lista são mds.finds objects
            # que contém: (i) a library, (ii) o nome e (iii) o metadado da variável
            mongo_list = self.x_mongo_list.copy()
            # Coleta os nomes das variaveis
            series_names = [mongo_list[i]['name'] for i in range(len(mongo_list))]
            new_mongo_list = []
            for el in series_names:
                # Coleta um vetor com os nomes de variáveis (com e/ou sem lag) cujas contemporaneas estavam
                # no X_mongo_list inicial
                matching = [s for s in self.to_include.index if el in s]
                if True in self.to_include.loc[matching].values:
                    # Coleta apenas o indexador das variáveis contemporâneas que estavam no mongo_list e
                    # permaneceram nas variaveis a serem incluidas no filtro
                    indexer = [s for s in range(len(mongo_list)) if mongo_list[s]['name'] == el][0]
                    new_mongo_list.append(mongo_list[indexer])
            self.x_mongo_list = new_mongo_list
