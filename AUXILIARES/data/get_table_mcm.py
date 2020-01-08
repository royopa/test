"""
Author:      pietcon
Last Update: 17/04/19

Goal: a funcao deste programa é buscar na base de dados da MCM 
uma sheet (ou todas as sheets) de uma planilha codificada e entregar 
um data.frame com os dados de maneira padrão
"""

import pandas as pd  # leitura (em excel) e análise de dados
import shelve        # acessar objetos em formato Python
import numpy as np   # operações matriciais


def mcm_base(alist):
    """FUNÇÃO PRINCIPAL:
        INPUT: uma lista com as informações desejadas a partir da base de dados da MCM.
        Padrões aceitáveis:
            [1] - lista com apenas o n.o de referência da planilha. 
            Retorna um dicionário contendo as sheets em forma de dfs e seus metadados
            [1,'sheet1',3] - lista cujos elementos são o n.o de referência da planilha 
            da base da MCM e também as sheets desejadas referenciadas 
            por nome ou por posição.
            Retorna um dicionário contendo as sheets referenciadas
            em forma de dfs e seus metadados
        ATENÇÃO: O PRIMEIRO ITEM TEM QUE SER NÚMERO DA PLANILHA, 
        SEGUIDO DAS SHEETS (EM NOME OU NÚMERO)."""
    df_list = {}  # dicionário de dataframes (ref pelos nomes)
    plan_cod = alist[0]
    # abre o df com apenas o NOME das planilha padrão da MCM indexados 
    # pelo indice da MCM
    mcm_db = db['indice_mcm']['NOME']  # referências das planilhas
    plan = pd.read_excel(
            r'F:\DADOS\ASSET\MACROECONOMIA\DADOS\Base de Dados\MCM\{0}'
                .format(plan_cod),sheet_name=None)
    sheets = list(plan.keys())

    # Indicador se deseja uma planilha específica ou todas
    if len(alist) > 1: 
        for isheet in range(1, len(alist)):
            cod_sh = alist[isheet]
            # Adiciona ao df_list as sheets desejadas referenciadas pelo nome
            if isinstance(cod_sh, str): # caso o cod seja string
                df_list[cod_sh] = mcm_df(plan[cod_sh])
            else: # caso o cod seja numerico
                df_list[sheets[cod_sh]] = mcm_df(plan[sheets[cod_sh]])
    else:
        for isheet in range(len(plan)):
            df_list[sheets[isheet]] = mcm_df(plan[sheets[isheet]])
    return(df_list)
    
##############################################################################
##############################################################################
##############################################################################
# FUNÇÕES AUXILIARES

def mcm_plan(alist):
    """ FUNÇÃO: a partir de uma lista de números, abre planilhas da base da MCM 
    conforme os códigos no objeto python e preenche a lista com as planilhas 
    de base de dados (entram como dicionários, onde cada entrada é uma sheet)"""
    # objeto python convertido a partir da planilha da MCM com todos
    # os dados sobre a base de dados que baixada do excel
    # a base tem 3 objetos: indice_mcm, indice_bacen, indice_sidra   
    db = shelve.open(
        r'F:\DADOS\ASSET\MACROECONOMIA\DADOS\Base de Dados\PYTHON\indice')
    # abre o df com apenas o NOME das planilha padrão da MCM indexados 
    # pelo indice da MCM
    mcm_db = db['indice_mcm']['NOME']  # referências das planilhas
    list_plan = list()
    # cria uma lista com as planilhas baixadas a partir da base da MCM
    for iter in range(len(alist)):
        list_plan.append(pd.read_excel(
            r'F:\DADOS\ASSET\MACROECONOMIA\DADOS\Base de Dados\MCM\{0}'
                .format(mcm_db[alist[iter]]),sheet_name=None))
    return list_plan



def conc_str(series):
    """ FUNÇÃO: concatena uma serie de strings em um header único"""
    str_out = ''
    for i in range(len(series)):
        if type(series.iloc[i]) == str or type(series.iloc[i]) == int:
            str_out += '_' + str(series.iloc[i])
    return str_out



def mcm_df(df):
    """FUNÇÃO: testa se a planilha da MCM input é vertical ou horizontal e 
    chama a função que trabalha os dados orrespondente
    (mcm_df_vert ou mcm_df_hor)"""
    test = test_df_dir(df)
    if test == 'v':
        df_out = mcm_df_vert(df)
    else:
        df_out = mcm_df_hor(df)
    return(df_out)
 
    
    
