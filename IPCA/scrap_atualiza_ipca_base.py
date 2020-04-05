import sys
sys.path.append('F:\\DADOS\\ASSET\\MACROECONOMIA\\1PIETRO\\AUXILIARES')
from econuteis import dessaz_df
sys.path.append('F:\\DADOS\\ASSET\\MACROECONOMIA\\DADOS\\Inflação\\1.IPCA\\rotinas')
from scrap_ipca_base import aggregate_ipcas, limpa_ipca
from cods_nucs_ipca import get_cods
sys.path.append(r'Z:\Macroeconomia\codes')

import pandas as pd
import locale
import numpy as np
import xlwings as xw
import proxies as prox
from datetime import datetime
import time

path_data = 'F:\\DADOS\\ASSET\\MACROECONOMIA\\DADOS\\Inflação\\1.IPCA\\bases\\'
file_var  = path_data + 'IPCA_base_var.xlsx'
file_peso = path_data + 'IPCA_base_peso.xlsx'

#carrega base (RODAR ANTES DA ROTINA)
ipca_var_base = pd.read_excel(file_var,  index_col=0)
ipca_pes_base = pd.read_excel(file_peso, index_col=0)

locale.setlocale(locale.LC_ALL, '')
proxies = prox.pietro

####### ATUALIZA BASE DE IPCA
# lista de apis do ipca que captam os ultimos valores das series de IPCA e IPCA15
list_vars00 = ['http://api.sidra.ibge.gov.br/values/t/7060/n1/all/v/63/p/last/c315/all/f/a']  # ipca, 2012 -
list_vars15 = ['http://api.sidra.ibge.gov.br/values/t/7062/n1/all/v/355/p/last/c315/all/f/a'] # ipca15, 2012 - 
list_peso00 = ['http://api.sidra.ibge.gov.br/values/t/7060/n1/all/v/66/p/last/c315/all/f/a']  # ipca, 2012 -
list_peso15 = ['http://api.sidra.ibge.gov.br/values/t/7062/n1/all/v/357/p/last/c315/all/f/a'] # ipca15, 2012 - 

ipca00_var = aggregate_ipcas(list_vars00, "28", proxies)
ipca15_var = aggregate_ipcas(list_vars15, "15", proxies)
ipca00_pes = aggregate_ipcas(list_peso00, "28", proxies)
ipca15_pes = aggregate_ipcas(list_peso15, "15", proxies)

# concatenando dados de variacao e peso do IPCA
ipca_var = limpa_ipca(pd.concat([ipca00_var, ipca15_var], ignore_index=True))
ipca_pes = limpa_ipca(pd.concat([ipca00_pes, ipca15_pes], ignore_index=True))

# setar um multi index no pd.dataframe e aplicar o unstack
#ipca_var = ipca_var.set_index(['Mês'])
#ipca_var = ipca_var['Valor'].unstack()
#ipca_var.index = list(map(int, ipca_var.index))

#ipca_pes = ipca_pes.set_index(['Mês'])
#ipca_pes = ipca_pes['Valor'].unstack()
#ipca_pes.index = list(map(int, ipca_pes.index))

loc = ipca_var.index.get_loc('0')
loc = np.argwhere(loc == True)[1][0]

ipca_var0 = pd.concat([ipca_var.iloc[:loc], ipca_var.iloc[loc:]], axis=1, sort=False).loc[:,'Valor']
ipca_var0.columns = ipca_var['Mês'].drop_duplicates()


ipca_pes0 = pd.concat([ipca_pes.iloc[:loc], ipca_pes.iloc[loc:]], axis=1, sort=False).loc[:,'Valor']
ipca_pes0.columns = ipca_var['Mês'].drop_duplicates()

ipca_pes = ipca_pes0.copy()
ipca_var = ipca_var0.copy()

ipca_var.columns = pd.to_datetime(ipca_var.columns) 
ipca_pes.columns = pd.to_datetime(ipca_pes.columns) 

# selecionando as colunas que não são repetidas
ord_atualiza = [x for x in ipca_var.columns if x not in ipca_var_base.columns]

# atualizando base com a nova informação

ipca_var.index = np.int64(ipca_var.index)
ipca_pes.index = np.int64(ipca_pes.index)

ipca_var_base = pd.concat([ipca_var_base, ipca_var[ord_atualiza]], axis=1, sort=False)
ipca_pes_base = pd.concat([ipca_pes_base, ipca_pes[ord_atualiza]], axis=1, sort=False)

