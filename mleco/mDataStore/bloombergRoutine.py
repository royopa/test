from py_init import *
import globalM
globalM.loadBLP = True
from mDataStore.globalMongo import mds
import mDataStore.bloomberg as bloomberg
import time
# import mUtil as uu
import socket
from copy import copy, deepcopy
# from datetime import datetime as dt
from tqdm import tqdm

import logging
from mDataStore.util import LogController

try:
    from mDataStore.globalBlp import blp
except:
    from mDataStore.globalRBlp import blp

from mDataStore import metadataAsset,metadataFundamental

def stripTb(df):
    df_obj = df.select_dtypes(['object'])
    df[df_obj.columns] = df_obj.apply(lambda x: x.str.strip())
    return df


def upsert_meta_from_xl(replaceMeta=True):
    """
    Read metadata info from a excel worksheet.
    :return: Dictionary with consolidated data read.
    """
    # mark starting time
    start = dt.now()

    path = globalM.dataRoot + '/metadata.xlsx'
    # open worksheet
    xl1 = pd.read_excel(path, ['meta','intra','field_hist','field_ref'])

    # read asset info for historical data
    meta_table=stripTb(xl1['meta']).set_index('name')

    meta_table.index = pd.Index(pd.Series(meta_table.index).str.replace(' ', ''))

    # read asset info for intraday data
    intra_table = stripTb(xl1['intra']).set_index('name')
    #
    field_hist=stripTb(xl1['field_hist']).set_index('name').fillna('')
    field_ref=stripTb(xl1['field_ref']).set_index('name').fillna('')

    upsert_fields(field_hist,db=mds.mongoCli.db_dws.mgmt.field_hist)
    upsert_fields(field_ref, db=mds.mongoCli.db_dws.mgmt.field_ref)
    return upsert_meta(meta_table, intra_table,replaceMeta=replaceMeta)

    # join read data into a dictionary


def upsert_fields(field_hist,db):
    col = field_hist.columns
    for i in range(field_hist.shape[0]):
        doc={}
        doc['name']=field_hist.index[i]
        flds=[f for f in col if 'fields' in f.lower()]
        flds1=list(field_hist[flds].iloc[i].values)
        doc['field'] = [f for f in flds1 if isinstance(f,str) and len(f)>0]

        outs=[f for f in col if 'out' in f.lower()]
        outs1=list(field_hist[outs].iloc[i].values)
        doc['out'] = [f for f in outs1 if isinstance(f,str) and len(f)>0]
        if 'options' in field_hist:
            doc['options']=field_hist['options'].iloc[i]
        assert(len(doc['out'])==len(doc['field']))

        r=db.replace_one(dict(name=doc['name']),doc,upsert=True)
        if r.raw_result['ok'] != 1:
            raise Exception('UNABLE TO UPSERT field hist {}'.format(doc['name']))

from mUtil import cast_types2basic


def mapClsFromLibrary(lib):
    libs=pd.Series([metadataAsset, metadataFundamental],index=['assetVS','fundamentalVS'])
    cls =libs.loc[lib]
    return cls.__module__ +'.'+cls.__name__

def upsert_meta(hist_table, intra_table, replaceMeta=True):
    db = mds.mongoCli.db_dws.mgmt.metadata
    meta = []

    req_fields = pd.Index(['type', 'subtype', 'library', 'is_fut', 'currency', 'multiplier'])
    for i in range(hist_table.shape[0]):
        doc={}
        doc['name'] = hist_table.index[i]
        r=hist_table.iloc[i]

        r=r.map(lambda x: nan if (isinstance(x,str) and x=='') else x)
        r=r[~r.isna()]
        rdict=r.to_dict()
        if not 'maturity' in rdict or isinstance(rdict['maturity'],str):
            rdict['maturity']=None

        if not replaceMeta:
            assert('library' in rdict)
            current = db.find_one(dict(name=doc['name'], library=rdict['library']))
            if not current is None:
                doc.update(current)

        doc.update( rdict)

        if doc['name'] in intra_table.index:
            doc_intra=intra_table.loc[doc['name']].to_dict()
            doc.update(doc_intra)

            I = req_fields.isin(doc.keys())
            if not I.all():
                raise Exception('Missing data for {}:{}'.format(doc['name'], req_fields[~I]))

        doc['cls'] = mapClsFromLibrary(doc['library'])

        cast_types2basic(doc)

        meta.append(doc)
        r=db.replace_one(dict(name=doc['name'],library=doc['library']),doc,upsert=True)

        if r.raw_result['ok'] != 1:
            raise Exception('UNABLE TO UPSERT meta {}'.format(doc['name']))



    return meta
