import pandas as pd
import requests
import locale
import numpy as np
import xlwings as xw

locale.setlocale(locale.LC_ALL, '')
 
# cria uma função que lê o api e transforma em um dataframe
def getsidra(api, proxies):
    response = requests.get(api, proxies=proxies)
    x = response.json()
    df = pd.DataFrame.from_dict(x)
    return df

def aggregate_ipcas(list_dfs, dia, proxies):
    ipca00 = pd.DataFrame([])
    for cod in list_dfs:
        ipca = getsidra(cod, proxies)
        ipca = ipca.drop(ipca.index[[0]])
        ipca.columns = ['Local (Código)','Local','Variável (Código)','Variável',
                        'Mês (Código)','Mês','Classe (Código)','Classe',
                        'Unidade (Código)','Unidade','Regiao (Código)',
                        'Região','Valor']
        ipca['Mês'] = dia + " " + ipca['Classe']
        ipca['Unidade'][ipca['Unidade'] == 'Índice geral'] = '0.Índice Geral'
        cods = ipca['Unidade'].str.split('.', expand=True)
        ipca['Classe (Código)'] = cods.iloc[:,0]
        ipca00 = pd.concat([ipca00, ipca])
    return ipca00

def limpa_ipca(ipca):
    ipca['Mês'] = pd.to_datetime(ipca['Mês'], format='%d %B %Y')
    ipca['Mês'] = ipca['Mês'].apply(lambda x: x.strftime('%Y-%m-%d'))
    ipca['Valor'] = ipca['Valor'].apply(lambda y: np.nan if y == "..." else y)
    ipca['Valor'] = ipca['Valor'].apply(lambda y: np.nan if y == "-" else y)
    ipca['Valor'] = ipca['Valor'].astype(float)
    ipca = ipca.set_index('Classe (Código)')
    ipca = ipca[['Mês', 'Valor']]
    #new = ipca['Unidade'].str.split(".", n = 1, expand = True) 
    #new = new.iloc[:,0]
    #new[new == 'Índice geral'] = 0
    #ipca['Unidade'] = new
    return ipca

if __name__ == '__main__':
    proxies = {"http": "http://marcgut:Outubro2019@webproxy:8080",
               "https": "https://marcgut:Outubro2019@webproxy:8080"}
    
    # lista de apis do ipca
    list_vars00 = ['http://api.sidra.ibge.gov.br/values/t/1419/n1/all/v/63/p/all/c315/all/f/a',  # ipca, 2012 -
                   'http://api.sidra.ibge.gov.br/values/t/2938/n1/all/v/63/p/all/c315/all/f/a',  # ipca, 2006 - 2012
                   'http://api.sidra.ibge.gov.br/values/t/655/n1/all/v/63/p/all/c315/all/f/a',   # ipca, 1999 - 2006 
                   'http://api.sidra.ibge.gov.br/values/t/58/n1/all/v/63/p/all/c72/all/f/a',    # ipca, 1991 - 1999
                   'http://api.sidra.ibge.gov.br/values/t/1692/n1/all/v/63/p/all/c72/all/f/a',
                   'http://api.sidra.ibge.gov.br/values/t/7060/n1/all/v/63/p/last/c315/all/f/a']  # ipca, 1989 - 1991     
    
    list_vars15 = ['http://api.sidra.ibge.gov.br/values/t/1705/n1/all/v/355/p/all/c315/all/f/a', # ipca15, 2012 - 
                   'http://api.sidra.ibge.gov.br/values/t/1387/n1/all/v/355/p/all/c315/all/f/a', # ipca15, 2006 - 2012
                   'http://api.sidra.ibge.gov.br/values/t/1646/n1/all/v/355/p/all/c315/all/f/a'] # ipca15, 1999 - 2006
    
    list_peso00 = ['http://api.sidra.ibge.gov.br/values/t/1419/n1/all/v/66/p/all/c315/all/f/a',  # ipca, 2012 -
                   'http://api.sidra.ibge.gov.br/values/t/2938/n1/all/v/66/p/all/c315/all/f/a',  # ipca, 2006 - 2012
                   'http://api.sidra.ibge.gov.br/values/t/656/n1/all/v/66/p/all/c315/all/f/a',   # ipca, 1999 - 2006 
                   'http://api.sidra.ibge.gov.br/values/t/61/n1/all/v/66/p/all/c72/all/f/a',    # ipca, 1991 - 1999
                   'http://api.sidra.ibge.gov.br/values/t/1693/n1/all/v/66/p/all/c72/all/f/a',
                   'http://api.sidra.ibge.gov.br/values/t/7060/n1/all/v/66/p/last/c315/all/f/a']  # ipca, 1989 - 1991
    
    list_peso15 = ['http://api.sidra.ibge.gov.br/values/t/1705/n1/all/v/357/p/all/c315/all/f/a', # ipca15, 2012 - 
                   'http://api.sidra.ibge.gov.br/values/t/1387/n1/all/v/357/p/all/c315/all/f/a', # ipca15, 2006 - 2012
                   'http://api.sidra.ibge.gov.br/values/t/1646/n1/all/v/357/p/all/c315/all/f/a'] # ipca15, 1999 - 2006

    ipca00_var  = aggregate_ipcas(list_vars00, "28", proxies)
    ipca15_var  = aggregate_ipcas(list_vars15, "15", proxies)
    ipca00_peso = aggregate_ipcas(list_peso00, "28", proxies)
    ipca15_peso = aggregate_ipcas(list_peso15, "15", proxies)
    
    # concatenando dados de variacao e peso do IPCA
    ipca_var  = limpa_ipca(pd.concat([ipca00_var, ipca15_var], ignore_index=True))
    ipca_peso = limpa_ipca(pd.concat([ipca00_peso,ipca15_peso],ignore_index=True))
    
    # setar um multi index no pd.dataframe e aplicar o unstack
    ipca_var = ipca_var.set_index(['Classe (Código)', 'Mês'])
    ipca_var = ipca_var['Valor'].unstack()
    
    ipca_peso = ipca_peso.set_index(['Classe (Código)', 'Mês'])
    ipca_peso = ipca_peso['Valor'].unstack()
    
    #salva no excel
    file_var = 'F:\\DADOS\\ASSET\\MACROECONOMIA\\DADOS\\Inflação\\1.IPCA\\bases\\IPCA_base_var.xlsx'
    file_peso = 'F:\\DADOS\\ASSET\\MACROECONOMIA\\DADOS\\Inflação\\1.IPCA\\bases\\IPCA_base_peso.xlsx'

    #atualiza excel
    wb_var  = xw.Book(file_var)
    sht_var = wb_var.sheets('var')
    sht_var.range('A1').value = ipca_var
    
    wb_peso = xw.Book(file_peso)
    sht_peso = wb_peso.sheets('peso')
    sht_peso.range('A1').value = ipca_peso

    
    
    