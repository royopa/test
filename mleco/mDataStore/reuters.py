from py_init import *
from mDataStore.mongo import *
from mDataStore.globalMongo import mds
import re
import gzip

def reutersCorrectDB():

    #dedar type e subtype com planilha

    reutersSplitGenTickerIntoContractsRoutine()
    mds.correctFutRoutine()
    #clearBadTicks
    #util.findBadTicks()

def reutersUpdateRoutine(library=None):
    reutersPath = globalM.dataRoot + '/datascope_csv'
    # _splitCSVreuters()
    for path, subdirs, files in os.walk(reutersPath + '/_input'):
        for f_ in files:
            print('Reuters: processing {}'.format(f_))
            # file1=path+'/'+f_

            # df_ = _readReutersCSVtoDF(file1)
            importFromReutersCSV(path + '/', f_, reutersPath + '/done/',library=library)
            # for nm in df_:
            #     self.write(df_[nm],check_metadata=False,keep_metadata=True)
            # file1_done=reutersPath+'/done/'+f_
            # os.rename(file1, file1_done)



def reutersSplitGenTickerIntoContractsRoutine(genTickers=['DIJc{}'.format(i+1) for i in range(38)],
                                              dt0=dt(2000,1,1),freq='6MS',library=mds.assetTS):

    dts=pd.date_range(dt0,dt.now(),freq=freq,closed='left')
    dts=dts.append(pd.DatetimeIndex([dt.now()]))

    uCode0 = []
    for t,dt1 in enumerate(dts[1:]):
        dt0_=dts[t]

        dfs = mds.read(genTickers,f.second,library,date_range=[dt0_,dt1])
        df1=pd.concat(dfs,0)
        if df1.shape[0]==0:
            continue
        print('dt: {}'.format(dt0_))
        df1=df1.rename(columns={'close': 'yield_close', 'ask': 'yield_bid', 'bid': 'yield_ask'})
        uCode = pd.unique(df1.underlying)

        #rename for 2 digits
        for i,code1 in enumerate(uCode):
            match = re.match(r"([a-z]+)([0-9]+)", code1, re.I)
            items = match.groups()
            if len(items[1])==1:#1 digit
                try:
                    mds.delete(code1,f.second,library)
                except:
                    pass
                dig = 1 * (dt0_.year - 2000 - int(items[1][-1]) > 2)
                newCode = items[0][:-1] + items[0][-1]+dig.__str__() + items[1][-1]
                df1.underlying.loc[df1.underlying==uCode[i]]=newCode
                uCode[i]=newCode
                #year1 = 2000 + int(match[2])


        #delete previous data
        for nm1 in uCode:
            if nm1 not in uCode0:
                try:
                    mds.delete(nm1,f.second,mds.assetTS)
                except:
                    pass
            uCode0.append(nm1)
        updateAllContracts(df1)

def classifyTypesIntraday(library='assetTS'):
    '''
    Classify intraday types and subtypes series in assetTS. Reuters routine do not make such
    classification.
    :return:
    '''
    lib = getattr(mds,library)
    meta1 = mds.find(library=lib)
    for m in meta1:
        m=m[2]
        if '.SA' in m.name:
            m.type='equity'
            m.subtype = 'equity_nadj'
        elif 'c1' in m.name or 'c2' in m.name:
            m.type='future'
            m.subtype = 'fut_nrol'

        mds.write_metadata(m,library=lib)

def updateAllContracts(df1):
    uCode=pd.unique(df1.underlying)

    monthCodes = array(['F', 'G', 'H', 'J', 'K', 'M', 'N', 'Q', 'U', 'V', 'X', 'Z'])
    for i,code1 in enumerate(uCode):
        df_ = mDataFrame(df1.loc[df1.underlying==code1].copy())
        del df_['underlying']
        df_=df_.astype(float64)
        match = re.match(r"([a-z]+)([0-9]+)", code1, re.I)
        assert(match)
        month1=where(monthCodes==match[1][-1])[0][0]+1
        year1=2000+int(match[2])
        mat1 = dt(year1,month1,1)
        if not df_.index.tz:
            df_.index = df_.index.tz_localize(pytz.timezone('GMT'))  # Brazil/East

        md1 = mds.read_metadata(code1,f.second,mds.assetTS)
        if md1:
            tz=pytz.timezone('GMT')
            stDT=minimum(df_.index[0].to_pydatetime(),tz.localize(md1.stDT))
        else:
            stDT =df_.index[0].to_pydatetime()
        df_.md = metadataAsset(code1,'future',stDT,fut_like=True,
                               maturity=mat1,freq=f.second)

        df_.md.subtype = 'di_fut_intraday'