# def insert_meta()
# def filterMeta(srsMeta,I,key1):
#     from copy import deepcopy
#     srsMeta1 = deepcopy(srsMeta)
#     # for k,v in srsMeta.items():
#     srsMeta1[key1]=srsMeta1[key1][I]
#     return srsMeta1

def bloombergUpdateHistory(meta,field_hist,dti, overwrite=False,doParallel=True,
                    prune_previous_version=True,dtm1=None,dtm3=None,c = None,initial=False,keep_metadata=False,maxQuery=64):
    from mDataStore import mDataFrame, metadataFundamental, metadataOption, metadataAsset, metadataIndicator, \
        metadataStrategy


    from dask.distributed import Client
    if doParallel:
        try:
            c = Client()
        except:
            c = None
    else:
        c=None

    if dtm1 is None:
        import pytz
        tz = pytz.timezone('GMT')
        dtm1=(dt.now()-datetime.timedelta(1)).replace(hour=0, minute=0, second=0, microsecond=0)
        # dtm1=tz.localize(dtm1)
    if dtm3 is None:
        dtm3 = (dt.now()-datetime.timedelta(3)).replace(hour=0, minute=0, second=0, microsecond=0)

    success={}

    dt_min = dt.today()-datetime.timedelta(days=80)

    meta0 = [m for m in meta if 'feeder_id' in m and isinstance(m['feeder_id'],str) and m['feeder_id'] !='']
    ###
    for i,fh in enumerate(field_hist):

        if initial:
            meta1 = array([m for m in meta0 if 'field_hist' in m and m['field_hist']==fh ])
        else:
            #exclude series whose maturity is before dti and that have endDT and it is before the minimum thresh (dt_min)
            meta1 = array([m for m in meta0 if ('field_hist' in m and m['field_hist']==fh)
                           and (not ('endDT' in m and not m['endDT_assetVS'] is None and m['endDT'] < dt_min))
                           and (not ('maturity' in m and not m['maturity'] is None and dti>m['maturity']))])

        if len(meta1) ==0:
            continue

        N = int(np.ceil(len(meta1)/maxQuery))

        fields1 = array(field_hist[fh]['field'])
        options1 = field_hist[fh]['options']
        out1 = array(field_hist[fh]['out'])

        for k in tqdm(range(N)): #tqdm
            meta1a = meta1[k*maxQuery:(k+1)*maxQuery]
            II = np.array([True if not m['feeder_id'] is None else False for m in meta1])
            if any(~(II)):
                warn('tickers missing')
                meta1a = meta1a[II]

            if len(meta1a) == 0:
                continue

            feeder_id=array([m['feeder_id'] for m in meta1a])
            df1 = blp.getHistoricData(feeder_id, fields1, dti, dtm1,**eval('dict('+options1+')'))
            # desc1 = blp.getRefData(feeder_id, desc)

            for i,df0 in enumerate(df1):
                df1[i]=df1[i].rename(columns=dict(zip(fields1,out1)))
                df1[i]=mDataFrame(df1[i])
                md1=copy(meta1a[i])
                df1[i].md=metadataAsset(**md1)
                # a=1
                # df1[i].md.stDT = df1[i].index[0]
                # df1[i].md.endDT = df1[i].index[-1]
            if c is not None:
                addr = mds.mongoCli.address[0]+':'+str(mds.mongoCli.address[1])
                fut = {}
                for l, df in enumerate(df1):
                    fut[df.md.name] = c.submit(insert2DB, False, df,df.md['library'], addr, overwrite, prune_previous_version,
                                        dti, dtm1, dtm3,keep_metadata)
                for i,f in enumerate(fut):
                    success[f] = fut[f].result()

            else:
                # addr =
                for l, df in enumerate(df1):
                    success[df.md.name] = insert2DB(True, df,df.md.library, mds,  overwrite, prune_previous_version, dti, dtm1, dtm3,keep_metadata)


    return [k for k in success if not success[k]]