def test_df_dir(df):
    """FUNÇÂO: tenta inferir se o data.frame em questão está distribuído
    de forma vertical (datas nas linhas, variáveis em colunas); horizontal
    (datas em colunas, variáveis em linhas) ou em formato de contas nacionais"""
    frame = 0
    # Testa se há datas nas primeiras colunas
    for col in range(0, 5): # Loop procura a coluna que tem as datas
        tstamp = df.iloc[:, col].apply(isinstance, args=[pd.Timestamp])
        dtime = df.iloc[:, col].apply(isinstance, args=[pd.datetime])
        if len(np.nonzero(tstamp)[0]) > 3 or len(np.nonzero(dtime)[0]) > 3:
            frame = 'v'  # a planilha é vertical
            break

    if frame == 0:
        for row in range(0, 10): # Loop procura a linha que tem as datas
            tstamp = df.iloc[row, :].apply(isinstance, args=[pd.Timestamp])
            dtime = df.iloc[row, :].apply(isinstance, args=[pd.datetime])
            if len(np.nonzero(tstamp)[0]) > 3 or len(np.nonzero(dtime)[0]) > 3:
                frame = 'h'  # a planilha é horizontal
                break

    if frame == 0:  # Se até aqui ainda não ficou definido, faço últimos testes
        # Se tem uma grande quantidade de colunas
        if len(list(df)) > 25:  frame = 'h'
        # Se tem uma quantidade grande de linhas
        elif len(df) > 100:     frame = 'v'
        # Se nenhuma das condições foi atingida, ele chuta que a planilha é vetical
        else:                   frame = 'v'  
    return(frame)



# FUNÇÕES QUE TRABALHAM OS DADOS DA MCM PARA UM DATAFRAME
def mcm_df_vert(df):
    """FUNÇÃO:
        INPUT:  uma sheet de planilha da MCM com padrão vertical (datas na primeira coluna) 
        OUTPUT: um dicionário contendo
            KEY - 'Nome da Planilha'_'Nome da Sheet'
            CONTEÚDO - data.frame com os dados e uma lista com os metadados
        ATENÇÃO: ESSA FUNÇÃO É DESENHADA PARA PLANILHAS COM DATA NA PRIMEIRA COLUNA"""
    df = df.dropna(how='all')
    df.index = range(len(df))

    # Loop procura a primeira entrada com data na coluna das datas
    for i, col in enumerate(df.columns):
        if (df[col].apply(isinstance,args=[pd.Timestamp]).any() or
                df[col].apply(isinstance,args=[pd.datetime]).any()):
            aux_date = df[col].copy()
            date_col = i
            break

    # Converte as entradas de aux_date para 1's onde tem as datas.
    for cell in range(len(df[col])):
        if isinstance(df[col][cell], (pd.datetime,pd.Timestamp)):
            aux_date.iloc[cell] = 1
        else:
            aux_date.iloc[cell] = 0

    axis_names = list()
    idx_dates = np.nonzero(aux_date)
    idx_first = idx_dates[0][0] 
    idx_last = idx_dates[0][-1]

    # Constroi os hearders do DF
    for i, col in enumerate(df.columns):  
        if i > date_col:  # Considera colunas a partir da segunda (exclui datas)
            for irow in range(idx_first):
                # Trata os merges do excel: as celulas com merge são lidas como zeradas
                if type(df[col][irow]) != str:
                    if (df[col][irow:idx_first].apply(isinstance,
                            args=[str]).isin([True]).any()):
                        df.iloc[irow, i] = df.iloc[irow, i - 1]
            # Concatena as strings para criar os headers
            axis_names.append(conc_str(df[col][0:idx_first]))

    # Cria o DF com os dados em data e força os dados para números
    df_out = df.iloc[aux_date.nonzero()[0], 1:]
    df_out.index = df.iloc[aux_date.nonzero()[0], 0]
    df_out.columns = axis_names
    df_out = df_out.apply(pd.to_numeric,args=('coerce',))

    meta_list = list()
    # Coleta dos metadados
    for irow in range(idx_last, len(df)):
        iter_cell = df.iloc[irow, 0]
        if ('Nome da Série' in str(iter_cell) or
                'Nome da Serie' in str(iter_cell)):
            meta_list.append(iter_cell.strip())
        elif 'Fonte' in str(iter_cell):
            meta_list.append(iter_cell.strip())
        elif 'Próxima' in str(iter_cell) or 'Proxima' in str(iter_cell):
            meta_list.append(iter_cell.strip())
        elif 'Dados' in str(iter_cell):
            meta_list.append(iter_cell.strip())
        elif 'Última' in str(iter_cell) or 'Ultima' in str(iter_cell):
            meta_list.append(iter_cell.strip())
        elif 'Ticker' in str(iter_cell) or 'ticker' in str(iter_cell):
            meta_list.append(iter_cell.strip())

    out_plan = [df_out, meta_list]
    return out_plan



