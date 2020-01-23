import globalM
import urllib.request
import ftplib
import os.path
from pandas import ExcelWriter
from pandas import ExcelFile
import pandas as pd
import globalM
import mUtil as uu
from datetime import datetime as dt
import datetime
import threading
from subprocess import call
from shutil import copyfile
import zipfile
import mDataStore as ds

#copyfile(src, dst)
def importBMFAll():
    '''
    Download txts/xmls from website
    '''
    thread1 = threading.Thread(target=importBMFNew)
    thread2 = threading.Thread(target=importMktData)
    thread3 = threading.Thread(target=importOthersB3)

    thread1.start()
    thread2.start()
    thread3.start()

    thread1.join()
    thread2.join()
    thread3.join()
    #importBMFNew()
    #importMktData()
    #importOthersB3()


def saveAll():
    '''
    Transform txts into pickle files
    '''
    savePregaoFinal()
    savePregaoAjustes()
    saveCadastroXML()
    savepPesqXML()
    savePremioEq()
    savePremioRef()

def remove_ext(dir_name,ext):
    if not os.path.exists(dir_name):
        return
    test = os.listdir(dir_name)

    for item in test:
        if item.endswith("."+ext):
            os.remove(os.path.join(dir_name, item))

def get_ext(dir_name,ext):
    if not os.path.exists(dir_name):
        return None
    test = os.listdir(dir_name)

    for item in test:
        if item.endswith("."+ext):
            return item
    return None

def genFile(minSize,path1,ext,mode,extract_ext):
    '''
    Generator for processing text files/xmls. Basically extracts a the next file and return
    :param minSize:
    :param path1:
    :param ext:
    :param mode:
    :param extract_ext:
    :return:
    '''
    path2 = path1 + '/out/'
    if not os.path.exists(path2):
        os.makedirs(path2)

    for file in os.listdir(path1):
        if not os.path.exists(path1+file):
            continue
        if os.path.getsize(path1+file) > minSize and file.endswith('.'+ext) :
            file1=file[:-len(ext)]+'exe'
            if mode == 'extract_exe':
                remove_ext(path1,extract_ext)
                remove_ext(path1,'exe')
                copyfile(path1+file,path1+file1)

                try:
                    call(path1+file1,cwd=path2,shell=True)
                except:
                    warn('call to file:{} returned exception'.format(file1))
                    continue
                file2=get_ext(path2,extract_ext)
                remove_ext(path2,'exe')
                if file2 is None:
                    continue
                os.rename(path2+file2,path1+file2)
                remove_ext(path2,extract_ext)

                #assert(not file2 is None)
                yield file2
            elif mode == 'extract_zip':
                path2=path1+'ext'
                remove_ext(path2,extract_ext)
                with zipfile.ZipFile(path1+file, 'r') as zip_ref:
                    zip_ref.extractall(path2)
                file2=get_ext(path2,extract_ext)
                assert(not file2 is None)
                os.rename(path2+'/'+file2,path1+file2)
                yield file2
            elif mode == 'extract_zip_zip':
                path2=path1+'/out'
                remove_ext(path1,extract_ext)
                remove_ext(path2,extract_ext)
                try:
                    with zipfile.ZipFile(path1+file, 'r') as zip_ref:
                        zip_ref.extractall(path2)
                except:
                    continue

                filezip = get_ext(path2, 'zip')

                if filezip:
                    try:
                        with zipfile.ZipFile(path2+'/'+filezip, 'r') as zip_ref:
                            zip_ref.extractall(path2)
                    except:
                        continue
                remove_ext(path2,'zip')

                file2=get_ext(path2,extract_ext)
                os.rename(path2+'/'+file2,path1+file2)
                assert(not file2 is None)
                yield file2

            elif mode == 'extract_zip_exe':
                path2=path1+'/out'
                remove_ext(path1,extract_ext)
                remove_ext(path1,'exe')
                remove_ext(path2,extract_ext)
                with zipfile.ZipFile(path1+file, 'r') as zip_ref:
                    zip_ref.extractall(path2)

                fileex_ = get_ext(path2, 'ex_')
                fileexe = file[:-len(ext)] + 'exe'

                os.rename(path2 + '/' + fileex_, path2 + fileexe)

                try:
                    call(path2+fileexe,cwd=path2,shell=True)
                except:
                    warn('call to file:{} returned exception'.format(file1))
                    continue
                file2=get_ext(path2,extract_ext)
                remove_ext(path2,'exe')
                if file2 is None:
                    continue
                file2_=file[:-3]+'txt' #to keep structure of exe
                os.rename(path2+'/'+file2,path1+file2_)
                remove_ext(path2,extract_ext)

                yield file2_

            else:
                raise(Exception('invalid mode'))

def savePregaoFinal(path1=globalM.dataRoot+ '/b3/ContratosPregaoFinal/'):
    #TODO: depurar e fazer codigo de insert no mongo
    #pregao final

    dfs=[]
    for i,f in enumerate(genFile(2000,path1,'ex_','extract_exe','txt')):
        dfs.append(_mongoImportB3BD_Final_csv(f,path1))
        # if i==10:
        #     break
    uu.save_obj(dfs,'b3_pregaoFinal')
    #df=pd.concat(dfs)

    #pregao ajustes