def insert2DB(serial, df, library1,mds_or_addr, overwrite, prune_previous_version,  dti, dtm1, dtm3,keep_metadata=False):

    # stDT=None,endDT=None, currency='BRL', fut_like=False,maturity=None
    # from mDataStore.globalMongo import mds

    from mDataStore.mongo import mongoDS,metadataAsset,mDataFrame

    if serial:
        mds = mds_or_addr
    else:
        from dask.distributed import get_worker
        worker = get_worker()
        if not hasattr(worker, 'mds'):
            worker.mds = mongoDS(mds_or_addr)
        mds = worker.mds

    # removal of success flag (unnecessary) - sxan-20190926

    if df.shape[0] == 0:
        warn(df.md.name + ': No data')
        mds.mongoCli.db_dws.mgmt.metadata.remove(dict(name=df.md.name,library=library1))
        return True

    # library1=df['library']
    # library1=df.md.pop('library')
    if overwrite:
        for s in df.columns:
            if df[s].dtype in [np.float32,np.float64] and np.all(np.isnan(df[s])):
                del df[s]

        mds.write(df, library=library1, check_metadata=False, prune_previous_version=prune_previous_version)
        return True

    else:
        return mds.appendIfCheck(df, date_range=[dti, dtm1], library=library1, check_metadata=False,
                                     prune_previous_version=prune_previous_version, replaceIntersection=True,
                                     lastChkDate=dtm3,keep_metadata=keep_metadata
                                 )


def bloombergUpdateIntraday(meta, dti, bOnlyUpdateMetadata=False, srsMeta=None, overwrite=False,
                            dtm1=None, onlineTS='onlineTS',keep_metadata=False):
    
    from mDataStore import mDataFrame, metadataFundamental, metadataOption, metadataAsset, metadataIndicator, \
        metadataStrategy

    meta1 = [m for m in meta if 'feeder_id_intraday' in m]
    N=len(meta1)
    if dtm1 is None:
        import pytz
        tz = pytz.timezone('GMT')
        dtm1 = (dt.now()-datetime.timedelta(1)).replace(hour=0, minute=0, second=0, microsecond=0)


    # success = np.full(hist1.shape[0], True)
    lst_failures=[]
    for k in tqdm(range(N)): #tqdm(

        # nfreq, sfreq = mongo.splitFreq(meta1[k]['freq_intraday'])


        interval = 1#nfreq
        #
        # if currency1[k] is None:
        #     # try:
        #     #     currency = desc1.CRNCY[feeder_id[k]]
        #     # except:
        #     currency = 'BRL'
        # else:
        #     currency = currency1[k]

        if not 'options_intraday' in meta1[k] or not isinstance(meta1[k]['options_intraday'], str) or meta1[k]['options_intraday']=='':
            options = {}

        else:
            options = eval('dict('+meta1[k]['options_intraday']+')')
        # get output columns
        md=copy(meta1[k])
        md['freq']='1Minute'
        md = metadataAsset(**md)
        library1 = 'assetTS2'#md.pop('library')
        if 'stDT' in md:
            md.pop('stDT')
        if 'endDT' in md:
            md.pop('endDT')

        mt_ant = mds.read_metadata(md['name'],'1Minute',library1)
        if mt_ant and 'endDT' in mt_ant and dti > mt_ant['endDT']:
            dti=pd.Timestamp(mt_ant['endDT']).normalize().to_pydatetime()

        df = blp.getIntradayHistoricDataBA(md.feeder_id_intraday, interval, dti, dt.now(), md, **options)
        if df.shape[0] == 0:
            continue

        # df.md.stDT = df.index[0]
        # df.md.endDT = df.index[-1]
        # if overwrite:
        #     for s in df.columns:
        #         if (df[s].dtype == np.float) and np.all(np.isnan(df[s])):
        #             del df[s]
        #
        #     # lst=mds.find(df.md.name, df.md.freq, library=library1[k])
        #     att = df.md.name + '_' + df.md.freq
        #     exists = att in getattr(mds, library1).list_symbols()
        #     if exists:
        #         mds.delete(df.md.name, df.md.freq, library=library1)
        #
        #     mds.write(df, library=library1, check_metadata=False)
        #     # mds.write(df, library=onlineTS, check_metadata=False)
        #
        #     successi = True
        #
        # else:
        try:
            mds.append(df,date_range=[dti, dtm1],  library=library1, check_metadata=False,keep_metadata=keep_metadata,
                       replaceIntersection=overwrite)
            successi=True
        except:
            try:
                mds.append(df, date_range=[dti, dtm1], library=library1, check_metadata=False, replaceIntersection=True,
                           keep_metadata=keep_metadata)
            except:
                successi=False

            # mds.append(df, date_range=[dti, dtm1], library=onlineTS, check_metadata=False, replaceIntersection=True,keep_metadata=True)

        if not successi:
            lst_failures.append(df.md.name)

    return lst_failures



