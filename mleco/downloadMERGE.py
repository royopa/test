# -*- coding: utf-8 -*-

from ftplib import FTP
import os
from time import localtime, strftime
import datetime
import sys
from collections import namedtuple

'''Clona repositorios do MERGE e MERGE_GPM_LATE_DAILY para o local
Caminhos são especificados nas variaveis no início do bloco do script.

Compara existencia dos arquivos nos repositorios a partir de seus nomes, apenas.

Pode chamar o script com argumento ano, que será usado apenas para o MERGE comum.
Nesse caso irá clonar o repositório daquele ano especificado. Se nao informado, irá
fazer download do ano atual usando a data do computador.
'''


def updateLocalDir(ftp, ftpDir, localDir):
    
    if not os.access(localDir, os.F_OK):
        os.makedirs(localDir)
    arqLocal = os.listdir(localDir)
        
    ftp.cwd(ftpDir)
    arqFtp = ftp.nlst()
    novosArqs = sorted(list(set(arqFtp).difference(set(arqLocal))))       

    for arq in novosArqs:
        print ('Fazendo Download de arquivo %s'%(arq))
        with open(localDir + '\\%s'%arq, 'wb') as f1:
            ftp.retrbinary('RETR %s'%arq, f1.write)
    return None
    
    

MERGE_FTP = 'ftp.cptec.inpe.br'
DATA_DIR = '/modelos/io/produtos/MERGE/'
GPM_DIR = os.path.join(DATA_DIR,'GPM/DAILY/MERGE_GPM_LATE')

MERGE_REPO = r'F:\DADOS\ASSET\MACROECONOMIA\DADOS\Base de Dados\OUTROS\MERGE PRECIP'

GPM_REPO = os.path.join(MERGE_REPO, 'GPM/LATE')
  
ftp = FTP(MERGE_FTP)
ftp.login()

#Faco download considerando dia base sendo ontem
arg_names = ['script','ano']
args = dict(zip(arg_names, sys.argv))
Arg_list = namedtuple('Arg_list', arg_names)
args = Arg_list(*(args.get(arg, None) for arg in arg_names))
if args.ano:
    anoBase = int(args.ano)
else:
    anoBase = localtime().tm_year
#diaBase = datetime.date(*tuple(map(int, strftime('%Y/%m/%d', localtime()).split('/')))) + datetime.timedelta(days=-1)

localMERGEDir = MERGE_REPO + '\\%s'%anoBase
ftpMERGEdir = DATA_DIR + '/%s'%anoBase

for k in ['GPM', 'MERGE']:
    if k == 'GPM': # Sempre confere por arquivos novos (baseado no nome) e atualiza local.
                   # Portanto clona repositório
        ftp.cwd(GPM_DIR)
        dispMeses = set(ftp.nlst())
        for m in list(dispMeses):
            localDir = GPM_REPO + '/%s'%m
            updateLocalDir(ftp, GPM_DIR + '/%s'%m, localDir)

    elif k == 'MERGE':
        localDir = localMERGEDir
        ftpDir = ftpMERGEdir
        updateLocalDir(ftp, ftpDir, localDir)
ftp.quit()