def mcm_df_hor(df):
    """FUNÇÃO:
        INPUT:  uma sheet de planilha da MCM com padrão horizontal (datas na primeira linha) 
        OUTPUT: um dicionário contendo
            KEY - 'Nome da Planilha'_'Nome da Sheet'
            CONTEÚDO - data.frame com os dados e uma lista com os metadados
        ATENÇÃO: ESSA FUNÇÃO É DESENHADA PARA PLANILHAS COM DATA NA PRIMEIRA COLUNA"""
    df = df.T    
    df = df.dropna(how='all', axis = 'columns')
    df = df.dropna(how='all')

    # Loop procura a coluna que tem as datas e o início dos metadados
    for i, col in enumerate(df.columns):  
        if (df[col].apply(isinstance,args=[pd.Timestamp]).any() or
               df[col].apply(isinstance,args=[pd.datetime]).any()):
            aux_date = df[col].copy()
            date_col = i
        if df[col].str.contains('Nome da Série').any():
            nul_col = i

    df_meta = df.iloc[:,nul_col:]  # metadados
    df = df.iloc[:,:nul_col]       # data.frame

    # Converte as entradas de aux_date para 1's onde tem as datas
    for cell in range(len(df.iloc[:, date_col])):
        if (isinstance(df.iloc[cell, date_col], pd.datetime) or
                isinstance(df.iloc[cell, date_col], pd.Timestamp)):
            aux_date.iloc[cell] = 1
        else:
            aux_date.iloc[cell] = 0

    axis_names = list()
    idx_dates = np.nonzero(aux_date)
    idx_first = idx_dates[0][0]

    # Constrói os hearders do DF
    for i, col in enumerate(df.columns):
        if i > date_col:  # Considera colunas a partir da segunda (exclui datas)
            for irow in range(idx_first):
                # Trata os merges do excel: as celulas com merge são lidas como zeradas
                if type(df[col][irow]) != str and \
                        type(df[col][irow]) != int:
                    if (df[col][irow:idx_first].apply(isinstance,args=[str]).any()):
                        df.iloc[irow, col] = df.iloc[irow, col - 1]
            # Concatena as strings para criar os headers
            axis_names.append(conc_str(df.iloc[0:idx_first, col]))

    # Cria o DF com os dados em data e força os para formato número
    df_out = df.iloc[aux_date.nonzero()[0], (date_col + 1):]
    df_out.index = df.iloc[aux_date.nonzero()[0], date_col]
    df_out.columns = axis_names
    df_out = df_out.apply(pd.to_numeric,args=('coerce',))

    meta_list = list()
    # Coleta dos metadados
    for col in range(len(list(df_meta))):
        iter_cell = df_meta.iloc[0, col]
        if ('Nome da Série' in str(iter_cell) or
                'Nome da Serie' in str(iter_cell)):
            meta_list.append(iter_cell.strip())
        elif 'Fonte' in str(iter_cell):
            meta_list.append(iter_cell.strip())
        elif 'Próxima' in str(iter_cell) or 'Proxima' in str(iter_cell):
            meta_list.append(iter_cell.strip())
        elif 'Dados' in str(iter_cell):
            meta_list.append(iter_cell.strip())
        elif 'Última' in str(iter_cell) or 'Ultima' in str(iter_cell):
            meta_list.append(iter_cell.strip())
        elif 'Ticker' in str(iter_cell) or 'ticker' in str(iter_cell):
            meta_list.append(iter_cell.strip())

    out_plan = [df_out, meta_list]
    return out_plan