# def bloombergInitialRoutine():
# 
#     srsMeta = get_meta_to_insert()
#     # uu.save_obj(srsMeta,'srsMeta')
#     # srsMeta = uu.load_obj('srsMeta')
# 
#     from mDataStore.globalMongo import mds
#     dti = dt(1910, 1, 1)
# 
#     print('BLOOMBERG HISTORY ROUTINE - INITIAL')
#     success = bloombergUpdateHistory(mds, dti, srsMeta=srsMeta, overwrite=True, initial=True, insertInThreads=True)
#     assert(all(success))
# 
#     print('FUTURES DATES')
#     bloombergUpdateFutureLastDates(srsMeta=srsMeta)
# 
#     dti = dt(2015, 1, 1)
#     print('BLOOMBERG INTRADAY ROUTINE - INITIAL')
#     success=bloombergUpdateIntraday(mds,dti,srsMeta=srsMeta,overwrite=True)
#     assert(all(success))
# 
    # print('BLOOMBERG OVERRIDE ROUTINE - INITIAL')
    # success=bloombergUpdateOverride(mds,dti,srsMeta=srsMeta,overwrite=True)
    # assert(all(success))
def bloombergUpdateFutureLastDates(meta):

    # assert srs_meta is not None

    from mDataStore.mongo import metadataFundamental
    from mDataStore.globalMongo import mds
    from mDataStore.mongo import mDataFrame

    # tb = srs_meta['intra_table']
    # tb = tb[tb.subtype == 'fut_rol']

    meta1 = [m for m in meta if m['subtype']=='fut_rol' and 'feeder_id' in m]

    for i,m in enumerate(tqdm(meta1)):

        df1 = blp.getRefData([m['feeder_id']], ['FUT_CHAIN_LAST_TRADE_DATES'], {"INCLUDE_EXPIRED_CONTRACTS": "Y"})
        if df1.shape[0]==0:
            continue
        aa = np.array(df1.iloc[0, 0])
        df_ = mDataFrame(aa[1:], columns=aa[0])
        df_.md = metadataFundamental(m['name'].lower()+'_dates', type='futureLastTradeDate')

        mds.write(df_, library=mds.fundamentalVS, check_metadata=False, prune_previous_version=True)

# def bloombergUpsert():
#     db_m = mds.mongoCli.db_dws.mgmt.metadata
#     db_fh=mds.mongoCli.db_dws.mgmt.field_hist
#     db_fref=mds.mongoCli.db_dws.mgmt.field_ref
#     
#     upsert_meta()


def setLogging(nm):
    LogController.configure(globalM.dataRoot, nm)
    # set a higher level for arctic.tic logging
    flaskLogger = logging.getLogger('arctic.tic')
    flaskLogger.setLevel(logging.ERROR)
    flaskLogger = logging.getLogger('arctic.serialization')
    flaskLogger.setLevel(logging.ERROR)

def bloombergUpdateMetadata():
    setLogging("bloombergUpdateMetadata")
    upsert_meta_from_xl(replaceMeta=False)


def bloombergInsertRoutine():

    setLogging("bloombergInsertRoutine")

    db_fh=mds.mongoCli.db_dws.mgmt.field_hist
    db_fref=mds.mongoCli.db_dws.mgmt.field_ref
    meta = upsert_meta_from_xl()

    field_hist,field_ref=getFields()

    bloombergUpdateMetaFromBLP(meta, field_ref,updateAll=True)

    bloombergUpdateHistAndIntra(meta, field_hist,doHistParallel=False,initial=True)


def bloomberg_insert_routine_with(meta_table, intra_table, replace_meta):

    meta = upsert_meta(meta_table, intra_table, replaceMeta=replace_meta)

    field_hist, field_ref = getFields()

    bloombergUpdateMetaFromBLP(meta, field_ref, updateAll=True)

    bloombergUpdateHistAndIntra(meta, field_hist, doHistParallel=False, initial=True)

def getFields():
    db_fh=mds.mongoCli.db_dws.mgmt.field_hist
    db_fref=mds.mongoCli.db_dws.mgmt.field_ref
    field_hist = list(db_fh.find())
    field_hist = dict(zip([fh['name'] for fh in field_hist],field_hist))

    field_ref = list(db_fref.find())
    field_ref = dict(zip([fref['name'] for fref in field_ref],field_ref))

    return field_hist,field_ref