#        print('appending {}.  {}/{}'.format(code1,i,len(uCode)))
#        print('appending {}.  {}/{}'.format(code1,i,len(uCode)))

        if not df_.index.is_unique:
            df_=uu.drop_duplicates_index(df_)

        # try:
        #     mds.delete(code1,f.second,mds.assetTS)
        # except:
        #     pass
        mds.append(df_,mds.assetTS,check_metadata=False)





def importFromReutersCSV(inputPath,file1,outPath,columns=None,chunksize=4*2**20,library=None):
    #reutersPath = globalM.dataRoot + '/datascope_csv'
    with gzip.open(inputPath+file1) as f_:
        for i,srs in enumerate(pd.read_csv(f_,chunksize=chunksize)):

    #    reutersPath = globalM.dataRoot+'/datascope_csv'
            print('{} - chunk {}'.format(file1,i))
            dt1 = pd.to_datetime(srs['Date-Time'], format='%Y-%m-%dT%H:%M:%S.%fZ')
            srs['Date-Time'] = dt1
            type1 = pd.unique(srs.Type)
            del srs['Domain']
            del srs['Type']

            if not columns is None:
                srs.columns = columns
            else:
                srs = srs.rename(columns={'#RIC': 'code', 'Date-Time': 'dt', 'GMT Offset': 'gmt_off',
                                          'Close Bid': 'bid', 'Close Ask': 'ask', 'Last': 'close', 'Volume': 'volume',
                                          'Alias Underlying RIC': 'underlying'})
            #            srs.rename(columns={'code', 'underlying', 'dt', 'gmt_off'})
            # srs.columns.values[:4] = ['code', 'underlying', 'dt', 'gmt_off']

            srs.gmt_off = srs.gmt_off.astype(int)
            # delta1 = pd.to_timedelta(srs.gmt_off, unit='h')
            # srs.dt = srs.dt + delta1

            codes = pd.unique(srs.code)
            out = Dict()
            fr = {'Intraday 5Sec': f.second5, 'Intraday 1Sec': f.second}
            for code in codes:
                out[code] = mDataFrame(srs[srs.code == code].iloc[:, 1:].set_index('dt'))
                out[code].md = metadataAsset(code, 'equity', freq=fr[type1[0]])

            for nm in out:
                # if not mds.read_metadata(out[nm].md.name,out[nm].md.freq,mds.assetTS):
                out[nm].index=out[nm].index.tz_localize(pytz.timezone('GMT'))
                mds.append(out[nm],check_metadata=False,keep_metadata=True,library=library)
    file1_done=outPath+file1
    os.rename(inputPath+file1, file1_done)


def _splitCSVreuters():
    reutersPath = globalM.dataRoot + '/datascope_csv/_input'
    L=100*2**20 #100 mb
    for path, subdirs, files in os.walk(reutersPath):
        for f_ in files:
            f1_=path+'/'+f_
            sz=os.path.getsize(f1_)
            if sz > L:
                L=L*10
                n=int(np.ceil(sz/L))
                i=0
                with gzip.open(f1_, 'rb') as inp:
                    while True:
                        print('Splitting {}:{}'.format(f_,i))
                        outslice=path+'/{}_'.format(i)+f_
                        i+=1
                        chunk=inp.read(L)
                        if chunk == b'':
                            break
                        with gzip.open(outslice, 'wb') as outp:
                            outp.write(chunk)
                    # else:
                    #     outslice=path+'/{}_'.format(n+1)+f_
                    #     with gzip.open(outslice, 'wb') as outp:
                    #         outp.write(inp.read())


                os.remove(f1_)




def _readReutersCSVtoDF(file,columns=None):
    with gzip.open(file) as f_:
        srs = pd.read_csv(f_)