def savePregaoAjustes():

    path1 = globalM.dataRoot + '/b3/ContratosPregaoAjuste/'
    dfs=[]
    for i,f in enumerate(genFile(2000,path1,'ex_','extract_exe','txt')):
        dfs.append(_mongoImportB3BD_Ajustes_csv(f,path1))
        # if i==10:
        #     break
    uu.save_obj(dfs,'b3_pregaoAjustes')


def writeAlltoDB():
    '''
    Import dfs from save into DB
    :return:
    '''


mercList=['BGI','CCM','DAP','DDI','DI1','DOL','IND','D11','D12','D13','D14','FRC','ICF','IDI','OZ1','WIN',
          'WDL','SOJ']



def writeDFSPregao(file1='b3_pregaoFinal'):
    from .globalMongo import mds
    from .mongo import metadataAsset,metadataOption

    dfs = uu.load_obj(file1)
    df=pd.concat(dfs)

    flds=['dt','code','serieVenc','venc','strike','valPonto','volRS','qtdAberto','qtdNeg','qtdTrans','ultOCP','ultOVD',
     'abtNeg','minNeg','maxNeg','medNeg','ultNeg','dtUltNeg','horaUltNeg','aju','du','dtLimiteNeg','dtLiqFin','vencContratoObj','codeGTS','tipoSerie']
    newFlds=['dt','codeMerc','srsCode','maturity','strike','multiplier','volume_fin','open_interest','neg','volume',
             'bid','ask','open','low','high','vwap','last','dtLast','timeLast','close','du','dtTradeLimit','dtFinSettle','underlyingSrsCode','code','cp']

    df=df[flds]
    df.columns=newFlds

    mdfFields=['dt','code','bid','ask','open','low','high','vwap','last','dtLast',
               'timeLast','close','du','volume_fin','open_interest','neg','volume']

    descFields=np.setdiff1d(newFlds,mdfFields).tolist()+['dt','code']


    df=df.loc[df.codeMerc.isin(mercList)]

    df0=df[mdfFields]
    dfMeta=df[descFields]
    uCode=np.unique(df0.code)

    for i,code1 in enumerate(uCode):
        df_ =  ds.mDataFrame( df0.loc[df0.code==code1])

        df_.set_index('dt',inplace=True)
        del df_['code']

        dfm_ = dfMeta.loc[dfMeta.code==code1].copy()
        dfm_.set_index('dt',inplace=True)
        del dfm_['code']

        # for c in dfm_.columns:
        #
        #     try:
        #         if dfm_[c].dtype==object:
        #             dfm_[c] = pd.to_numeric(dfm_[c])
        #     except:
        #         pass
        #     if dfm_[c].dtype==np.float64:
        #         assert((np.all(dfm_[c]==dfm_[c][0]) | np.isnan(dfm_[c][0]) ))
        #     else:
        #         assert(np.all(dfm_[c] == dfm_[c][0]))

        if dfm_.cp[-1] in ['C','V']:
            df_.md=metadataOption(code1+'_b3','option',df_.index[0].to_pydatetime(),None,'BRL',False,dfm_.maturity[-1].to_pydatetime(),
                                   strike=dfm_.strike[-1],underlying=dfm_.codeMerc[-1] +dfm_.underlyingSrsCode[-1],
                                   cp=dfm_.cp[-1].lower())
            df_.md.subtype='option'
        else:
            df_.md=metadataAsset(code1+'_b3','future',df_.index[0].to_pydatetime(),None,'BRL',False,dfm_.maturity[-1].to_pydatetime())
            df_.md.subtype='future'

        df_.md.source='B3'

        print('writing {}. {}/{}'.format(code1,i,uCode.size))
        if not df_.index.is_unique:
            nm=df_.index.name if not df_.index.name is None else 'index'
            df_=df_.reset_index().drop_duplicates(subset=nm, keep='last').set_index(nm)

        mds.write(df_,mds.b3VS,check_metadata=False,prune_previous_version=True)


