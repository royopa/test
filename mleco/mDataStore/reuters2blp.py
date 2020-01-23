from py_init import *
# from asset import *
# from feeder import *
from mDataStore.globalMongo import mds
from mDataStore.mongo import convertFreq
import arctic as arclib
DateRange = arclib.date.DateRange

def cnvReuters2BlpFut(asset1,freq):
    pass

def consolidateReutersBlpIntraday(asset1,srBlp,freq):
    pass

from mDataStore.mongo import mongoDS


def cnv2minuteAll(lst=None,library=mds.assetTS):
    ms = mds.find(library=library)

    for m in ms:
        if m[2].freq=='1Second': # and m[2].name.startswith('DIJ') and not m[2].name.startswith('DIJc')
            print('Converting {}'.format(m[2].name))
            nm1=m[2].name
            if not lst is None:
                if nm1 in lst:
                    cnv2minute1(nm1,library=mds.assetTS)
            else:
                cnv2minute1(nm1, library=mds.assetTS)


def cnv2minute1(tk,library=mds.assetTS):
    dti = library.min_date(tk+'_1Second')
    dtf = library.max_date(tk+'_1Second')

    dts = pd.date_range(dti,dtf,freq='6MS').normalize()
    lst1=list(pd.to_datetime(dts))
    lst1 = [l.to_pydatetime() for l in lst1]
    dts=[dti]+lst1+[dtf]

    try:
        mds.delete(tk,ds.freqHelper.minute, library=library)
    except Exception as e:
        print('UNABLE TO DELETE:')
        uu.printException(e)

    for t,dt0 in enumerate(dts[:-1]):
        dt1 = dts[t+1]
        if dt0>= dt1:
            continue
        try:
            df1 = mds.read(tk, ds.freqHelper.second, library=library, date_range=[dt0, dt1])
        except Exception as e:
            print('Error reading {}'.format(tk))
            uu.printException(e)
        for fld in ['close','yield_close','ask','yield_ask','bid','yield_bid']:
            if fld in df1:
                df1[fld][df1[fld]==0]=np.NaN

        df2 = convertFreq(df1,ds.freqHelper.minute)
        mds.append(df2,library=library,check_metadata=False)

def cp2blp(librarySource=mds.assetTS,libraryDest=mds.assetTS2):
    # from mDataStore.bloomberg import get_srs_meta
    # if srsMeta is None:
    #     srsMeta = get_srs_meta()

    nms,nmsBlp=cnvAllReutersTickers(library=librarySource)

    #k=[i for i,nm in enumerate(nms) if nm =='ESc1'][0]

    for i,nm in enumerate(nms):
        print('Copying {} - {}/{}'.format(nm,i,len(nms)))
        # if not nmsBlp[i].startswith('DI1'):
        #     continue
        df1=mds.read(nm,ds.freqHelper.minute,librarySource,date_range=[dt(1990,1,1),dt(2030,1,1)])
        df1.md.name=nmsBlp[i]
        try:
            mds.delete(df1.md.name,df1.md.freq,library=libraryDest)
        except:
            pass
        mds.write(df1,library=libraryDest)


def renameDIs():
    from mDataStore.globalMongo import mds
    lst = mds.find(library=mds.assetTS2)

    for l in lst:
        if l[2].name.startswith('OD'):
            df1 = mds.read(l[2].name,l[2].freq,library=mds.assetTS2)
            df1.md.name =df1.md.name.replace('OD','DI1')
            mds.write(df1,library=mds.assetTS2)
            mds.delete(l[2].name,l[2].freq,library=mds.assetTS2)

def cnvAllReutersTickers(library=mds.assetTS):
    import xlwings as xw
    ms = mds.find(library=mds.assetTS)
    nms = [m[2].name for m in ms if m[2].freq=='1Second']


    d = {'.SA':'','DIJ':'DI1','IND':'BZ','c1':'1','c2':'2','DOL':'UC'}

    def replace1(s1,d):
        for k,v in d.items():
            s1=s1.replace(k,v)
        return s1

    nmsBLP = [replace1(nm,d) for nm in nms]

    return nms,nmsBLP


def cp2onlineTS():
    from mDataStore.globalMongo import mds

    ms = mds.find(library=mds.assetTS2)

    for i, m in enumerate(ms):

        nm = m[2].name
        print('Copying {} - {}/{}'.format(nm,i,len(ms)))
        if m[2].freq=='1Minute':
            df = mds.read(nm,'1Minute',mds.assetTS2,date_range=[dt(1990,1,1),dt(2035,1,1)])
            try:
                mds.delete(nm,'1Minute',library=mds.onlineTS)
            except:
                pass

            mds.write(df, library=mds.onlineTS, check_metadata=False)

def cp2onlineVS():
    from mDataStore.globalMongo import mds

    ms = mds.find(library=mds.assetVS)

    for i,m in enumerate(ms):

        nm = m[2].name
        print('Copying {} - {}/{}'.format(nm,i,len(ms)))
        if m[2].freq=='1BDay':
            df = mds.read(nm,'1BDay',mds.assetVS,date_range=[dt(1990,1,1),dt(2035,1,1)])
            try:
                mds.delete(nm,'1BDay',library=mds.onlineVS)
            except:
                pass

            mds.write(df,library=mds.onlineVS,check_metadata=False)


def fixInttradayMD(ats = ['IND','DOL','ES','TY'],freqs=['1Second','1Minute'],lib='assetTS'):
    for at in ats:
        for f in freqs:
            for suff in ['c1','c2']:
                print(at+suff)
                md1 = mds.read_metadata(at+suff,f,lib)
                md1.fut_like=True
                mds.write_metadata(md1,lib)