def bloombergUpdateRoutine():
    setLogging("bloombergUpdateRoutine")

    db_m = mds.mongoCli.db_dws.mgmt.metadata
    field_hist, field_ref = getFields()

    meta = list(db_m.find({'library': {'$in': ['assetVS', 'fundamentalVS']}, 'feeder_id': {'$exists': True}}))
    bloombergUpdateMetaFromBLP(meta, field_ref, updateAll=False)

    field_hist,field_ref=getFields()

    # bloombergUpdateFutureLastDates(meta)

    bloombergUpdateHistAndIntra(meta, field_hist, initial=False, doHistParallel=False, lookback_intervalD = 15,
                                lookback_intervalIntra=5)


def bloomberg_update_from_list(tickers):

    db_m = mds.mongoCli.db_dws.mgmt.metadata
    field_hist, field_ref = getFields()

    meta = [db_m.find_one({ "name": t}) for t in tickers]

    bloombergUpdateMetaFromBLP(meta, field_ref, updateAll=False)

    field_hist, field_ref = getFields()

    bloombergUpdateHistAndIntra(meta, field_hist, initial=False, doHistParallel=False, lookback_intervalD=15,
                                lookback_intervalIntra=5)


def bloombergUpdateMetaFromBLP(meta, field_ref,updateAll=False):

    db=mds.mongoCli.db_dws.mgmt.metadata

    for k in field_ref:


        meta1 = [m for m in meta if 'field_ref' in m and m['field_ref']==k and 'feeder_id' in m and m['feeder_id'] != '' and
                 (updateAll or ('in_use' in m and m['in_use'])  )]
        feeder_id0 = [m['feeder_id'] for m in meta1]
        # options1=field_ref[k]['options']
        if len(feeder_id0) == 0 :
            continue
        if 'FUT_CUR_GEN_TICKER' in field_ref[k]['field']:
            feeder_id=blp.getRefData(feeder_id0, ['FUT_CUR_GEN_TICKER'])
            cut_tick=list(feeder_id.reindex(feeder_id0)['FUT_CUR_GEN_TICKER'].values)
            cut_tick = [f if isinstance(f,str) else feeder_id0[i].strip().split(' ')[0] for i,f in enumerate(cut_tick)]
            feeder_id=[c+' '+feeder_id0[i].strip().split(' ')[1] for i,c in enumerate(cut_tick)]

            ii=np.where(np.array(field_ref[k]['field'])=='FUT_CUR_GEN_TICKER')[0]
            field_ref1=copy(field_ref[k]['field'])
            out1=copy(field_ref[k]['out'])

            field_ref1.pop(ii.item())

            for i in range(len(meta1)):
                if feeder_id[i] != feeder_id0[i]:
                    meta1[i][out1[ii.item()]]=feeder_id[i]

            out1.pop(ii.item())


        else:
            feeder_id = feeder_id0
            field_ref1=field_ref[k]['field']
            out1=field_ref[k]['out']

        if len(feeder_id)==0:
            continue

        ref=blp.getRefData(feeder_id,field_ref1) #**eval('dict('+options1+')')

        ref=ref.rename(columns=dict(zip(field_ref1,out1)))
        for i in range(ref.shape[0]):

            try:
                ref1 = ref.loc[feeder_id[i]].to_dict()
            except:
                print('unable to get metadata for {} - feeder return did not match'.format(meta1[i]['name']))
                continue

            meta1[i].update(ref1)

            cast_types2basic(meta1[i])

            doc=meta1[i]
            r = db.replace_one(dict(name=doc['name'], library=doc['library']), doc, upsert=True)
            if r.raw_result['ok'] != 1:
                logging.info('UNABLE TO UPSERT meta from bloomberg {}'.format(doc['name']))