#    reutersPath = globalM.dataRoot+'/datascope_csv'

    dt1 = pd.to_datetime(srs['Date-Time'], format='%Y-%m-%dT%H:%M:%S.%fZ')
    srs['Date-Time'] = dt1
    type1=pd.unique(srs.Type)
    del srs['Domain']
    del srs['Type']

    if not columns is None:
        srs.columns = columns
    else:
        srs=srs.rename(columns={'#RIC': 'code', 'Date-Time': 'dt', 'GMT Offset': 'gmt_off',
                            'Close Bid':'bid','Close Ask':'ask','Last':'close','Volume':'volume','Alias Underlying RIC':'underlying'})
#            srs.rename(columns={'code', 'underlying', 'dt', 'gmt_off'})
            #srs.columns.values[:4] = ['code', 'underlying', 'dt', 'gmt_off']

    srs.gmt_off = srs.gmt_off.astype(int)
    #delta1 = pd.to_timedelta(srs.gmt_off, unit='h')
    #srs.dt = srs.dt + delta1

    codes=pd.unique(srs.code)
    out=Dict()
    fr={'Intraday 5Sec':f.second5,'Intraday 1Sec':f.second}
    for code in codes:
        out[code]=mDataFrame(srs[srs.code==code].iloc[:,1:].set_index('dt'))
        out[code].md=metadataAsset(code,'equity',freq=fr[type1[0]])

    #srs[nm].to_pickle(pyRoot + '/obj/' + srsInfo[nm].pickle)
    return out

from mDataStore.mongo import convertFreq
#
# def convertFreq(df1,freq=ds.freqHelper.minute15,h_interval=None):
#     from copy import deepcopy
#
#     df1.index = uu.x2dti_date(df1.index)
#     freqPD=freq.lower().replace('minute','min').replace('second','sec')
#     df2=pd.DataFrame(index=df1.index.to_series().resample(freqPD, label='left').last().index)
#     # df2=df2.asfreq(freqPD)
#     # df2 = pd.DataFrame(index=df1.index).asfreq(freqPD)
#
#     print('close..', end='')
#     if 'close' in df1:
#         df2['close'] = pd.DataFrame(df1.close.resample(freqPD, label='left').last())
#
#     if 'yield_close' in df1:
#         df2['yield_close'] = pd.DataFrame(df1.yield_close.resample(freqPD, label='left').last())
#
#     if 'alpha_close' in df1:
#         df2['alpha_close'] = df1.alpha_close.resample(freqPD, label='left').last()
#
#     print('open..', end='')
#     if 'open' in df1:
#         df2['open'] = df1.open.resample(freqPD, label='left').first()
#     elif 'close' in df1:
#         df2['open'] = df1.close.resample(freqPD, label='left').first()
#
#     print('high..', end='')
#     if 'high' in df1:
#         df2['high'] = df1.high.resample(freqPD, label='left').max()
#     elif 'close' in df1:
#         df2['high'] = df1.close.resample(freqPD, label='left').max()
#
#     print('low..', end='')
#     if 'low' in df1:
#         df2['low'] = df1.low.resample(freqPD, label='left').min()
#     elif 'close' in df1:
#         df2['low'] = df1.close.resample(freqPD, label='left').min()
#
#     print('vwap..', end='')
#     if 'vwap' in df1:
#         px_vwap=df1.vwap
#     else:
#         if 'close' in df1:
#             px_vwap=df1.close
#         elif 'yield_close' in df1:
#             px_vwap=df1.yield_close
#         else:
#             px_vwap = None
#
#     print('volume..', end='')
#     if 'volume' in df1:
#         df2['volume'] = df1.volume.resample(freqPD, label='left').sum()
#         if not px_vwap is None:
#             df2['vwap'] = (px_vwap*df1.volume).resample(freqPD, label='left').sum()
#             vol1=((~px_vwap.isna())*df1.volume).resample(freqPD, label='left').sum()
#             df2['vwap'] = df2['vwap']/vol1
#     else:
#         if not px_vwap is None:
#             df2['vwap'] = px_vwap.resample(freqPD, label='left').mean()
#
#     print('bid..', end='')
#     if 'bid' in df1:
#         df2['bid'] = df1.bid.resample(freqPD, label='left').last()
#
#     if 'yield_bid' in df1:
#         df2['yield_bid'] = pd.DataFrame(df1.yield_bid.resample(freqPD, label='left').last())
#
#     print('ask..', end='')
#     if 'ask' in df1:
#         df2['ask'] = df1.ask.resample(freqPD, label='left').last()
#
#     if 'yield_ask' in df1:
#         df2['yield_ask'] = pd.DataFrame(df1.yield_ask.resample(freqPD, label='left').last())
#
#     # df2=df2.between_time('9:00','18:00')
#
#     if not h_interval is None:
#         df2 = df2.between_time(h_interval[0], h_interval[1])
#
#     II=df2.index.normalize().isin(df1.index.normalize())
#     df2=df2.loc[II]
#
#     print('dropna..', end='')
#     if 'close' in df1:
#         # df2.close=df2.close.fillna(method='ffill')
#         df2 = df2.dropna(subset=['close','bid','ask'],how='all')
#     if 'alpha_close' in df1:
#         df2.alpha_close=df2.alpha_close.fillna(method='ffill')
#
#     df2.md=deepcopy(df1.md)
#     df2.md.freq = freq
#     print('done convert..')
#     return df2

