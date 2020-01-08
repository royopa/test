import pandas as pd
import numpy as np
import sys           # Funcionalidades do sistema (incluindo caminhos)
sys.path.append(r'Z:\Macroeconomia\codes')  # Para utilizar as funÃ§Ãµes
sys.path.append(r'Z:\Macroeconomia\databases')
sys.path.append(r'F:\SISTDAD\MEMPGRP\BMORIER\python\lib')
sys.path.append(r'Z:\Macroeconomia\codes\Projetos\MLEco')
from sklearn.feature_selection import SelectKBest, f_regression, mutual_info_regression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


class S_univariate_selection:
    ''' Objetivo: selecionar as melhores variaveis a serem utilizadas na 
    projecao da variavel y de interesse com base em uma escolha univariada
    '''    
    def __init__(self, y, x, min_est_prop=.8):
        x = x.dropna(axis=0, how='any')
        y = y.align(x, axis=0, join='inner')[0]
        self.y = y.copy()
        self.x = x.copy()
        self.x_select = None
        self.selected_list = []
        self.selected_dict = {}
        self.min_est_size = int(len(y)*min_est_prop)

    def select(self, k=None, prop=.8, method='mutual_info_regression'):
        # Seleciona k variáveis (k é uma proporcao do tamanho da amostra de y, 
        # pois k deve ser menor q n) ou um escalar
        y = self.y.copy()
        x = self.x.copy()
        min_size = self.min_est_size

        if k == None:
            k = min(round(len(y)*prop), len(x.columns))

        if method == 'f_regression':
            selector = make_pipeline(StandardScaler(), SelectKBest(f_regression, k))
        elif method == 'mutual_info_regression':
            selector = make_pipeline(StandardScaler(), SelectKBest(mutual_info_regression, k))

        selector.fit_transform(x.iloc[:min_size, :], y.iloc[:min_size])
        mask = selector.steps[1][1].get_support()

        ###########
        # Gerando um threshold para o n.o de variáveis através de um score mínimo normalizado
        #scores = selector.steps[1][1].scores_
        #scores[np.isnan(scores)] = 0
        #scores = (scores - np.mean(scores))/np.std(scores)
        #sort = np.sort(scores)
        #diff = np.diff(sort)
        #window = 10
        #mave = np.zeros(len(diff) - window)

        #for i in range(len(mave)):
        #    mave[i] = sum(diff[i:i+window]) / window
            
        #threshold = np.argwhere(mave > .005)[0]
        #if threshold > k:
        #    mask = scores > sort[threshold]
        ###########
        
        self.selected_list = list(x.columns.values[mask])
        self.x_select = pd.DataFrame(self.x, index=self.x.index, columns=self.selected_list)

        # Construindo um dicionário com as variáveis e os lags selecionados
        look_for_variables = self.selected_list    
        while len(look_for_variables) != 0:
            var = look_for_variables[0]
            lagged = []
            try:
                int(var[-1])
                var = var[:-2]
            except ValueError:
                lagged = [0]
                pass

            ids = lagged + [s for s in range(len(look_for_variables)) if var == look_for_variables[s][:-2]]
            vars = [look_for_variables[s] for s in ids]
            look_for_variables = [look_for_variables[s] for s in range(len(look_for_variables)) if s not in ids]

            try:
                lags = [int(s[-1]) for s in vars]
            except ValueError:
                lags = [0] + [int(s[-1]) for s in vars[1:]]

            self.selected_dict[var] = lags
