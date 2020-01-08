from splinter import Browser
from bs4 import BeautifulSoup
from datetime import datetime as dt
from os import listdir
from os.path import isfile, join
import os
import pandas as pd
import time,traceback
from numpy import *
from selenium import webdriver
from queue import Queue
from mUtil import Dict
#from py_init import *
from mDataStore.globalMongo import mds
import mDataStore as ds
import mUtil as uu
import numpy as np

q = None

dt0=dt(2018,12,1)
dt1=dt(2018,12,21)

indicadorLst_ = ['balComercial', 'balPgto', 'fiscal', 'indPreco', 'inflacao_12meses', 'inflacao_12_suavizada',
                'metaSelic', 'PIB', 'precosAdm_e_monit', 'prod_ind', 'cambio', 'top5']

indicadorLst = ['balComercial', 'balPgto', 'fiscal', 'indPreco', 'inflacao_12meses', 'inflacao_12_suavizada',
                'metaSelic', 'PIB', 'precosAdm_e_monit', 'prod_ind', 'cambio', 'top5']

calculoLst = ['media', 'mediana', 'std', 'coef_variacao', 'max', 'min', 'numResp']

MONTHS = {'jan': 1, 'fev': 2, 'mar': 3, 'abr': 4,  'mai': 5,  'jun': 6,
          'jul': 7, 'ago': 8, 'set': 9, 'out': 10, 'nov': 11, 'dez': 12}


FULL_MONTHS = {'janeiro': 1,  'fevereiro': 2, u'março': 3,    'abril': 4,
               'maio': 5,     'junho': 6,     'julho': 7,     'agosto': 8,
               'setembro': 9, 'outubro': 10,  'novembro': 11, 'dezembro': 12}

downLoadPath=r'D:\BM\Downloads'
outPath=r'D:\BM\Data\eco_csv\bcb_expect'

l=len(indicadorLst_)-len(indicadorLst)
indicador = {ind: '{}'.format(k+l) for k, ind in enumerate(indicadorLst)}
calculo = {ind: '{}'.format(k) for k, ind in enumerate(calculoLst)}

browser=None
# profile=None
profilePath=r'C:\Users\bmorier\AppData\roaming\Mozilla\Firefox\Profiles\qsabwxos.default'
#discovered with about::profiles in adress bar of firefox
def startBrowser(headless=False,downLoadPath=downLoadPath):
    global browser#, profile
    # profile = webdriver.FirefoxProfile()
    # profile.set_preference("browser.download.panel.shown", False)
    # #profile.set_preference("browser.helperApps.neverAsk.openFile", 'application/zip')
    # profile.set_preference("browser.helperApps.neverAsk.saveToDisk", 'application/zip')
    # profile.set_preference("browser.helperApps.neverAsk.saveToDisk", 'application/csv')
    if not os.path.exists(downLoadPath):
        os.makedirs(downLoadPath)

    prof = {}
    prof['browser.download.manager.showWhenStarting'] = 'false'
    prof['browser.helperApps.alwaysAsk.force'] = 'false'
    prof['browser.download.dir'] = downLoadPath
    prof['browser.download.folderList'] = 2
    prof[
        'browser.helperApps.neverAsk.saveToDisk'] = 'text/csv, application/csv, text/html,application/xhtml+xml,application/xml, application/octet-stream, application/pdf, application/x-msexcel,application/excel,application/x-excel,application/excel,application/x-excel,application/excel, application/vnd.ms- excel,application/x-excel,application/x-msexcel,image/png,image/jpeg,text/html,text/plain,application/msword,application/xml,application/excel,text/x-c'
    prof['browser.download.manager.useWindow'] = 'false'
    prof['browser.helperApps.useWindow'] = 'false'
    prof['browser.helperApps.showAlertonComplete'] = 'false'
    prof['browser.helperApps.alertOnEXEOpen'] = 'false'
    prof['browser.download.manager.focusWhenStarting'] = 'false'

    browser=Browser(headless=headless,profile_preferences=prof) #profile=profilePath,
    url='https://www3.bcb.gov.br/expectativas/publico/consulta/serieestatisticas'
    browser.visit(url)
    return browser