def correctFutRoutine(codes=['IND','DOL','TY','ES']):

    for code in codes:
        for mty in ['c1','c2']:
            correctGenFut(mds,code+mty,'1Second')



@njit
def cntrep(x):
    c=zeros_like(x)
    v=x[0]
    cnt=0
    t0=0
    for t in range(x.shape[0]):
        if x[t]==v:
            cnt+=1
        else:
            c[t0:t]=cnt
            cnt=1
            v=x[t]
            t0=t

    c[t0:]=cnt
    return c




def correctGenFut(mds, code, freq):
    '''
    Correct data for Gen Future from reuters. It sometimes use the second future instead of the first.
    just deleting this data.
    '''

    symbol = code + '_' + freq
    dt0 = mds.assetTS.min_date(symbol)
    dt1 = mds.assetTS.max_date(symbol)

    dts = pd.date_range(dt0, dt1, freq='3MS').tolist()
    dts.append(dt1)
    print('analyzing {}'.format(code))

    #last_underlying = []
    for t, dt0_ in enumerate(dts[:-1]):
        dt1_ = dts[t + 1]
        # print('analyzing {} : {} - {}'.format(code,dt0_, dt1_))
        df = mds.read(code, freq=freq, date_range=[dt0_, dt1_])

        df1 = df.copy()
        #order unames according to time (so, invert year and month.
        #underlying will be replaced by integers reflecting order
        unames_ =  pd.unique(df.underlying)
        unames=unames_.copy()
        for i in range(len(unames)):
            dt1=df.index[df.underlying==unames_[i]][-1]
            match = re.match(r"([a-z]+)([0-9]+)", unames_[i], re.I)
            assert(match)
            items = match.groups()
            dig=1*(dt1.year - 2000-int(items[1][-1])>2)
            unames[i]=items[0][:-1]+dig.__str__()+ items[1][-1]+items[0][-1]
        idx=np.argsort(unames)

        map1 = {k:v for v,k in enumerate(unames_[idx])}
        df1.underlying = df1.underlying.replace(map1)

        # df1['cnt']=cntrep(df1.underlying.values)
        # df1.underlying[df1['cnt']<1500]
        I = df1.underlying.values[1:] < df1.underlying.cummax().values[:-1]

        # I = df1.underlying.values[:-1] > df1.underlying.cummin().values[:0:-1]
        I1=I[1:]!=I[:-1]
        J = np.where(I1)[0]
        dt_rep = df1.index[J + 1]
        dt_rep=dt_rep.append(df1.index[-1:].shift(1,'S'))
        # dt_rep = df1.index[J]
        if len(dt_rep)>0:
            for j in range(len(dt_rep)-1):
                if I[J[j]+1]:
                    dt_rg = DateRange(dt_rep[j], dt_rep[j+1])
                    print('correcting: {} - dates: {} - {}'.format(symbol,dt_rg.start,dt_rg.end))
                    a=1
                    mongoDS.TS_deleteDateRange(mds.assetTS, symbol, dt_rg, df)



if __name__ =='__main__':
    # import mDataStore.bloomberg as bloomberg
    # correctFutRoutine()
    # correctFutRoutine(codes=['TY', 'ES'])
    ##### renameDIs()
    # cnv2minuteAll(library=mds.assetTS)

    # cnv2minuteAll(['INDc1','DOLc1','TYc1','ESc1','INDc2','DOLc2','TYc2','ESc2'],
    #               library=mds.assetTS)
    # cp2blp()
    # cp2onlineVS()
    # bloomberg.bloombergUpdateRoutine()
    # cp2onlineTS()

    # a=1
    # feed1 = feeder.get(['INDc1', 'INDc2'], ds.freqHelper.minute, date_range=[dt(2000, 1, 1), dt(2020, 1, 1)])
    # asset1 = asset.get( feederCollection(['INDc1','INDc2']) )

    # consolidateReutersBlpIntraday(a1, 'BZ1',ds.freqHelper.minute )

    cp2onlineTS()


def saveFutures2pickle(mds):

    lst=['INDc1','DOLc1','TYc1','ESc1','INDc2','DOLc2','TYc2','ESc2']
    names=[]
    path1=globalM.dataRoot+'/futPickle'
    for l in lst:
        name=saveFuture2pickle(mds, l, ds.freqHelper.second,path=path1)
        names.append(name)
    uu.save_obj(names,'saveFutures2pickle',path=path1)

def saveFuture2pickle(mds, code, freq,path):

    symbol = code + '_' + freq
    dt0 = mds.assetTS.min_date(symbol)
    dt1 = mds.assetTS.max_date(symbol)

    dts = pd.date_range(dt0, dt1, freq='6MS').tolist()
    dts.append(dt1)
    print('analyzing {}'.format(code))

    #last_underlying = []
    for t, dt0_ in enumerate(dts[:-1]):
        dt1_ = dts[t + 1]
        # print('analyzing {} : {} - {}'.format(code,dt0_, dt1_))
        df = mds.read(code, freq=freq, date_range=[dt0_, dt1_])
        if df.shape[0]>0:
            name=symbol+'_{:%Y-%m-%d}_{:%Y-%m-%d}'.format(dt0_, dt1_)
            uu.save_obj(df,name,path=path)

    return name

def loadFuturesFrompickle(mds:mongoDS,library='assetTS'):
    names=uu.save_obj('saveFutures2pickle',path=path1)
    path1=globalM.dataRoot+'/futPickle'

    for nm in names:
        print('uploading {}'.format(name))
        df=uu.load_obj(name,path=path1)
        mds.append(df,library=library)