def bloombergUpdateHistAndIntra(meta,field_hist,doHistParallel=True,initial=True,lookback_intervalD = 15,lookback_intervalIntra = 5):

    import pytz

    # mark starting date
    start = dt.now()

    logging.info("Bloomberg update routine - {:%d-%m-%Y}".format(dt.today()))
    ### INTERVAL UPDATE IN DAYS ###

    # update start date - [update_interval] days ago.
    dti0=dt(1910, 1, 1)
    dti_intra0=(dt.now() - datetime.timedelta(200))
    if not initial:
        dti=(dt.now()-datetime.timedelta(lookback_intervalD)).replace(hour=0, minute=0, second=0, microsecond=0) #42 #5
        dti_intra = (dt.now() - datetime.timedelta(lookback_intervalIntra))
    else:
        dti=dti0
        # warn('CHANGE THIS')
        # dti=(dt.now()-datetime.timedelta(lookback_intervalD)).replace(hour=0, minute=0, second=0, microsecond=0) #42 #5
        # dti_intra = (dt.now() - datetime.timedelta(1))
        dti_intra = dti_intra0

    # start date of 5 days ago
    bbg_update_hist(meta, field_hist, dti, dti0, initial, doHistParallel)

    # logging.info("BLOOMBERG INTRADAY DATES")
    # bloombergUpdateFutureLastDates(meta)

    bbg_update_intra(dti_intra, dti_intra0, meta, initial)

    logging.info("[bloombergUpdateRoutine] - Finished - Elapsed time: " + str(dt.now() - start))


def bbg_update_hist(meta, field_hist, dti, dti0, initial, do_parallel):

    logging.info('BLOOMBERG HISTORY ROUTINE - UPDATE since {:%d-%m-%Y}'.format(dti))
    # success = bloombergUpdateHistory(mds, dti0, srsMeta=srs_meta, overwrite=True, c=c)

    failed = bloombergUpdateHistory(meta, field_hist, dti, overwrite=initial, doParallel=do_parallel,
                                    initial=initial)
    # I = success
    # if any(~I):
    if len(failed) > 0:
        meta1 = [m for m in meta if m['name'] in failed]
        failed = bloombergUpdateHistory(meta1, field_hist, dti0, overwrite=True, doParallel=do_parallel,
                                        initial=True)

        logging.info('Blommberg Update History Failed for {}'.format(failed))
    # assert(all(success))


def bbg_update_intra(dti_intra, dti_intra0, meta, initial):

    logging.info("BLOOMBERG INTRADAY ROUTINE - UPDATE since {:%d-%m-%Y}".format(dti_intra))
    failed = bloombergUpdateIntraday(meta, dti_intra, overwrite=initial)
    if len(failed) > 0:
        meta1 = [m for m in meta if m['name'] in failed]
        failed = bloombergUpdateIntraday(meta1, dti_intra0, overwrite=True)
        logging.info('Blommberg Update Intraday Failed for {}'.format(failed))
    else:
        logging.info('Blommberg Update Intraday - sucessfully updated.')



def copyMetadata2Global(library):
    from pydoc import locate
    if isinstance(library,str):
        library=getattr(mds,library)
    nms = library.list_symbols()
    library1 = mongo.getLibraryName(library)
    for i,nm in enumerate(nms):
        nm1, freq1=nm.split('_')
        print('library: {} / name: {} (in library: {}/{})'.format(library1,nm,i,len(nms)))
        try:
            md1=mds.read_metadata(nm1,freq1,library=library)
            # md1 = locate(md1['cls'])(md1)
            mds.write_metadata(md1, library, onlyGlobal=True)
        except Exception as e:
            print('FAILED')
            uu.printException(e)


def copyMetadata2GlobalAll():
    #['fundoVS', 'assetTS', 'fundamentalVS', 'testVS', 'testTS', 'b3VS', 'econVS', 'b3VS_XML']:
    # for library in [ 'econVS', 'b3VS_XML']:
    #     copyMetadata2Global(library)
    for library in [ 'assetTS', 'assetVS']:
        copyMetadata2Global(library)

# def delMetaWnoData(library):
#     nms = library.list_symbols()
#     for nm in nms:


if __name__ == '__main__':
    ip = socket.gethostbyname(socket.gethostname())
    uu.save_obj('ipBloomberg',ip)
    #copyMetadata2GlobalAll()
    #bloombergInsertRoutine()
    bloombergUpdateRoutine()

    # bloomberg_update_from_list(['ES1', 'TY1'])

    # bloombergUpdateMetadata()

    a=1

    #

    # print('Hello')
    # time.sleep(5)



    # bloomberg.bloombergInitialRoutine()
    # bloombergUpdateRoutine()