def fixTSAll():
    from arctic.date import DateRange
    bkLib = mds.arctic.get_library('assetTS_bk')
    names=bkLib.list_symbols()
    names = [nm.replace('_1Second','') for nm in names if '1Second' in nm]
    assetBase=mds.findAsset(freq=ds.freqHelper.second,library=mds.assetTS)
    date_range0 = [dt(2000,1,1,0,0,0),dt.now()]
    dts = pd.date_range(date_range0[0],date_range0[-1],freq='1YS',normalize=False)
    dts=dts.append(pd.DatetimeIndex([date_range0[-1]]))
    dts=dts.tz_localize('GMT')

    for i,dt0 in enumerate(dts[:-1]):
        date_range=[dt0.to_pydatetime(),dts[i+1].to_pydatetime()]
        for i,name in enumerate(names):
            print('fix {}. {}/{}'.format(name,i,len(names)))
            # if name != 'ESc1':
            #     continue
            try:
                # df1 = mds.read(name,ds.freqHelper.second,mds.assetTS,date_range=date_range)
                id=name+'_'+ds.freqHelper.second
                df = ds.mDataFrame(bkLib.read(id,date_range=DateRange(date_range[0], date_range[1])))
                meta1 = bkLib.read_metadata(id)
                df.md = locate(meta1['cls'])(meta1)

                #mutreta para converter duas vezes. O ajuste esta errado na base. Eh necessario refazer a base
                tzG = pytz.timezone('GMT')
                df.index=df.index.tz_convert(tzG)
                df.index = df.index.tz_localize(None,ambiguous='infer',errors ='coerce').tz_localize(pytz.timezone('America/Sao_Paulo'),ambiguous='infer',errors ='coerce')
                df=df.loc[df.index.notnull()]
                df.index=df.index.tz_convert(tzG)


            except:
                print('unable to read {} - dt {}->{}'.format(name, date_range[0], date_range[1]))
                continue
            mds.write(df,mds.testTS)


# def convertFreqAll(freq=ds.freqHelper.minute,freqBase=ds.freqHelper.second):
#     assetBase=mds.findAsset(freq=freqBase,library=mds.assetTS)
#     if not isinstance(freq,list):
#         freq=[freq]
#     for i,name in enumerate(assetBase.name):
#         print('starting {} . {}/{}'.format(name,i,len(assetBase.name)))
#         df = mds.read(name,freqBase,mds.assetTS,date_range=[dt(2000, 1, 1), dt(2050, 6, 1)],tz='GMT')
#         for f in freq:
#             df1=convertFreq(df, f)
#             try:
#                 mds.delete(df1.md.name,f,mds.assetTS)
#             except:
#                 pass
#             df = mds.write(df1,mds.assetTS)