def writePremioREF(file1='b3_premioREF'):
    from .globalMongo import mds
    from .mongo import metadataAsset,metadataOption

    dfs = uu.load_obj(file1)
    dfs=pd.concat(dfs)

    dfs.dt = pd.to_datetime(dfs.dt, format='%Y%m%d')
    dfs.venc = pd.to_datetime(dfs.venc, format='%Y%m%d')
    del dfs['id']
    del dfs['compl']
    del dfs['reg']
    del dfs['tipoUnderlying']
    del dfs['numCasasDec']
    yearStr=pd.DatetimeIndex(dfs.venc).year.astype(str)
    dfs['codeSerie'] = dfs.code + dfs.serie +yearStr
    dfs.set_index('codeSerie',inplace=True)

    uCode = pd.unique(dfs.index)
    assetLst = np.array(mds.b3VS.list_symbols())
    assetLst = [s.replace('_b3_opc_1BDay','') for s in assetLst]
    #uCode = np.setdiff1d(uCode,np.array(assetLst))
    uCode = [u for u in uCode if not u in assetLst]

    for i, code1 in enumerate(uCode):
        df_ = ds.mDataFrame(dfs.loc[code1].copy())
        if isinstance(dfs.loc[code1],pd.Series):
            continue
        df_.set_index('dt', inplace=True)
        #del df_['codeSerie']

        df_.md = metadataOption(code1 + '_b3_opc', 'option', df_.index[0].to_pydatetime(), None, 'BRL', False,
                                df_.venc[-1].to_pydatetime(),
                                strike=df_.strike[-1], underlying=df_.code[-1] + uu.futCodeFromDate(df_.venc[-1].to_pydatetime()),
                                cp=df_.tipoOpc[-1].lower())
        df_.md.subtype = 'option'
        df_.md.optModel = df_.modeloOpc[-1].lower()

        df1=df_[['premio']]
        df1.columns=['close']
        print('writing {} - {}/{}'.format(code1,i,len(uCode)))

        try:
            mds.delete(code1[:-4],ds.freqHelper.bday,mds.b3VS)
        except:
            pass
        df1=uu.drop_duplicates_index(df1)
        mds.write(df1,mds.b3VS,check_metadata=False,prune_previous_version=True)

        # del dfs['venc']
        # del dfs['code']
        # del dfs['strike']
        # del dfs['serie']





def writePremioEq(file1='b3_premioEq'):
    from .globalMongo import mds
    from .mongo import metadataAsset,metadataOption

    dfs = uu.load_obj(file1)

    dfs=pd.concat(dfs)

    dfs.dt = pd.to_datetime(dfs.dt, format='%Y%m%d')
    dfs.venc = pd.to_datetime(dfs.venc, format='%Y%m%d')
    yearStr=pd.DatetimeIndex(dfs.venc).year.astype(str)
    dfs.index=dfs.index+yearStr

    uCode = pd.unique(dfs.index)
    assetLst = np.array(mds.b3VS.list_symbols())
    assetLst = [s.replace('_b3_opc_1BDay','') for s in assetLst]
    #uCode = np.setdiff1d(uCode,np.array(assetLst))
    #uCode = [u for u in uCode if not u in assetLst]
    uCode = list(set(uCode)-set(assetLst))
    for i, code1 in enumerate(uCode):
        df_ = ds.mDataFrame(dfs.loc[code1].copy())
        if isinstance(dfs.loc[code1],pd.Series):
            continue

        df_.set_index('dt', inplace=True)

        df_.md = metadataOption(code1 + '_b3_opc', 'option', df_.index[0].to_pydatetime(), None, 'BRL', False,
                                df_.venc[-1].to_pydatetime(),
                                strike=df_.strike[-1], underlying=code1[:4] + uu.futCodeFromDate(df_.venc[-1].to_pydatetime()),
                                cp=df_.code[-1].lower())
        df_.md.subtype = 'equity_option'
        df_.md.optModel = df_.type[-1].lower()

        df1=df_[['premio','vol','strike']]
        df1.columns=['close','vol','strike']
        print('writing {} - {}/{}'.format(code1,i,len(uCode)))
        df1=uu.drop_duplicates_index(df1)
        mds.write(df1,mds.b3VS,check_metadata=False,prune_previous_version=True)


otherMerc=[]
saveClean=False
def saveCleanXML(fileCadastro='b3_cadastroXML',filePx='b3_pesqXML'):
    cad = uu.load_obj(fileCadastro)
    px = uu.load_obj(filePx)
    codes=list(set.union(*[set(p.keys()) for p in px]))
    codes1 = [c for c in codes if c in cad and 'code' in cad[c] and (
            any([cad[c]['code'].startswith(m) for m in mercList + otherMerc]) or
            ('nmInf' in cad[c] and cad[c]['nmInf'] == 'OptnOnEqtsInf'))]
    cad_clean = Dict({c: cad[c] for c in codes1})
    uu.save_obj(cad_clean, 'b3_cadastroXML_clean')
    #px_clean = [{c: p[c] for c in p if c in codes1} for p in px]
    px_clean = [Dict({c: p[c] for c in set.intersection(set(p.keys()),set(codes1))}) for p in px]
    uu.save_obj(px_clean, 'b3_pesqXML_clean')