# def bloombergUpdateOverride(mds, dti, bOnlyUpdateMetadata=False, srsMeta=None, overwrite=False,
#                             prune_previous_version=True):
#     from mDataStore import mDataFrame, metadataFundamental, metadataOption, metadataAsset, metadataIndicator, \
#         metadataStrategy
#
#     if srsMeta is None:
#         srsMeta = get_meta_to_insert()
#
#     # hist_table = srsMeta['hist_table']
#     histoverride_table = srsMeta['histoverride_table']
#     histoverride_table.fillna('', inplace=True)
#     desc = srsMeta['desc']
#
#     #hist_override (NTN-B)
#
#     col = histoverride_table.columns
#     fields = [f for f in col if ('FIELDS' in f.upper()) or ('OVERRIDE' in f.upper())]
#
#     dfFlds = histoverride_table[fields].drop_duplicates()
#
#     histoverride_table['id'] = arange(histoverride_table.shape[0])
#     maxQuery = 50
#     success = np.full(histoverride_table.shape[0],False)
#
#     for i in range(dfFlds.shape[0]):
#         I = np.all(histoverride_table[fields] == dfFlds.iloc[i, :], 1)
#
#         hist1 = histoverride_table[I]
#         N = int(np.ceil(hist1.shape[0]/maxQuery))
#         fields1 = [dfFlds[f].iloc[0] for f in fields if (not dfFlds[f].iloc[0] is None and not (isinstance(dfFlds[f].iloc[0],str) and dfFlds[f].iloc[0]=='') ) and 'FIELDS' in f]
#         fields_override1 = [dfFlds[f].iloc[0] for f in fields if not dfFlds[f].iloc[0] is None and 'OVERRIDE' in f]
#
#         #import threading
#         from threading import Thread
#
#         class P1(Thread):
#             def __init__(self, fields1, blp1):
#                 self.blp = blp1
#                 #self.df0 = df0
#                 self.fields1 = fields1
#                 self.exit = False
#                 self.df0 = None
#                 super(P1, self).__init__()
#
#             def run(self):
#                 import time
#                 while not self.exit:
#
#                     if not self.df0 is None:
#                         time.sleep(0.01)
#                         try:
#                             dts = self.df0.index
#                             fields1 = self.fields1
#                             df1=pd.DataFrame(np.empty((dts.size, len(fields1))), dts, columns=fields1)
#                             for t, dt_ in enumerate(dts):
#                                 overr_dict = self.df0.iloc[t].to_dict()
#                                 overr_dict['PX_BID'] = overr_dict.pop('PX_DIRTY_BID')
#                                 overr_dict['SETTLE_DT'] = "{:%Y%m%d}".format( uu.workday(dt_,1)[0].astype(dt))  #uu.workday(dt_,2)[0].astype(dt)
#                                 df = self.blp.getRefData([feeder_id[l]], fields1, overr_dict)
#                                 df1.iloc[t, :] = df.iloc[0, :]
#                                 # if t % 10==0:
#                                 #     print(dt_)
#                             self.df = df1
#                         except:
#                             print('ERRO')
#
#                         self.df0 = None
#
#         for k in range(N):
#             hist1a = hist1.iloc[k*maxQuery:(k+1)*maxQuery, :]
#             II = np.array([not h is None for h in hist1a.FEEDER_ID])
#
#             if any(~II):
#                 warn('tickers missing')
#                 hist1a = hist1a[II]
#
#             short_name = hist1a.index.values
#             feeder_id = hist1a.FEEDER_ID.values
#             type1 = hist1a.TYPE.values
#             is_fut = hist1a.IS_FUT.values
#             maturity = hist1a.maturity.values
#             library1 = hist1a.library.values
#             freq1 = hist1a.freq.values
#             #multiplier = hist1a.multiplier.values
#             #min_trade = hist1a.minTrade.values
#
#             if bOnlyUpdateMetadata:
#                 mds.updateMetadataFromDF(hist1a)
#             else:
#                 desc1 = blp.getRefData(feeder_id, desc)
#
#                 df1=[]
#                 nThreads=1
#
#                 #blps = [bloomberg.blp()]*nThreads
#
#                 if 'SETTLE_DT' in [f.upper() for f in fields_override1]:
#                     df0 = blp.getHistoricData(feeder_id, ['PX_DIRTY_BID', 'YLD_YTM_BID'], dti, dt.now())
#                     df1 = []
#                     threads = []
#                     for i in range(nThreads):
#                         th1 = P1(fields1,blp)
#                         #                            th1.run()
#                         th1.start()
#                         threads.append(th1)
#                     for l in range(hist1a.shape[0]): #tqdm(
#                         df0a =df0[l]
#                         N=int(np.ceil(df0a.index.size/nThreads))
#                         for i,th1 in enumerate(threads):
#                             th1.df0=df0a.iloc[i * N:(i + 1) * N]
#                         while True:
#                             all1=True
#                             for th1 in threads:
#                                 all1=all1 and th1.df0 is None
#                             if all1:
#                                 break
#
#                         df_=pd.concat([th.df for th in threads],0).sort_index()
#                         df_['PX_DIRTY_BID']=df0a['PX_DIRTY_BID']
#                         df_['YLD_YTM_BID']=df0a['YLD_YTM_BID']
#                         df1.append(df_)
#                         print('l:{}/{}'.format(l,hist1a.shape[0]))
#
#                     for th1 in threads:
#                         th1.exit=True
#                 else:
#                     raise(Exception('Not implemented: hist override without SETTLE_DT'))
#
#                 for l,df in enumerate(df1):
#                     if df.shape[0]>0:
#                         df = mDataFrame(df)
#                         df.md = metadataAsset(short_name[l], type1[l], df.index[0], df.index[-1],
#                                               desc1.CRNCY[feeder_id[l]], int(is_fut[l]), freq=freq1[l])
#                         # if 'MATURITY' in desc1.columns and not desc1.MATURITY[l] is None:
#                         #     df.md.maturity=dt.combine(desc1.MATURITY[feeder_id[l]],datetime.time())
#                         df.md.nameBLP = desc1.NAME[feeder_id[l]]
#                         df.md.feeder_id = feeder_id[l]
#                         df.md.maturity = pd.to_datetime(maturity[l])
#                         #df.md.multiplier = multiplier[l]
#                         #df.md.minTrade = min_trade[l]
#
#                         #get output columns
#                         fieldsOUT = [f for f in col if 'OUT' in f.upper()]
#                         fieldsout1 = hist1a[fieldsOUT].iloc[l, :]
#                         fieldsout1 = [f for f in fieldsout1 if not f is None and not (isinstance(f, str) and f == '')]
#
#                         df.columns = fieldsout1
#
#                         for s in df.columns:
#                             if np.all(np.isnan(df[s])):
#                                 del df[s]
#
#                         if overwrite:
#                             for s in df.columns:
#                                 if np.all(np.isnan(df[s])):
#                                     del df[s]
#
#                             #self.append(df)
#                             mds.write(df, library=library1[l], check_metadata=False, prune_previous_version=prune_previous_version)
#                             successi = True
#                         else:
#                             mds.append(df, library=library1[l], check_metadata=False, prune_previous_version=prune_previous_version, replaceIntersection=True)
#                             successi = True
#                             # successi =mds.appendIfCheck(df,date_range=[dti,dt.now()],library=library1[l], check_metadata=False, prune_previous_version=prune_previous_version)
#
#                         success[l]=successi
#     return success



