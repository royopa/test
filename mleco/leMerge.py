import numpy as np
from numpy import ma
from py3grads import Grads
import os
import datetime

def readCtlFile(dataIni,dataFim,var,parentFolder):    
    
    horario=datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
    errorLog = open(parentFolder+'ErrorLog.txt','a')
    ga=Grads(verbose=False)    
    datas=getDates(dataIni,dataFim)    
    dados=[]    
    lins=313 #from .ctl File
    cols=245    
    for data in datas:
        fileName=parentFolder+'%s/prec_%s.ctl'%(data[0:4],data)      
        print (fileName)
        try:
            arq=ga('open %s'%fileName)
            dados.append(ga.exp(var))
        except FileNotFoundError:
            errorLog.write('Arquivo %s_%s.ctl nao encontrado ou danificado. Rodada iniciada em %s\n'%(var,data,horario))            
            dados.append(ma.zeros((lins,cols))+np.nan)
            continue
        ga.cmd('close 1') #fecha arquivo no GrADS
    
    
    coordX=np.zeros((lins,cols))
    coordY=np.zeros((cols,lins))
    coordX[range(lins)]=np.array(np.arange(-82.8,-82.8+(cols)*0.2,0.2))
    coordY[range(cols)]=np.array(np.arange(-50.2,-50.2+(lins)*0.2,0.2))
    coordY=coordY.transpose()
    
    del ga
    
    return dados,coordX,coordY

def isValidDate(data):
    
    ano=int(data[:4])
    mes=int(data[4:6])
    dia=int(data[6:8])
    if dia<0 or mes>12 or mes<0 or ano<0:
        return False
    if mes in [1,3,5,7,8,10,12]:
        if dia>31:
            return False
        else:
            return True
    elif mes==2:
        if np.mod(ano,400)==0 or (np.mod(ano,4)==0 and np.mod(ano,100)!=0):
            if dia<=29:
                return True
        else:
            if dia <=28:
                return True
        return False        
    else:
        if dia<=30:
            return True
        else:
            return False
    
    return None         
    
def getDates(diaIni,diaFim):
    
    datas=[diaIni]
    temp=diaIni
    ano=int(diaIni[:4])
    mes=int(diaIni[4:6])
    dia=int(diaIni[6:8])
    while temp!=diaFim:
        dia+=1
        temp='%s%s%s'%(ano,str(mes).zfill(2),str(dia).zfill(2))
        if not isValidDate(temp):
            dia=1
            mes+=1
            temp='%s%s%s'%(ano,str(mes).zfill(2),str(dia).zfill(2))
            if not isValidDate(temp):
                mes=1
                ano+=1
                temp='%s%s%s'%(ano,str(mes).zfill(2),str(dia).zfill(2))
        datas.append(temp)        
    
    return datas
    
def readMask(codBacia,parentDir,gridModel='MERGE'):
    
    mask=np.loadtxt(parentDir+str(codBacia).zfill(3)+'_mask%s.txt'%gridModel)
    
    return mask

def writeAnnualSeries(anoIni=1998,anoFim=1998,var='prec',gridModel='MERGE',parentDir='C:/Felipe/Mudclima/dadosMerge/'):
        
    ano=anoIni
    while ano<=anoFim:
        dataIni=str(ano)+'0101'
        if ano==1998: dataIni=str(ano)+'0102'
        dataFim=str(ano)+'1231'
        if ano==2019: dataFim=str(ano)+'0201'
        serie,lons,lats = readCtlFile(dataIni,dataFim,var,parentDir)
        datas=getDates(dataIni,dataFim)    
        ano+=1
    return None

def writeCoorFile(newPath,mask,lats,lons):

    fcoor=open(newPath+'coor.txt','w',0)
    lons=ma.array(lons,mask=mask)
    lats=ma.array(lats,mask=mask)          
    for i in range(len(lats[~lats.mask])): fcoor.write('\t'+'%5.1f'%lats[~lats.mask][i])
    fcoor.write('\n')              
    for i in range(len(lons[~lons.mask])): fcoor.write('\t'+'%5.1f'%lons[~lons.mask][i])
    fcoor.write('\n')
    fcoor.close()

    return None          

if __name__ == '__main__':   
    writeAnnualSeries(anoIni=1998,anoFim=2019,var='prec')
        