def writeFromXML(fileCadastro='b3_cadastroXML',filePx='b3_pesqXML'):

    from .globalMongo import mds
    from .mongo import metadataAsset,metadataOption

    cad = uu.load_obj(fileCadastro)
    px = uu.load_obj(filePx)

    #must also get dates
    codes=list(set.union(*[set(p.keys()) for p in px]))

    if saveClean:
        saveCleanXML(fileCadastro,filePx)
    #px_ = {{k:l[k] for k in l} for l in px}
    #keys1 = [s for s in cad.keys()]

    lst_b3 = mds.find(library=[mds.b3VS,mds.b3VS_XML], metadata=False)
    lst_b3 = [l[1].replace('_1BDay','') for l in lst_b3]
    flds=('dt','FrstPric','MinPric','MaxPric','LastPric','TradAvrgPric','FinInstrmQty','OpnIntrst')
    cols=['open', 'low', 'high', 'close', 'vwap', 'volume','open_interest']
    map1={flds[i+1]:c for i,c in enumerate(cols)}
    for j,c in enumerate(codes):
        #must use dates here
        if c in cad:
            cad1=cad[c]
        if c in cad and any([cad1['code'].startswith(m) for m in mercList+otherMerc]) or cad1['nmInf'] == 'OptnOnEqtsInf':
            px1=[{k:v for (k,v) in p[c].items() if k in flds} for p in px]
            px1=[p for p in px1 if len(p)>0]
            df1 = ds.mDataFrame(pd.DataFrame.from_dict(px1))
            df1.set_index('dt',inplace=True)
            df1.sort_index(inplace=True)

            df1=df1[(~np.all(np.isnan(df1.values),1))]
            if df1.shape[0]==0:
                continue
            isOpt ='ExrcPric' in cad1

            if isOpt:
                code1=cad1['code']+'_b3_opc'
                optSubtype = 'equity_option' if ('nmInf' in cad1 and cad1['nmInf']=='OptnOnEqtsInf') else 'option'
                strike= cad1['ExrcPric'] if not isinstance(cad1['ExrcPric'],list) else cad1['ExrcPric'][-1][-1]
                cp = 'p' if 'PUT' in cad1['OptnTp'].upper() else 'c'
                underlyingId=str(cad1['UndrlygInstrmId']['OthrId']['Id'])[:-2]
                underlying=cad[underlyingId]['code']
                df1.md = metadataOption(code1,'option',df1.index[0],fut_like=False,maturity=cad1['XprtnDt'],strike=strike,underlying=underlying,cp=cp)
                df1.md.underlyingId=underlyingId
                df1.md.subtype=optSubtype
                df1.md.optModel='e' if cad1['OptnStyle'] =='EURO' else 'a'
                if optSubtype == 'equity_option':
                    strikes=cad1['ExrcPric']
                    if not isinstance(strikes,list):
                        strikes=[[None,strikes]]
                    strikes=np.array(strikes)
                    for i,s in enumerate(strikes[:,0]):
                        strikes[i,0] = dt(1900,1,1) if s is None else s
                    strikeSrs=pd.Series(strikes[:,1].astype(np.float64),strikes[:,0])
                    strikeSrs1=strikeSrs.reindex(df1.index,method='ffill')
                    df1['strike']=strikeSrs1
                    df1.md.strikes=strikes.tolist()
#                    strikeSrs.index[0]=None


            else:
                code1=cad1['code']+'_b3'
                df1.md = metadataAsset(code1,'future',df1.index[0],fut_like=True,maturity=cad1['XprtnDt'])
            df1.md.id = c
            df1=df1.rename(columns=map1)
            if code1 in lst_b3:
                df0 = mds.read(code1,library=[mds.b3VS,mds.b3VS_XML])
                df0_=df0.copy()
                df1_=df1.copy()
                try:
                    del df0_['strike']
                except:
                    pass
                try:
                    del df0_['open_interest']
                except:
                    pass
                try:
                    del df1_['strike']
                except:
                    pass
                try:
                    del df1_['open_interest']
                except:
                    pass
                df0 = df0.loc[(~np.all(pd.isnull(df0_.values), 1))]

                df1=df1.loc[~df1.index.isin(df0.index)&(~np.all(pd.isnull(df1_.values),1))]
                if df1.shape[0]==0:
                    continue
                md=df1.md
                df1=ds.mDataFrame(pd.concat([df0,df1],0,sort=True))
                df1.md=md

            df1=df1.loc[(~np.all(pd.isnull(df1.values),1))]

            if df1.shape[0]==0:
                continue

            #check if exists and append !!!
            print('{} = {}/{}'.format(code1,j,len(codes)))
            df1=uu.drop_duplicates_index(df1)
            if isOpt:
                mds.write(df1, mds.b3VS_XML, check_metadata=False, prune_previous_version=True)
            else:
                mds.write(df1,mds.b3VS,check_metadata=False,prune_previous_version=True)
            #break






#'ExrcPric'
def updateAccum(cad0,cadi,dti):
    f='ExrcPric'
    for k in cadi:
        if k in cad0 and f in cad0[k]:
            if not isinstance(cad0[k][f],list):
                cad0[k][f]=[[None, cad0[k][f]]]
            if cadi[k][f]!=cad0[k][f][-1][-1]:
                cad0[k][f].append([dti,cadi[k][f]])
        elif k not in cad0:
            cad0[k]=cadi[k]



# def updateAccum(cad0,cadi,dti):
#     for k in cadi:
#         try:
#             if isinstance(cad0[k],list):
#                 cmp=cad0[k][-1][-1] != cadi[k]
#             else:
#                 cmp=cad0[k] != cadi[k]
#         except:
#             cmp=False
#         try:
#             cmp2=k in cad0
#         except:
#             cmp2=False
#         if not cmp2:
#             cad0[k]=cadi[k]
#         elif isinstance(cadi[k],dict):
#             assert(isinstance(cad0[k],dict))
#             updateAccum(cad0[k], cadi[k],dti)
#         elif cmp:
#             if not isinstance(cad0[k],list):
#                 cad0[k]=[[None, cad0[k]]]
#             cad0[k].append([dti,cadi[k]])