def getExpectAll(runThreads=False,maxThreads=30,headless=None,dt11=dt.now()):
    global q
    dt00=dt(2000,1,1)
    #dt11=dt.now()
    if headless is None:
        headless=runThreads
    dts=pd.date_range(dt00,dt11,freq='11MS').to_pydatetime()
    if dts[-1]<dt11:
        dts=append(dts,dt11)

    if runThreads:
        threads = []
        q=Queue(maxThreads)
        for i in range(maxThreads): #start workers
            t = bcbExpThread(headless=headless,downLoadPath=os.path.join(downLoadPath,'q{}'.format(i)))
            threads.append(t)
            t.start()

        for ind in indicador: #put jobs
            for k in range(len(dts)-1):
                obj=Dict({'ind':ind,'dt0':dts[k],'dt1':dts[k+1]})
                q.put(obj)
        q.join() #wait for job done

        for i in range(maxThreads): #stop workers
            q.put(None)

        for t in threads: #wait just in case
            t.join()

    else:
        for ind in indicador:
            for k in range(len(dts)-1):
                try:
                    status,db=mds.obj.load('bcb_' + '{}.{:%Y-%m-%d}-{:%Y-%m-%d}'.format(ind, dts[k], dts[k+1]), 'routine.bcb')
                except:
                    status=False
                if not status:
                    getExpect(ind,dts[k], dts[k+1])

def getExpect(ind, dt0, dt1, browser=browser, downLoadPath=downLoadPath, outPath=outPath):

    if browser is None:
        browser=startBrowser()

    browser.select('indicador',indicador[ind])
    chks=browser.find_by_css('[type=checkbox]')
    if len(chks)==0:
        chks = browser.find_by_css('[type=radio]')

    sz=len(chks)
    if sz == 0:
        sz=1
    for c  in range(sz):
        chks = browser.find_by_css('[type=checkbox]')
        if len(chks) == 0:
            chks = browser.find_by_css('[type=radio]')
        if len(chks)==0:
            chks = [None]

        chk=chks[c]
        if chk is None:
            chkName=''
        else:
            id_chk=chk['id']
            label = browser.find_by_css('[for="{}"]'.format(id_chk))
            chkName=label[0].text
            chk.check()
            for c1 in range(sz):
                if c != c1:
                    try:
                        chks = browser.find_by_css('[type=checkbox]')
                        time.sleep(0.2)
                        chks[c1].uncheck()
                    except:
                        pass

        #soup = BeautifulSoup(browser.html, 'html.parser')

#browser.find_by_id('grupoIndicePreco:opcoes_5')[0].check()
        per_ = browser.find_by_id('periodicidade')
        if len(per_)>0:
            per = browser.find_by_id('periodicidade')[0]  # .select('0')
            opts = per.find_by_tag('option')
            sz = len(opts)
            noPer=False
        else:
            sz=1
            noPer=True
        for o in range(sz):
            if o==0 and not noPer:
                continue
            if noPer:
                per_text=''
            else:
                per_ = browser.find_by_id('periodicidade')
                if len(per_) > 0:
                    per = browser.find_by_id('periodicidade')[0]  # .select('0')
                    opts = per.find_by_tag('option')
                    opt = opts[o]
                    per_text = opt.text
                    per.select(opt.value)

            for calc in calculo:
                try:
                    browser.select('calculo',calculo[calc])
                except:
                    continue
                #browser.select('periodicidade','0')
                browser.find_by_name('tfDataInicial')[0].value=dt0.strftime("%d/%m/%Y")
                browser.find_by_name('tfDataFinal')[0].value=dt1.strftime("%d/%m/%Y")


                ini=browser.find_by_css('[name$=ReferenciaInicial]')
                for i_ in ini:
                    i_.select('0')

                fim=browser.find_by_css('[name$=ReferenciaFinal]')
                for f_ in fim:
                    optsf = f_.find_by_tag('option')
                    f_.select(optsf[-1].value)


                rank = browser.find_by_id('tipoRanking')

                if len(rank)==0:
                    rank_name=''
                    ranks=[None]
                else:
                    ranks=rank.find_by_tag('option')
                sz=len(ranks)
                for ii in range(sz):
                    rank = browser.find_by_id('tipoRanking')
                    if len(rank) == 0:
                        rank_name = ''
                        ranks = [None]
                    else:
                        ranks = rank.find_by_tag('option')
                    r=ranks[ii]
                    if not r is None:
                        if ii==0:
                            continue
                        rank_name = r.text
                        rank.select(r.value)

                    ttaxa=browser.find_by_id('tipoDeTaxa')
                    if len(ttaxa) == 0:
                        ttaxa_name = ''
                        ttaxas = [None]
                    else:
                        ttaxas = ttaxa.find_by_tag('option')
                    szt = len(ttaxas)
                    for iii in range(szt):
                        ttaxa = browser.find_by_id('tipoDeTaxa')
                        if len(ttaxa) == 0:
                            ttaxa_name = ''
                            ttaxas = [None]
                        else:
                            ttaxas = ttaxa.find_by_tag('option')
                        t = ttaxas[iii]
                        if not t is None:
                            if iii == 0:
                                continue
                            ttaxa_name = t.text
                            ttaxa.select(t.value)

                        button = browser.find_by_name('btnCSV')[-1]
                        file1= downLoadPath + '/Séries de estatísticas.csv'

                        fileTrgt = 'exp'+rank_name+'_' + ind + '_' + ttaxa_name +'_'+chkName + '_' + per_text + '_' + calc + '_' + dt0.strftime(
                            "%Y-%m-%d") + '_' + dt1.strftime("%Y-%m-%d") + '.csv'
                        fileOut=outPath+'/'+fileTrgt
                        if not os.path.exists(fileOut):
                            if os.path.exists(file1):
                                os.remove(file1)
                            button.click()
    #                        prompt = browser.get_alert()


                            err=browser.find_by_xpath("//*[contains(text(),'Nenhuma estatística que satisfaça aos parâmetros')]")
                            if len(err)==0:
                                try:
                                    os.rename(file1,fileOut)
                                except:
                                    time.sleep(3)
                                    os.rename(file1,fileOut)

                #files = [f for f in listdir(mypath) if isfile(join(mypath, f))]

                #browser.find_by_id('mesReferenciaInicial').select('0')
                #browser.select("divPeriodoRefereEstatisticas:grupoMesReferencia:anoMesReferenciaInicial",'11')

                # browser.find_by_id('mesReferenciaFinal').select('0')
                # browser.select("divPeriodoRefereEstatisticas:grupoMesReferencia:anoMesReferenciaFinal",'12')

