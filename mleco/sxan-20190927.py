# serie = 'pim_1 Bens de capital'
# a=S_complete(serie)
# a.run()

import numpy as np
import pandas as pd
#import sys
#sys.path.append(r'F:\SISTDAD\MEMPGRP\BMORIER\python\lib')
#sys.path.append(r'Z:\Macroeconomia\codes\Projetos\MLEco')
#sys.path.append(r'Z:\Macroeconomia\codes')
#sys.path.append(r'Z:\Macroeconomia\databases')
from mongo_load import transform_series
from mDataStore.globalMongo import mds
import mDataStore.freqHelper as f
from S_clean_db import S_clean_db
from S_univariate_selection import S_univariate_selection
from S_linear_model_vp import S_all_estimator
from S_complete import S_complete

serie = 'pim_1 Industria geral'
a=S_complete(serie)
a.run_()

#serie = 'abpo_TOTAL'
#b = S_complete(serie)
#b.run_()


# PIB
#serie = 'pib_volume_Agropecuaria - total_nsa'
#b = S_complete(serie, frequency='quarterly')
#b.run_()
#
#serie = 'pib_volume_Industrias extrativas_nsa'
#b = S_complete(serie, frequency='quarterly')
#b.run_()
#
#serie = 'pib_volume_Industrias de transformacao_nsa'
#b = S_complete(serie, frequency='quarterly')
#b.run_()
#
#serie = 'pib_volume_Eletricidade e gas, agua, esgoto, atividades de gestao de residuos_nsa'
#b = S_complete(serie, frequency='quarterly')
#b.run_()
#
#serie = 'pib_volume_Construcao_nsa'
#b = S_complete(serie, frequency='quarterly')
#b.run_()
#
#serie = 'pib_volume_Comercio_nsa'
#b = S_complete(serie, frequency='quarterly')
#b.run_()
#
#serie = 'pib_volume_Transporte, armazenagem e correio_nsa'
#b = S_complete(serie, frequency='quarterly')
#b.run_()
#
#serie = 'pib_volume_Informacao e comunicacao_nsa'
#b = S_complete(serie, frequency='quarterly')
#b.run_()
#
#serie = 'pib_volume_Atividades financeiras, de seguros e servicos relacionados_nsa'
#b = S_complete(serie, frequency='quarterly')
#b.run_()
#
#serie = 'pib_volume_Atividades imobiliarias_nsa'
#b = S_complete(serie, frequency='quarterly')
#b.run_()
#
#serie = 'pib_volume_Outras atividades de servicos_nsa'
#b = S_complete(serie, frequency='quarterly')
#b.run_()
#
#serie = 'pib_volume_Administracao, saude e educacao publicas e seguridade social_nsa'
#b = S_complete(serie, frequency='quarterly')
#b.run_()

#serie = 'pim_1 Industria geral'
#b=S_complete(serie, transformation='mom')
#b.run_()

# serie = 'pim_1 Bens de capital'
# b=S_complete(serie)
# b.run_()
#
# serie = 'pim_2 Bens intermediarios'
# c=S_complete(serie)
# c.run_()
#
# serie = 'pim_2 Industrias extrativas'
# a=S_complete(serie)
# a.run()
#
# serie = 'pim_3 Bens de consumo'
# a=S_complete(serie)
# a.run()
#
# serie = 'pim_3 Industrias de transformacao'
# a=S_complete(serie)
# a.run()

# serie = 'pmc_Artigos farmaceuticos, medicos, ortopedicos, de perfumaria e cosmeticos'
# a=S_complete(serie)
# a.run()
#
# serie = 'pmc_Combustiveis e lubrificantes'
# a=S_complete(serie)
# a.run()
#
# serie = 'pmc_Equipamentos e materiais para escritorio, informatica e comunicacao'
# a=S_complete(serie)
# a.run()
#
# serie = 'pmc_Hipermercados e supermercados'
# a=S_complete(serie)
# a.run()
#
# serie = 'pmc_Hipermercados, supermercados, produtos alimenticios, bebidas e fumo'
# a=S_complete(serie)
# a.run()
#
#serie = 'pmc_Indice de volume de vendas no comercio varejista'
#a=S_complete(serie)
#a.run_()

#serie = 'pmc_Indice de volume de vendas no comercio varejista ampliado'
#a=S_complete(serie)
#a.run_()

#serie = 'pms_Total'
#b=S_complete(serie)
#b.run_()

#
# serie = 'pmc_Livros, jornais, revistas e papelaria'
# a=S_complete(serie)
# a.run()
#
# serie = 'pmc_Material de construcao'
# a=S_complete(serie)
# a.run()
#
# serie = 'pmc_Moveis e eletrodomesticos'
# a=S_complete(serie)
# a.run()
#
# serie = 'pmc_Outros artigos de uso pessoal e domestico'
# a=S_complete(serie)
# a.run()
#
# serie = 'pmc_Tecidos, vestuario e calcados'
# a=S_complete(serie)
# a.run()
#
# serie = 'pmc_Veiculos, motocicletas, partes e pecas'
# a=S_complete(serie)
# a.run()