def saveCadastroXML():
    path1 = globalM.dataRoot + '/b3/_new/cadastroInstrumentos/'
    #cads=[]
    cad0=None
    for i,f in enumerate(genFile(2000,path1,'zip','extract_zip_zip','xml')):
        cadi=_mongoImportB3_cadastro_XML(f,path1)
        if cad0 is None:
            cad0=cadi
        else:
            updateAccum(cad0,cadi,cadi[list(cadi.keys())[0]]['dt'])
        print(f)
        if i%10==1:
            print('saving')
            uu.save_obj(cad0, 'b3_cadastroXML')
        # if i == 10:
        #     break
    #df=pd.concat(dfs)
    uu.save_obj(cad0,'b3_cadastroXML')

def savepPesqXML():

    path1 = globalM.dataRoot + '/b3/_new/pesquisapregao/'
    pesqs=[]
    for i,f in enumerate(genFile(2000,path1,'zip','extract_zip_zip','xml')):
        pesqs.append(_mongoImportB3_BD_XML(f,path1))
        # if i == 1:
        #     break
    uu.save_obj(pesqs,'b3_pesqXML')

def savePremioRef():

    #premio ref
    path1 = globalM.dataRoot + '/b3/premio_ref/'
    dfs=[]
    for i,f in enumerate(genFile(2000,path1,'ex_','extract_exe','txt')):
        dfs.append(_mongoImportB3_premio_csv(f,path1))
        # if i == 10:
        #     break
    #df=pd.concat(dfs)
    uu.save_obj(dfs,'b3_premioREF')

def savePremioEq():
    #premio ref equities
    path1 = globalM.dataRoot + '/b3/_new/premioAcoes/'
    dfs=[]
    for i,f in enumerate(genFile(2000,path1,'zip','extract_zip_exe','txt')):
        dfs.append(_mongoImportB3_premio_acoes_csv(f,path1))
        # if i == 10:
        #     break
    uu.save_obj(dfs,'b3_premioEq')
    #df=pd.concat(dfs)





def _mongoImportB3BD_Final_csv(file,path1=globalM.dataRoot+ '/b3/ContratosPregaoFinal/'):
    #pandas.read_fwf(filepath_or_buffer, colspecs='infer', widths=None, **kwds)
    #file='BD_Final.txt'
    #path1=globalM.dataRoot+ '/b3/ContratosPregaoFinal/'
    widths =[6,3,2,8,2,3,1,1,4,6,8,13,13,13,13,8,8,8,5,1,8,5,1,8,1,8,1,8,1,8,1,8,5,1,8,6,8,1,8,1,8,1,13,1,1,13,1,13,13,
             13,8,8,1,1,8,1,8,1,8,13,13,9,5,5,5,4,13,13,8,3,20,20,1,4,8,8,1,13,1,13]
    colNames=['id','compl','reg','dt','tipoNeg','code','merc','tipoSerie','serieVenc','hora','venc','strike','valPonto',
              'volRS','volUS','qtdAberto','qtdNeg','qtdTrans','qtdUltOCP','sigUltOCP','ultOCP','qtdUltOVD','sigUltOVD',
              'ultOVD','sigAbtNeg','abtNeg','sigMinNeg','minNeg','sigMaxNeg','maxNeg','sigMedNeg','medNeg','qtdUltNeg',
              'sigUltNeg','ultNeg','horaUltNeg','dtUltNeg','sigUltNegAnt','ultNegAnt','sigFec','fec','sigAju','aju','sitAju',
              'sigAjuAnt','ajuAnt','sitAjuAnt','valAjuPContr','volExercRS','volExercUS','qtdNegExerc','qtdContrExerc','numCasasStar',
              'numCasasAju','percOscila','sigOscila','valDifPts','sigDiffPts','valEquiv','valDolAnt','valDol','valDeltaMarg','saques',
              'diasCorridos','du','vencContratoObj','margCliNorm','margHedger','dtEntrega','seqVencFut','codeVivaVoz','codeGTS',
              'canaisPermitidos','refResumoNeg','dtLimiteNeg','dtLiqFin','sigLoteMinNegociacao','loteMinNegociacao',
              'sigLoteMaxNegociacao','loteMaxNegociacao']

    df = pd.read_fwf(path1+file, widths=widths,header=None,names=colNames)
    flds1=['strike','ultOCP','ultOVD','abtNeg','minNeg','maxNeg','medNeg','ultNeg','ultNegAnt','fec']
    df.loc[:,flds1]=df.loc[:,flds1].values/(10.0**df.numCasasStar.values[:,None])
    flds_aju1 =['aju','ajuAnt']
    df.loc[:,flds_aju1]=df.loc[:,flds_aju1].values/(10**df.numCasasAju.values[:,None])

    fld=[[['valPonto','valDolAnt','valDol','valDeltaMarg'],7],[['valAjuPContr','valEquiv','margCliNorm','margHedger'],2],[['percOscila'],1]]

    for f_ in fld:
        df.loc[:,f_[0]]=df.loc[:,f_[0]]/(10**f_[1])

    dtflds=['dt','venc','dtUltNeg','dtEntrega','dtLimiteNeg','dtLiqFin']
    for fld in dtflds:
        dt1 = pd.to_datetime(df[fld], format='%Y%m%d',errors='coerce')
        df[fld] = dt1

    return df