#browse r.fill('q', 'splinter - python acceptance testing for web applications')

import threading

#for ind in indicador:


class bcbExpThread(threading.Thread):
    def __init__(self,headless=False,downLoadPath=downLoadPath):
        super(bcbExpThread,self).__init__()
        self.browser=startBrowser(headless=headless,downLoadPath=downLoadPath)
        self.downLoadPath=downLoadPath
        # self.ind=ind
        # self.dt0=dt0
        # self.dt1=dt1
        # self.browser=browser if not browser is None else startBrowser()
        # self.downPath=downPath
        # self.outPath=outPath
    def run(self):
        while(True):
            obj=q.get()
            if obj is None:
                break
            try:
                status,db=mds.obj.load('bcb_' + '{}.{:%Y-%m-%d}-{:%Y-%m-%d}'.format(obj.ind, obj.dt0, obj.dt1), 'routine.bcb')
                doSave=False
            except:
                status=False
                doSave=True
            if doSave:
                mds.obj.save('bcb_' + '{}.{:%Y-%m-%d}-{:%Y-%m-%d}'.format(obj.ind, obj.dt0, obj.dt1), False, 'routine.bcb')

            if status:
                q.task_done()
                print('{}:{:%Y-%m-%d}-{:%Y-%m-%d} already done'.format(obj.ind, obj.dt0, obj.dt1))
                continue

            try:
                getExpect(browser=self.browser,downLoadPath=self.downLoadPath,**obj)
                mds.obj.save('bcb_' + '{}.{:%Y-%m-%d}-{:%Y-%m-%d}'.format(obj.ind, obj.dt0, obj.dt1), True, 'routine.bcb')
                print('{}:{:%Y-%m-%d}-{:%Y-%m-%d} done'.format(obj.ind, obj.dt0, obj.dt1))
            except Exception as e:
                print('Error in {}.{:%Y-%m-%d}-{:%Y-%m-%d}'.format(obj.ind, obj.dt0, obj.dt1))
                print(e)
                traceback.print_tb(e.__traceback__)
            q.task_done()



def expect2mongo(path1=outPath):
    import mUtil as uu
    dfs=read2df(path1=path1)
    dfs2mongo(dfs)


def dfs2mongo(dfs):
    indTyp = array([d.index.values[0][-1].__class__.__name__ for d in dfs])
    uTyp = unique(indTyp)
    k=0
    for typ in uTyp:
        I=indTyp==typ
        dfA=pd.concat(array(dfs)[I],axis=0)

        uCat = dfA.index.unique('category')
        uName= dfA.index.unique('name')
        uFreq= dfA.index.unique('freq')
        uStat= dfA.index.unique('mstat')
        for cat in uCat:
            for name in uName:
                for freq in uFreq:
                    # for mstat in uStat:
                    try:
                        df=dfA[cat,name,freq]
                    except:
                        continue
                    print('writing {}/{}'.format(k,dfA.index.shape[0]))
                    df=df[~df.index.duplicated(keep='first')]
                    df=df.unstack(level='mstat')
                    nm1=('BCB_exp_'+cat+'_'+name+'_'+freq).encode('ascii',errors='ignore').decode("utf-8")
                    df.md=ds.metadataFundamental(nm1,
                        type='expectation',source='bcb',stDT=df.index[0][0],category=cat,
                                                 subname=name,expfreq=freq)
                    mds.write(df,library=mds.testVS,check_metadata=False,prune_previous_version=True)
                    k=k+1

    # uu.drop_duplicates_index(dfA)