def convertAllParallel(freq=ds.freqHelper.minute,freqBase=ds.freqHelper.second):
    # import multiprocessing
    # pool = multiprocessing.Pool(4)
    # from dask.distributed import Client,wait
    # client = Client(processes=False)
    # client = Client(processes=False)

    assetBase=mds.findAsset(freq=freqBase,library=mds.assetTS)

    date_range0 = [dt(2000,1,1,12,0,0),dt.now()]
    dts = pd.date_range(date_range0[0],date_range0[-1],freq='1YS',normalize=False)
    dts=dts.append(pd.DatetimeIndex([date_range0[-1]]))
    dts=dts.tz_localize('GMT')
    # dts=dts.tolist()
    # dts.append(date_range0[-1])
    for i,dt0 in enumerate(dts[:-1]):
        date_range=[dt0.to_pydatetime(),dts[i+1].to_pydatetime()]

        # def convertOne1(i):
        #     return convertOne(i,assetBase,mds,date_range,freq=freq,freqBase=freqBase)
        # convertOne1=lambda i:convertOne(i,assetBase,mds,date_range,freq=freq,freqBase=freqBase)
        futs=[]
        for j in range(len(assetBase.name)):
            # futs.append(client.submit(convertOne,j,assetBase,date_range,freq,freqBase))
            # if assetBase.name[j]!='ESc1':
            #     continue
            convertOne( j, assetBase, date_range, freq, freqBase,firstRun=i==0)

        # wait(futs)
        # pool.map(convertOne1, range(len(assetBase.name)))

def convertOne(i,assetBase,date_range,freq=ds.freqHelper.minute,freqBase=ds.freqHelper.second,firstRun=False):
    from mDataStore.globalMongo import mds
    name=assetBase.name[i]

    #################### REMOVE THIS ##########################3
    # if firstRun:
    #     try:
    #         mds.delete(name, freq, mds.assetTS)
    #     except:
    #         pass
    ##########################################################3

    print('starting {} . {}/{}'.format(name,i,len(assetBase.name)))
    try:
        df1=mds.read(name,freq,mds.assetTS,date_range=date_range)
        print('Already Done!')
        return
    except:
        pass

    try:
        df = mds.read(name,freqBase,mds.assetTS,date_range=date_range,tz='GMT')
    except:
        print('unable to read {} - dt {}->{}'.format(name,date_range[0],date_range[1]))
        return

    df1=convertFreq(df, freq)
    df = mds.write(df1,mds.assetTS)

def reutersFreqRoutine():
    f=ds.freqHelper
    convertAllParallel(freq=f.minute, freqBase=ds.freqHelper.second)
    convertAllParallel(freq=f.minute10, freqBase=ds.freqHelper.minute)



def convertFreqAll_old(freq=ds.freqHelper.minute15):
    from strategy import asset

    futRolTKs=['DOL','IND','ES','TY']
    #treasury is in fact US/Centrall tz.
    #in fact both are roughly 24hours, but I am getting the most liquid market time.
    tzs=['America/Sao_Paulo','America/Sao_Paulo','US/Eastern','US/Eastern']
    #['9:30','16:15'] is the ET time for the S&P big congtract
    # trading_hours=[['9:00','18:00'],['9:00','18:00'],['7:30','16:15'],['7:30','16:15']]

    for i,tk in enumerate(futRolTKs):
        md = mds.read_metadata(tk+'c1',ds.freqHelper.second,mds.assetTS)
        df0 = feeder.get([tk+'c1', tk+'c2'], freq=ds.freqHelper.second, date_range=[dt(2000, 1, 1), dt(2215, 1, 1)],tz=tzs[i])
        a = asset(feederCollection(df0))
        df1 = a._mdf.copy()
        df2=convertFreq(df1,freq,trading_hours[i])
        df2.md.name=tk+'r1'
        df2.md.subtype = 'fut_rol'
        df2.md.freq=freq
        mds.write(df2, mds.assetTS)


if __name__ == '__main__':
    # fixTSAll()
    # reutersFreqRoutine()
    reutersUpdateRoutine(mds.assetTS)
    classifyTypesIntraday(library='assetTS')
    reutersSplitGenTickerIntoContractsRoutine(library='assetTS')


    # df=df2
    # df.md=dol[0].md
    # df.md.subtype = 'fut_rol'
    # uu.save_obj(df,'tst_dol')