def _mongoImportB3BD_Ajustes_csv(file,path1=globalM.dataRoot+ '/b3/ContratosPregaoAjuste/'):
    #pandas.read_fwf(filepath_or_buffer, colspecs='infer', widths=None, **kwds)
    #pandas.read_fwf(filepath_or_buffer, colspecs='infer', widths=None, **kwds)

    widths =[6,3,2,8,2,3,1,1,4,6,8,13,13,13,13,8,8,8,5,1,8,5,1,8,1,8,1,8,1,8,1,8,5,1,8,6,8,1,8,1,8,1,13,1,1,13,1,13,13,
             13,8,8,1,1,8,1,8,1,8,13,13,9,5,5,5,4,13,13,8,3,20,20,1,4,8,8,1,13,1,13]
    colNames=['id','compl','reg','dt','tipoNeg','code','merc','tipoSerie','serieVenc','hora','venc','strike','valPonto',
              'volRS','volUS','qtdAberto','qtdNeg','qtdTrans','qtdUltOCP','sigUltOCP','ultOCP','qtdUltOVD','sigUltOVD',
              'ultOVD','sigAbtNeg','abtNeg','sigMinNeg','minNeg','sigMaxNeg','maxNeg','sigMedNeg','medNeg','qtdUltNeg',
              'sigUltNeg','ultNeg','horaUltNeg','dtUltNeg','sigUltNegAnt','ultNegAnt','sigFec','fec','sigAju','aju','sitAju',
              'sigAjuAnt','ajuAnt','sitAjuAnt','valAjuPContr','volExercRS','volExercUS','qtdNegExerc','qtdContrExerc','numCasasStar',
              'numCasasAju','percOscila','sigOscila','valDifPts','sigDiffPts','valEquiv','valDolAnt','valDol','valDeltaMarg','saques',
              'diasCorridos','du','vencContratoObj','margCliNorm','margHedger','dtEntrega','seqVencFut','codeVivaVoz','codeGTS',
              'canaisPermitidos','refResumoNeg','dtLimiteNeg','dtLiqFin','sigLoteMinNegociacao','loteMinNegociacao',
              'sigLoteMaxNegociacao','loteMaxNegociacao']
    #file='BDAjuste.txt'
    df = pd.read_fwf(path1+file, widths=widths,header=None,names=colNames)

    flds1=['strike','ultOCP','ultOVD','abtNeg','minNeg','maxNeg','medNeg','ultNeg','ultNegAnt','fec']
    df.loc[:,flds1]=df.loc[:,flds1].values/(10.0**df.numCasasStar.values[:,None])
    flds_aju1 =['aju','ajuAnt']
    df.loc[:,flds_aju1]=df.loc[:,flds_aju1].values/(10**df.numCasasAju.values[:,None])

    fld=[[['valPonto','valDolAnt','valDol','valDeltaMarg'],7],[['valAjuPContr','valEquiv','margCliNorm','margHedger'],2],[['percOscila'],1]]

    for f_ in fld:
        df.loc[:,f_[0]]=df.loc[:,f_[0]]/(10**f_[1])

    dtflds=['dt','venc','dtUltNeg','dtEntrega','dtLimiteNeg','dtLiqFin']
    for fld in dtflds:
        dt1 = pd.to_datetime(df[fld], format='%Y%m%d',errors='coerce')
        df[fld] = dt1
    return df


def _mongoImportB3_premio_acoes_csv(file,path1 = globalM.dataRoot + '/b3/_new/premioAcoes/'):

    #file = 'PE170703.txt'
    colNames = ['code', 'type', 'venc', 'strike', 'premio', 'vol']
    df = pd.read_csv(path1 + file, ';', header=None, skiprows=1, names=colNames)
    df['dt'] = '20'+file[2:8]

    return df


def _mongoImportB3_premio_csv(file,path1=globalM.dataRoot+ '/b3/premio_ref/'):
    #file='Premio.txt'

    widths=[6,3,2,8,3,1,4,1,1,8,15,15,1]
    colNames=['id','compl','reg','dt','code','tipoUnderlying','serie','tipoOpc','modeloOpc','venc','strike','premio','numCasasDec']
    df = pd.read_fwf(path1+file, widths=widths,header=None,names=colNames)
    if not df.premio.dtype==np.float64:
        for i in range(len(df.premio)):
            try:
                df.premio.values[i]=float(df.premio[i])
            except:
                df.premio.values[i]=np.nan
        df.premio=df.premio.astype(np.float64)
    df.strike=df.strike/(10.0**df.numCasasDec)
    df.premio = df.premio / (10.0 ** df.numCasasDec)
    return df