####### CALCULO DOS NUCLEOS

# coletando um subgrupo da base de IPCA para calcular os nucleos dessazonalizados
aux_col = [str(i) for i in ipca_var_base.columns]
init = [i for i in range(len(aux_col)) if aux_col[i] == '2001-01-15 00:00:00'][0]
ipca_var_nuc = ipca_var_base.iloc[:, init:]
ipca_pes_nuc = ipca_pes_base.iloc[:, init:]

# coletando os indexes da base de dados para criar vetores booleanos para os nucleos
cods = [int(x[0]) for x in np.char.split(ipca_var_nuc.index.values.astype('str'),'.')]

# agrupando os itens que sao incluidos em cada grupo
index_servsub      = [cods.index(x) for x in get_cods(nuc='cods_nuc_serv_bc')]
index_servsub_exal = [cods.index(x) for x in get_cods(nuc='cods_nuc_servexal_bc')]
index_indusub      = [cods.index(x) for x in get_cods(nuc='cods_nuc_indu_bc')]
index_alimsub      = [cods.index(x) for x in get_cods(nuc='cods_nuc_alim_bc')]
index_admisub      = [cods.index(x) for x in get_cods(nuc='cods_nuc_admi_bc')]
index_livres       = [cods.index(x) for x in list(set(get_cods(nuc='difusao')) - set(index_admisub))]

index_ex2      = [cods.index(x) for x in get_cods(nuc='cods_nuc_bc_ex2')]
index_ex3      = [cods.index(x) for x in get_cods(nuc='cods_nuc_bc_ex3')]

index_ndur     = [cods.index(x) for x in get_cods(nuc='cods_non_dur')]
index_sdur     = [cods.index(x) for x in get_cods(nuc='cods_semi_dur')]
index_dur      = [cods.index(x) for x in get_cods(nuc='cods_dur')]

index_trad     = [cods.index(x) for x in get_cods(nuc='cods_trad')]
index_ntrad    = [cods.index(x) for x in get_cods(nuc='cods_non_trad')]

index_servtrab = [cods.index(x) for x in get_cods(nuc='cods_serv_int_trab')]
index_servtot  = [cods.index(x) for x in get_cods(nuc='cods_serv_tot')]
index_servdiv  = [cods.index(x) for x in get_cods(nuc='cods_serv_div')]

list_cods = [index_servsub,  index_servsub_exal, index_indusub, index_alimsub, 
             index_admisub,  index_livres,       index_ex2,     index_ex3, 
             index_ndur, index_sdur, index_dur, index_trad, index_ntrad, 
             index_servtrab, index_servtot, index_servdiv]

# dados trabalhados para os gráficos
out_data = {}
list_keys = ['servicos_sub', 'servicos_sub_exal', 'industriais_sub', 'alimentacao_sub', 
             'administrados_sub', 'livres', 'nucleo_ex2', 'nucleo_ex3',
             'nao_duraveis', 'semi_duraveis', 'duraveis',
             'tradables', 'non_tradables',
             'servicos_trabalho', 'servicos_totais', 'servicos_diversos', 
             'difusao']

