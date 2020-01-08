"""
Author:      pietcon
Last Update: 20/05/19

Goal: a funcao deste programa é extrair uma series de dados da base do SIDRA
e formata-la de maneira a ficvar pronta para uso
"""

import pandas as pd
import requests
import locale
import numpy as np
 
locale.setlocale(locale.LC_ALL, '')
 
proxies = {
  "http": "http://pietcon:Safrajun19@webproxy:8080",
  "https": "https://pietcon:Safrajun19@webproxy:8080",
}


def series_ibge(api_cod, class_name):
    """FUNÇÃO PRINCIPAL:
    INPUT: uma lista de APIs que correspondem a TABELAS da Sidra,
    conforme as instruções em http://api.sidra.ibge.gov.br/
    OUTPUT: um dataframe com todas as informações requeridas"""
    ibge = limpa_ibge(format_ibges(api_cod, class_name))
    ibge = ibge.set_index(['Classe', 'Mês'])
    ibge = ibge['Valor'].unstack()
    return ibge


def getsidra(api):
    """FUNÇÃO: extrai dados da Sidra
    INPUT: um API da Sidra
    OUTPUT: dados extraídos em forma de lista"""
    response = requests.get(api, proxies=proxies)
    x = response.json()
    df = pd.DataFrame.from_dict(x)
    return df


def format_ibges(api_cod, class_name, dia = '01'):
    """FUNÇÃO: agregada dados extraídos da Sidra
    INPUT: dados obtidos da função getsidra
    OUTPUT: agrega e formata os dados extraídos do Sidra, 
    porém mantém em formato de lista"""    
    ibge = getsidra(api_cod)
    ibge = ibge.drop(ibge.index[[0]])
    ibge.columns = ['Local (Código)','Local','Variável (Código)','Variável',
                    'Mês (Código)','Mês','Unidade (Código)','Unidade','Valor']
    ibge['Mês'] = dia + " " + ibge['Mês']
    ibge['Classe (Código)'] = 300000
    ibge['Classe'] = class_name
    ibge = ibge[['Local (Código)','Local','Variável (Código)','Variável',
                 'Mês (Código)','Mês','Classe (Código)', 'Classe',
                 'Unidade (Código)','Unidade','Valor']]


def limpa_ibge(ibge):
    """FUNÇÃO: limpa dados agregados extraídos da Sidra
    INPUT: dados agregados em forma de lista
    OUTPUT: limpa e formata os dados para serem transformados em um data.frame"""  
    ibge['Mês'] = pd.to_datetime(ibge['Mês'], format='%d %B %Y')
    ibge['Mês'] = ibge['Mês'].apply(lambda x: x.strftime('%Y-%m-%d'))
    ibge['Valor'] = ibge['Valor'].apply(lambda y: np.nan if y == "..." else y)
    ibge['Valor'] = ibge['Valor'].apply(lambda y: np.nan if y == "-" else y)
    ibge['Valor'] = ibge['Valor'].astype(float)
    ibge = ibge[['Classe', 'Mês', 'Valor']]
    return ibge



