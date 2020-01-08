from splinter import Browser
from bs4 import BeautifulSoup
from datetime import datetime as dt
from os import listdir
from os.path import isfile, join
import os
import pandas as pd
import time
from numpy import *
from selenium import webdriver
from queue import Queue
from mUtil import Dict
q = None

dt0=dt(2018,12,1)
dt1=dt(2018,12,21)

indicadorLst_ = ['balComercial', 'balPgto', 'fiscal', 'indPreco', 'inflacao_12meses', 'inflacao_12_suavizada',
                'metaSelic', 'PIB', 'precosAdm_e_monit', 'prod_ind', 'cambio', 'top5']

indicadorLst = ['metaSelic', 'PIB', 'precosAdm_e_monit', 'prod_ind', 'cambio', 'top5']

calculoLst = ['media', 'mediana', 'std', 'coef_variacao', 'max', 'min', 'numResp']

l=len(indicadorLst_)-len(indicadorLst)
indicador = {ind: '{}'.format(k+l) for k, ind in enumerate(indicadorLst)}
calculo = {ind: '{}'.format(k) for k, ind in enumerate(calculoLst)}

browser=None
# profile=None
profilePath=r'C:\Users\bmorier\AppData\roaming\Mozilla\Firefox\Profiles\qsabwxos.default'
#discovered with about::profiles in adress bar of firefox
def startBrowser():
    global browser#, profile
    # profile = webdriver.FirefoxProfile()
    # profile.set_preference("browser.download.panel.shown", False)
    # #profile.set_preference("browser.helperApps.neverAsk.openFile", 'application/zip')
    # profile.set_preference("browser.helperApps.neverAsk.saveToDisk", 'application/zip')
    # profile.set_preference("browser.helperApps.neverAsk.saveToDisk", 'application/csv')

    browser=Browser(profile=profilePath)
    url='https://www3.bcb.gov.br/expectativas/publico/consulta/serieestatisticas'
    browser.visit(url)
    return browser
def getExpectAll(runThreads=False,maxThreads=30):
    global q
    dt00=dt(2000,1,1)
    dt11=dt.now()

    dts=pd.date_range(dt00,dt11,freq='11MS').to_pydatetime()
    if dts[-1]<dt11:
        dts=append(dts,dt11)

    if runThreads:
        threads = []
        q=Queue(maxThreads)
        for i in range(maxThreads): #start workers
            t = bcbExpThread()
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
                getExpect(ind,dts[k], dts[k+1])

def getExpect(ind,dt0,dt1,browser=browser,downPath=r'D:\BM\Downloads',outPath=r'D:\BM\Data\eco_csv\bcb_expect'):

    if browser is None:
        startBrowser()

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
            chk.check()
            label = browser.find_by_css('[for="{}"]'.format(id_chk))
            chkName=label[0].text
            for c1 in range(sz):
                if c != c1:
                    try:
                        chks = browser.find_by_css('[type=checkbox]')
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
                    rank=browser.find_by_id('tipoDeTaxa')

                if len(rank)==0:
                    rank_name=''
                    ranks=[None]
                else:
                    ranks=rank.find_by_tag('option')
                sz=len(ranks)
                for ii in range(sz):
                    rank = browser.find_by_id('tipoRanking')
                    if len(rank) == 0:
                        rank = browser.find_by_id('tipoDeTaxa')
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
                    button = browser.find_by_name('btnCSV')[-1]
                    file1=downPath+'/Séries de estatísticas.csv'

                    fileTrgt = 'exp'+rank_name+'_' + ind + '_' + chkName + '_' + per_text + '_' + calc + '_' + dt0.strftime(
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
    def __init__(self):
        super(bcbExpThread,self).__init__()
        self.browser=startBrowser()
        # self.ind=ind
        # self.dt0=dt0
        # self.dt1=dt1
        # self.browser=browser if not browser is None else startBrowser()
        # self.downPath=downPath
        # self.outPath=outPath
    def run(self):
        try:
            while(True):
                obj=q.get()
                if obj is None:
                    break
                getExpect(browser=self.browser,**obj)
                print('{}:{}-{} done'.format(self.ind,self.dt0,self.dt1))
        except Exception as e:
            print(e.__doc__)
            print(e)




if __name__=='__main__':
    getExpectAll(True)