for i, cods_nuc in enumerate(list_cods):
    pnuc = ipca_pes_nuc.iloc[cods_nuc]/(ipca_pes_nuc.iloc[cods_nuc].sum(axis=0, skipna=True))
    nuc = (ipca_var_nuc.iloc[cods_nuc]*pnuc).sum(axis=0, skipna=True)
    nuc.index = pd.to_datetime(nuc.index, format = '%Y-%m-%d')

    #MoM e MoM dessaz.
    nuc15 = nuc[0::2]; nuc15_dsz = dessaz_df(nuc15)
    #MoM acumulado 12 meses
    nuc15_12       = nuc15.rolling(12).apply(lambda x: (np.prod(1 + x/100) - 1)*100, raw=True)
    nuc15_12_dsz   = nuc15_dsz.rolling(12).apply(lambda x: (np.prod(1 + x/100) - 1)*100, raw=True)
    #MM3M do MoM
    nuc15_mm3m     = nuc15.rolling(3).apply(lambda x: np.average(x), raw=True)
    nuc15_mm3m_dsz = nuc15_dsz.rolling(3).apply(lambda x: np.average(x), raw=True)

    nuc30 = nuc[1::2]; nuc30_dsz = dessaz_df(nuc30)
    nuc30_12       = nuc30.rolling(12).apply(lambda x: (np.prod(1 + x/100) - 1)*100, raw=True)
    nuc30_12_dsz   = nuc30_dsz.rolling(12).apply(lambda x: (np.prod(1 + x/100) - 1)*100, raw=True)
    nuc30_mm3m     = nuc30.rolling(3).apply(lambda x: np.average(x), raw=True)
    nuc30_mm3m_dsz = nuc30_dsz.rolling(3).apply(lambda x: np.average(x), raw=True)

    nuc_dsz        = pd.concat([nuc15_dsz,      nuc30_dsz],     axis=0).sort_index(ascending=1)
    nuc_12         = pd.concat([nuc15_12,       nuc30_12],      axis=0).sort_index(ascending=1)
    nuc_12_dsz     = pd.concat([nuc15_12_dsz,   nuc30_12_dsz],  axis=0).sort_index(ascending=1)
    nuc_mm3m       = pd.concat([nuc15_mm3m,     nuc30_mm3m],    axis=0).sort_index(ascending=1)
    nuc_mm3m_dsz   = pd.concat([nuc15_mm3m_dsz, nuc30_mm3m_dsz],axis=0).sort_index(ascending=1)
    
    pcore = ipca_pes_nuc.iloc[cods_nuc].sum(axis=0, skipna=True)
    table = pd.concat([pcore, nuc, nuc_dsz, nuc_12, nuc_12_dsz, nuc_mm3m, nuc_mm3m_dsz], axis = 1)
    table.columns = ['Peso','Nuc','Nuc_dsz','Ac12m','Ac12m_dsz','MM3m','MM3m_dsz']
    
    out_data[list_keys[i]] = table
    
    # Salvando dados de Serviços antes do resto dos núcleos
    if i <= 1:
        file_nuc = path_data + 'IPCA_base_nucleos_servicos_sub.xlsx'
        wb = xw.Book(file_nuc)
        sht = wb.sheets(list_keys[i])
        sht.range('A1').value = out_data[list_keys[i]]
        #writer = pd.ExcelWriter(file_nuc, engine='xlsxwriter', 
        #                    date_format='mm/dd/yyyy',
        #                    datetime_format='mm/dd/yyyy')
        #out_data[list_keys[i]].to_excel(writer, sheet_name=list_keys[i])
        #writer.save()

index_dif = [cods.index(x) for x in get_cods(nuc='difusao')]
difusao   = ipca_var_nuc.iloc[index_dif] > 0
dif       = difusao.mean(axis=0)
dif.index = pd.to_datetime(dif.index)

dif15          = dif[0::2]; dif15_dsz      = dessaz_df(dif15)
dif15_mm3m     = dif15.rolling(3).apply(lambda x: np.average(x), raw=True)
dif15_mm3m_dsz = dif15_dsz.rolling(3).apply(lambda x: np.average(x), raw=True)

dif30          = dif[1::2]; dif30_dsz      = dessaz_df(dif30)
dif30_mm3m     = dif30.rolling(3).apply(lambda x: np.average(x), raw=True)
dif30_mm3m_dsz = dif30_dsz.rolling(3).apply(lambda x: np.average(x), raw=True)

dif_dsz      = pd.concat([dif15_dsz, dif30_dsz], axis=0).sort_index(ascending=1)
dif_mm3m     = pd.concat([dif15_mm3m, dif30_mm3m], axis=0).sort_index(ascending=1)
dif_mm3m_dsz = pd.concat([dif15_mm3m_dsz, dif30_mm3m_dsz], axis=0).sort_index(ascending=1)
dif_table    = pd.concat([dif, dif_dsz, dif_mm3m, dif_mm3m_dsz], axis=1)
dif_table.columns = ['Difusao','Difusao_dsz','MM3m','MM3m_dsz']

out_data['difusao']   = dif_table

# Create a Pandas Excel writer using XlsxWriter as the engine.
file_nuc = path_data + 'IPCA_base_nucleos.xlsx'
wb = xw.Book(file_nuc)
for i, key in enumerate(list_keys):
    sht = wb.sheets(key)
    sht.range('A1').value = out_data[key]

#atualiza excel
wb_var  = xw.Book(file_var)
sht_var = wb_var.sheets('var')
sht_var.range('A1').value = ipca_var_base

wb_peso = xw.Book(file_peso)
sht_peso = wb_peso.sheets('peso')
sht_peso.range('A1').value = ipca_pes_base

ipca_var_base.to_excel(file_var)
ipca_pes_base.to_excel(file_peso)