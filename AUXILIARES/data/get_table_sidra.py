"""
Author:      pietcon
Last Update: 20/05/19

Goal: a funcao deste programa é extrair uma tabela de dados da base do SIDRA
e formata-la de maneira a ficvar pronta para uso
"""

import pandas as pd
import requests
import locale
import numpy as np
 
locale.setlocale(locale.LC_ALL, '')
 
proxies = {
  "http": "http://pietcon:Saframai19@webproxy:8080",
  "https": "https://pietcon:Saframai19@webproxy:8080",
}


def table_ibge(list_apis):
    """FUNÇÃO PRINCIPAL:
    INPUT: uma lista de APIs que correspondem a TABELAS da Sidra,
    conforme as instruções em http://api.sidra.ibge.gov.br/
    OUTPUT: um dataframe com todas as informações requeridas"""
    ibge = limpa_ibge(aggregate_ibges(list_apis))
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


def aggregate_ibges(list_dfs, dia = '01'):
    """FUNÇÃO: agregada dados extraídos da Sidra
    INPUT: dados obtidos da função getsidra
    OUTPUT: agrega e formata os dados extraídos do Sidra, 
    porém mantém em formato de lista"""    
    ibge00 = pd.DataFrame([])
    for cod in list_dfs:
        ibge = getsidra(cod)
        ibge = ibge.drop(ibge.index[[0]])
        ibge.columns = ['Local (Código)','Local','Variável (Código)','Variável',
                        'Mês (Código)','Mês','Classe (Código)', 'Classe',
                        'Unidade (Código)','Unidade','Valor']
        ibge['Mês'] = dia + " " + ibge['Mês']
        ibge00 = pd.concat([ibge00, ibge])
    return ibge00


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