def read2df(path1=outPath):
    import io
    dfs=[]
    lst=os.listdir(path1)
    for i,file in enumerate(lst):
        # if i ==10:
        #     break
        # i=3600
        # file=lst[i]
        print('{}/{}'.format(i,len(lst)))
        file1=os.path.join(path1,file)
        str1=file.replace('coef_variacao','coefVariacao')[3:]
        if str1.startswith('_'):
            str1=str1[1:]
        flds = str1.split('_')

        with open(file1) as fp:
            # txt=fp.read()
            txt=fp.readlines()

        #sometimes the file comes with two or more indicators. It should have only one. Need to filter
        heads=[(i,t) for i,t in enumerate(txt) if not t.endswith(';\n')]

        correctHead=[k for k,head in enumerate(heads) if 'Período' in head[1]] #flds[3]
        # assert(len(correctHead)==1)

        for k in correctHead:
            if len(correctHead) > 1:
                code=heads[k][1].split('-')[1].replace(' ','')
            else:
                code=''
            txt_f=array(txt)[heads[k][0]:heads[k+1][0]] if k+1<len(heads) else array(txt)[heads[k][0]:]
            txt_l=[t[:-2] for i,t in enumerate(txt_f) if t.endswith(';\n')
                            and ((i==1) or not t.startswith('Data'))]
            txt1='\n'.join(txt_l)


    #        fileTrgt = 'exp' + rank_name + '_' + ind + '_' + ttaxa_name + '_' + chkName + '_' + per_text + '_' + calc + '_' + dt0.strftime(

            cat1='+'.join([flds[1],flds[0]]) if flds[0] !='' else flds[1]
            nm1='+'.join([code,flds[3],flds[2]]) if flds[2] !='' else flds[3]
            # dtype1={'2014':np.float64, '2015':np.float64, '2016':np.float64, '2017':np.float64, '2018':np.float64, '2019':np.float64}
            # df1 = pd.read_csv(io.StringIO(txt1), sep=';', decimal=',',dtype=dtype1)

            # cols=txt_l[0].split(';')
            # dtypes1={c:np.float64 for c in cols[1:]}
            # txt1=txt1.replace(',','.').replace(';', ',')
            df1 = pd.read_csv(io.StringIO(txt1),na_values=' ', sep=';', decimal=',') #,engine='python'
            # df1 = pd.read_csv(io.StringIO(txt1),na_values=' ') #,engine='python'
            J =where(df1.dtypes[1:]!=np.float64)[0]
            for j in J:
                df1.iloc[:, j+1]=pd.to_numeric(df1.iloc[:,j+1], errors='coerce')

                # df1[df1.columns[j]]=pd.to_numeric(df1.iloc[:,j], errors='coerce')
                # df1[df1.columns[j]]=df1[df1.columns[j]].astype(np.float64)
            cols = df1.columns[1:].to_series()
            doRename = True
            df1 = df1.rename(columns={' ': 'value'})
            try:
                cols=cols.astype(float64)
            except:
                for m1,n1 in MONTHS.items():
                    cols=cols.str.replace(m1,str(n1))
                try:
                    cols=pd.to_datetime(cols,format='%m/%Y')
                except:
                    try:
                        cols=cols.str.split(' a ',expand=True)
                        cols=pd.to_datetime(cols.iloc[:,-1],format='%m/%Y')
                    except:
                        print('unable to conver cols for {}'.format(file))
                        doRename=False
            if doRename:
                df1=df1.rename(columns={c:cols[i] for i,c in enumerate(df1.columns[1:])})

#            try



            df1.Data=pd.to_datetime(df1.Data,format='%d/%m/%Y')
            df1['category']=cat1
            df1['name']=nm1
            df1['freq']=flds[-4]
            df1['mstat']=flds[-3]
            df1.set_index(['category','name','freq','mstat','Data'],inplace=True)
            assert(df1.index.is_unique)
            df1=df1.stack()
            dfs.append(df1)




    return dfs
            # df1 = pd.read_csv(fp,sep=';',decimal=',',skiprows=1)





if __name__=='__main__':
    getExpectAll(True,7,headless=True,dt11=dt(2018,12,23))
    #getExpectAll(False,1,headless=False,dt11=dt(2018,12,23))

    expect2mongo(path1=outPath)
    # dfs=uu.load_obj('dfs')
    # dfs2mongo(dfs)