#import xml.etree.ElementTree as ET
from mDataStore.util import XmlDictConfig
from mDataStore.util import removeNamespace
from mUtil import Dict
import numpy as np
def _mongoImportB3_BD_XML(file,path1=globalM.dataRoot+ '/b3/_new/pesquisapregao/'):

    #file='BVBG.086.01_BV000328201707030328000001818284323.xml'
    #file='BVBG.086.01_BV000328201707030328000002008265169.xml'
#    tree = ET.parse(path1+file1)
#    root = tree.getroot()
#    for doc in root.findall('Document'):

    import lxml.etree
    doc = lxml.etree.parse(path1+file)
    root=doc.getroot()
    # results = root.xpath(
    #     "//*[re:test_old(local-name(), '.*PricRpt')]",
    #     namespaces={'re': "http://exslt.org/regular-expressions"})
    removeNamespace(root)
    results = root.xpath('//PricRpt')

    d=Dict()
    for r in results:
        attr=r.find('FinInstrmAttrbts')
        nm=r.find('SctyId/TckrSymb').text
        id=r.find('FinInstrmId/OthrId/Id').text
        dt_=r.find('TradDt/Dt').text
        dt_=dt.strptime(dt_, '%Y-%m-%d')
        d_=Dict()
        for node in attr:
            try:
                d_[node.tag]=np.float64(node.text)
            except:
                d_[node.tag] = node.text
        d_['dt']=dt_
        #d_= XmlDictConfig(attr)
        d_['code']=nm
        d[id]=d_


    #xml=Dict(XmlDictConfig(root))
    #pandas.read_fwf(filepath_or_buffer, colspecs='infer', widths=None, **kwds)
    return d

def _mongoImportB3_cadastro_XML(file,path1 = globalM.dataRoot + '/b3/_new/cadastroInstrumentos/'):
    #pandas.read_fwf(filepath_or_buffer, colspecs='infer', widths=None, **kwds)

    #file1 = 'BVBG.028.02_BV000327201707030327153587456341493.xml'
    #file2 = 'BVBG.086.01_BV000328201707030328000002008265169.xml'
    #    tree = ET.parse(path1+file1)
    #    root = tree.getroot()
    #    for doc in root.findall('Document'):

    import lxml.etree
    doc = lxml.etree.parse(path1 + file)
    root = doc.getroot()
    # results = root.xpath(
    #     "//*[re:test_old(local-name(), '.*PricRpt')]",
    #     namespaces={'re': "http://exslt.org/regular-expressions"})
    removeNamespace(root)
    results = root.xpath('//Instrm')

    def recursive_dict(element):
        try:
            v=dt.strptime(element.text, '%Y-%m-%d')
        except:
            try:
                v = np.float64(element.text)
            except:
                v = element.text

        return element.tag, \
               Dict(dict(map(recursive_dict, element))) or v
    d = Dict()
    for i,r in enumerate(results):
        # if i%100==0:
        #     print(i)
        attr = r.find('InstrmInf')
        #nm = r.find('SctyId/TckrSymb').text
        dt_ = r.find('RptParams/RptDtAndTm/Dt').text
        id=r.find('FinInstrmId/OthrId/Id').text
        dt_ = dt.strptime(dt_, '%Y-%m-%d')
        d_=recursive_dict(attr)[1]
        # d_= XmlDictConfig(attr)
        nmInf=list(d_.keys())[0]
        dd=d_[nmInf]
        if 'TckrSymb' in dd:
            nm=dd['TckrSymb']
        elif 'ISIN' in dd:
            nm = dd['ISIN']
        else:
            continue
        if 'TradgEndDt' in dd:
            nm=nm #+str(dd['TradgEndDt'].year) #for options
        dd['Id']=id
        dd['dt'] = dt_
        dd['nmInf']=nmInf
        dd['code']=nm
        d[id] = dd

    return d


def _getHolidaysXLS():
    df = pd.read_excel(globalM.dataRoot + '/feriados_nacionais.xls','Plan1')
    f1=lambda x : isinstance(x,dt)
    df=df.Data[df.Data.apply(f1)]
    uu.save_obj(df.values.tolist(),'holidays_bz')


#http://www.b3.com.br/pesquisapregao/download?filelist=PR150919.zip
from warnings import warn
def _importBMFNew(urlbase,fileBase,outPath,suffix,dti,dtf):
    fer_bz=uu.load_obj('holidays_bz')
    dts = pd.bdate_range(dti,dtf,freq='C',holidays=fer_bz)

    for d in dts:
        file1='{}{:%y%m%d}.{}'.format(fileBase,d,suffix)
        fileout='{}{:%y%m%d}.zip'.format(fileBase,d) #bmf weird: always a zip is coming
        urlfile=urlbase+file1
        fp=outPath+'/'+fileout
        if not os.path.exists(fp):
            print('download {}'.format(file1))
         #   print(urlfile)
            try:
                urllib.request.urlretrieve(urlfile,fp)
            except:
                try:
                    urllib.request.urlretrieve(urlfile, fp)
                except:
                    print('UNABLE TO DOWNLOAD - MOVING ON')
            # if os.path.getsize(fp) < 30:
            #     warn('file: {} is empty. Deleting'.format(fp))
            #     os.remove(fp)
        else:
            print('{} exists'.format(fileout))