# def copy2online(mds, srsMeta, dest='onlineTS', overwrite=False):
#     hist1 = srsMeta['intra_table']
#
#     dt1 = pd.Timestamp(dt.now()).normalize()
#     dt0=dt1 - pd.Timedelta(days=15)
#     for i in range(hist1.shape[0]):
#         a=Dict(hist1.iloc[i].to_dict())
#         a.SHORT_NAME=hist1.iloc[i].name
#         doCopy=False
#
#         print('Processing {}'.format(a.SHORT_NAME))
#         if not overwrite:
#
#             try:
#                 df1 = mds.read(a.SHORT_NAME,a.freq,library=a.library,date_range=[dt0,dt1])
#             except Exception as e:
#                 warn('Unable to read {}/{} from {} in copy2online'.format(a.SHORT_NAME,a.freq,a.library))
#                 uu.printException(e)
#
#                 try:
#                     df1 = mds.read(a.SHORT_NAME, a.freq, library=a.library)
#                 except:
#                     continue
#                 doCopy = True
#
#             if not doCopy:
#                 try:
#                     df0 = mds.read(a.SHORT_NAME,a.freq,library=dest,date_range=[dt0,dt1])
#                     if df1.index[-1] > df0.index[-1]:
#                         doCopy = True
#                 except:
#                     doCopy = True
#
#         else:
#             doCopy = True
#
#         if doCopy:
#             print('Copying...')
#             df1 = mds.read(a.SHORT_NAME, a.freq, a.library, date_range=[dt(1990, 1, 1), dt(2030, 1, 1)])
#
#             try:
#                 mds.delete(df1.md.name, df1.md.freq, library=dest)
#             except:
#                 pass
#
#             mds.write(df1, library=dest)