def importBMFNew():
    #http://www.b3.com.br/pesquisapregao/download?filelist=IR180920.zip,IN180921.zip,PE180920.ex_,VE180920.ex_,CT180621.ex_,CV180621.ex_,RE180920.ex_,
    urlbase='http://www.b3.com.br/pesquisapregao/download?filelist='
    #http://www.b3.com.br/pesquisapregao/download?filelist=PE180920.ex_,
   # fileBase=['PR','IR','IN','PE','VE','CT','CV','RE']
    # suffix=['zip','zip','zip','ex_','ex_','ex_','ex_','ex_']
    #outPath=['pesquisapregao/','indexReport/','cadastroInstrumentos/','premioAcoes/','superfAcoes/','cambioTaxas/','cambioVolume/','premioOpcoes/']
    fileBase = [ 'IR', 'IN', 'PE', 'VE', 'CT', 'CV', 'RE']
    suffix=['zip','zip','ex_','ex_','ex_','ex_','ex_']
    outPath=['indexReport/','cadastroInstrumentos/','premioAcoes/','superfAcoes/','cambioTaxas/','cambioVolume/','premioOpcoes/']
    outpath1=globalM.dataRoot+'/b3/_new/'

    for i,a in enumerate(outPath):
        outPath[i]=outpath1+outPath[i]
        if not os.path.exists(outPath[i]):
            os.makedirs(outPath[i])

    #dti=dt(2017,7,1)
    dti = dt(2015, 1, 1)
    dtf=dt.today()-datetime.timedelta(days=1)

    for i,u in enumerate(fileBase):
        _importBMFNew(urlbase, fileBase[i], outPath[i],suffix[i], dti, dtf)



def importFTP(ftpAddr,pathFTP,pathOut):
    #ftpAddr="ftp://ftp.bmf.com.br/PremioReferencia/"
    #ftpAddr = "ftp.bmf.com.br"
    #pathFTP='PremioReferencia/'
    ftp = ftplib.FTP(ftpAddr)
    ftp.login("anonymous", "ftplib-example-1")

    ftp.cwd(pathFTP)
    # try:
    files = ftp.nlst()
    # except ftplib.error_perm as resp:
    #     if str(resp) == "550 No files found":
    #         print("No files in this directory")
    #     else:
    #         raise
    for f in files:
        fout=pathOut+f

        if not (os.path.isfile(fout) or os.path.isdir(fout)):
            print('Downloading ' + f)
            with open(fout, 'wb') as f_:
                ftp.retrbinary("RETR " + f, f_.write)
        else:
            print(f + ' exists')


    ftp.quit()


def importMktData():
    importFTP('ftp.bmf.com.br', 'MarketData', globalM.dataRoot+'\\b3\\MarketData\\')
    importFTP('ftp.bmf.com.br', 'MarketData/BMF', globalM.dataRoot + '\\b3\\MarketData\\BMF\\')
    importFTP('ftp.bmf.com.br', 'MarketData/Bovespa-Opcoes', globalM.dataRoot + '\\b3\\MarketData\\Bovespa-Opcoes\\')
    importFTP('ftp.bmf.com.br', 'MarketData/Bovespa-Vista', globalM.dataRoot + '\\b3\\MarketData\\Bovespa-Vista\\')

def importOthersB3():

    paths=['ContratosPregaoAjuste/','ContratosPregaoFinal/','ContratosPregaoAtualizado/','BdDocs/','BdDocs2/','BdDocs3/','SuperficiesVolatilidade/']
    for p in paths:
        path1=globalM.dataRoot+'\\b3\\' + p
        if not os.path.exists(path1):
            os.makedirs(path1)
        importFTP('ftp.bmf.com.br', p, path1)



def importPremioRef():
    pathOut=globalM.dataRoot+'\\b3\\premio_ref\\'
    #ftppath="ftp://ftp.bmf.com.br/PremioReferencia/"
    ftppath = "ftp.bmf.com.br"
    path1='PremioReferencia/'
    ftp = ftplib.FTP(ftppath)
    ftp.login("anonymous", "ftplib-example-1")

    ftp.cwd(path1)
    # try:
    files = ftp.nlst()
    # except ftplib.error_perm as resp:
    #     if str(resp) == "550 No files found":
    #         print("No files in this directory")
    #     else:
    #         raise
    for f in files:
        fout=pathOut+f

        if not os.path.isfile(fout):
            print('Downloading ' + f)
            with open(fout, 'wb') as f_:
                ftp.retrbinary("RETR " + f, f_.write)
        else:
            print(f + ' exists')


    ftp.quit()



if __name__ == "__main__":
    importBMFAll()



