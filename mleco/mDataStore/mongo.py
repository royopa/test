'''
-funcao para remover versoes anteriores (chamando prune e save com prune
-importar opcoes e futuros da bmf. acertar metadata de tudo
-importar curva pre bmf
-fazer rolagem de futuros e vertice fixo
importar economatica (no trabalho)
importar economatica (no trabalho)
importar bloomberg (no trabalho)
'''
from pymongo.errors import DuplicateKeyError

from mDataStore import freqHelper as f
from mDataStore import bloomberg #as bloomberg
from mDataStore import util

import pymongo
from globalM import mongoStr
from arctic import Arctic, TICK_STORE, VERSION_STORE
import arctic as arclib
from datetime import datetime as dt
import pandas as pd
import numpy as np
from mUtil import Dict
from six import string_types
import re
from warnings import warn
from pydoc import locate
import pytz
import datetime
import globalM
import os
import six
from copy import copy
from bson.binary import Binary
import pickle
import subprocess
import arctic
from copy import deepcopy
from io import BytesIO

tzInsert='America/Sao_Paulo'
DB_OBJ='db_dws'
#sudo timedatectl set-timezone America/Sao_Paulo

try:
    import xlwings as xw
except:
    pass
import mUtil as uu
try:
    from mDataStore.bloomberg import blp
except:
    blp=None
#_mongo=None
_arctic=None
from arctic.date import DateRange
from arctic.tickstore.tickstore import SYMBOL,META



def connect(mongoStr=mongoStr,**kwargs):
#    global _mongo
    _mongo = pymongo.MongoClient(mongoStr, **kwargs)  #

    return _mongo


types = ['equity','future','fut_rol','fut_cat','equity_raw','index','option','strategy','fund','fx','etf','vol','bond','fut_nrol']
fields = ['open','high','low','close','yield_open','yield_high','yield_low','yield_close','bid','ask','yield_bid',
            'yield_ask','volume','gmt_off','underlying','open_interest','vwap','du','duration','AUM', 'numShares','nav_close',
          'alpha_close','close_nan','yield_close_nan','neg','volume_fin','last','dtLast',
               'timeLast','vol','strike','delta','gamma','theta','vega','release_dt','trades','lending_rate','borrow_rate']

libraries = ['assetTS','assetVS','fundamentalVS','b3VS','testTS','testVS','b3VS_XML','mktData','onlineTS','assetTS2','onlineVS','econVS','fundoVS']
lib_types=[TICK_STORE, VERSION_STORE,VERSION_STORE,VERSION_STORE,TICK_STORE,VERSION_STORE,VERSION_STORE,TICK_STORE,TICK_STORE,TICK_STORE,VERSION_STORE,VERSION_STORE,VERSION_STORE]

#frequencies=pandas.tseries.offsets.__all__
from pandas.tseries.offsets import __all__ as frequencies

metaSelfAttr=['library','firstDT','lastDT'] #fields not stored
# from addict import Dict

class metadataBase(Dict):
    attr=[]
    def __init__(self, *args, **kwargs):
        super(metadataBase, self).__init__(*args, **kwargs)
        # self.library=None
        # self.firstDT=None
        # self.lastDT=None
        self['cls']=type(self).__module__ +'.'+type(self).__name__

    # def __setattr__(self, name, value):
    #     if name in metaSelfAttr:
    #         dict.__setattr__(self,name, value) #do not set in dict items
    #     else:
    #         super(metadataBase, self).__setattr__(name, value)

    # def __getattr__(self, item):
    #     if item in metaSelfAttr:
    #         return dict.__getattribute__(self,item) #do not set in dict items
    #     else:
    #         return super(metadataBase, self).__getattr__(item)

    def __str__(self):
        if self.firstDT:
            tz=self.firstDT.tzinfo
        else:
            tz='None'
        str=self.to_dict().__str__().replace(',',',\n')+ '\nlibrary:{}\nfirstDT:{}\nlastDT :{}\ntzinfo:{}'.format(self.library,self.firstDT,self.lastDT,tz)
        return str

    @classmethod
    def _hook(cls, item):
        if isinstance(item, dict):
            return Dict(item)
        elif isinstance(item, (list, tuple)):
            return type(item)(Dict._hook(elem) for elem in item)
        return item

#    def __repr__(self):
#        return self.__str__()

    # def getLibrary(self):
    #     if isinstance(self, metadataAsset):
    #         str = 'asset'
    #     else:
    #         str = 'fundamental'
    #
    #     nfreq,sfreq=splitFreq(self.freq)
    #     if sfreq in ['Hour','Minute','Second','Milli','Micro','Nano',]:
    #         str+= 'TS'
    #     else:
    #         str += 'VS'
    #
        # self.library=str

        return str
    # def getDates(self):
    #     if not self.library:
    #         self.getLibrary()
    #     global _arctic
    #     id=self.name +'_'+self.freq
        # try:
        #     self.firstDT=_arctic[self.library].min_date(id)
        # except:
        #     self.firstDT =None
        #
        # try:
        #     self.lastDT=_arctic[self.library].max_date(id)
        # except:
        #     self.lastDT =None

    def __dir__(self):
        return list(self.keys()) + metaSelfAttr +dict.__dir__(self)

    def __eq__(self, other):
        if not isinstance(other,Dict):
            return False
        return util.equal_dicts(self.to_dict(),other.to_dict(),['stDT'])#self.to_dict()==other.to_dict()

    def checkMetadata(self):
        for a in self.__class__.attr:
            if not a in self:
                warn('meta check {} not in {}'.format(a,self.name))
            #assert(a in self)


def dateFormat(dt1):

    if isinstance(dt1,dt):
        dt0=dt1.replace(tzinfo=None)

        if dt0>dt.max-datetime.timedelta(days=1):
            dt1=np.inf
        elif dt0<dt.min+datetime.timedelta(days=1):
            dt1 = -np.inf
    if isinstance(dt1,dt):
        return '{:%Y-%b-%d}'.format(dt1)
    elif dt1:
        return '{:<11}'.format(dt1)
    else:
        return 'None       '





class metadataAsset(metadataBase):
    attr = ['name', 'type', 'subtype', 'currency', 'fut_like', 'maturity', 'stDT', 'endDT', 'freq']

    def __init__(self,name=None, type=None,stDT=None,endDT=None, currency='BRL', fut_like=False,maturity=None,  freq='1BDay',subtype=None, *args, **kwargs):
        if isinstance(name,dict):
            super(metadataAsset, self).__init__(name, *args, **kwargs)
            #self.checkMetadata()

        else:
            super(metadataAsset, self).__init__()
            self.name=name
            #assert(type)
            if type:
                assert(type in types)
            self.type=type
            self.subtype = subtype
            self.currency = currency
            self.fut_like = fut_like

            if maturity:
                if isinstance(maturity,dt):
                    if isinstance(maturity, datetime.date):
                        maturity = dt.combine(maturity, datetime.time())
                        maturity = maturity.replace(hour=0, minute=0, second=0, microsecond=0)
                    maturity=maturity.replace(hour=0,minute=0,second=0, microsecond=0)
            self.maturity = maturity
            if endDT:
                if isinstance(endDT,datetime.date) and not isinstance(endDT,dt):
                    endDT=dt.combine(endDT,datetime.time())
                else:
                    endDT = uu.x2dti_date(endDT)
                endDT=endDT.replace(hour=0, minute=0, second=0, microsecond=0)
            if stDT:
                if isinstance(stDT,datetime.date) and not isinstance(stDT,dt):
                    stDT=dt.combine(stDT,datetime.time())
                else:
                    stDT = uu.x2dti_date(stDT)
                stDT=stDT.replace(hour=0, minute=0, second=0, microsecond=0)
            self.stDT = stDT
            self.endDT = endDT
            self.freq = freq
            for k,v in kwargs.items():
                self[k]=v
    def __str__(self):
        if self.firstDT:
            tz=self.firstDT.tzinfo
            if tz:
                tz=re.findall("'.*'", tz.__str__())[0][1:-1]

        else:
            tz='None'
        
        str= 'name: {:14}| type: {:14}| currency: {:11}| '.format(self.name,self.type,self.currency)
        str+=' freq: {}'.format(self.freq)
        str+='\nfut_like: {:<10}| endDT: '.format(self.fut_like) + dateFormat(self.endDT) + '  | maturity: '+dateFormat(self.maturity)
        str+='\nlibrary:{:<12}| firstDT:{} | lastDT: {}  | tz:{}'.format(self.library if self.library else 'None',dateFormat(self.firstDT),dateFormat(self.lastDT),tz)
       # str+= '\nlibrary:{}\nfirstDT:{}\nlastDT :{}\ntzinfo:{}'.format(self.library,self.firstDT,self.lastDT,tz)
        return str


class metadataStrategy(metadataAsset):
    attr = ['name', 'type','subtype', 'currency', 'fut_like', 'maturity', 'stDT', 'endDT', 'freq','assetNames']
    def __init__(self,name=None, stDT=None,endDT=None, currency='BRL',  freq='1BDay', subtype=None,assetNames=[], *args, **kwargs):
        super(metadataStrategy,self).__init__(name=name, type='strategy',stDT=stDT,endDT=endDT, currency=currency, fut_like=False,maturity=None,  freq=freq, subtype=subtype, *args,**kwargs)
        self.assetNames=assetNames


class metadataIndicator(metadataBase):
    attr = ['name', 'type',  'stDT', 'endDT', 'freq','subtype','feederNames']
    def __init__(self,name=None, type=None,stDT=None,endDT=None,   freq='1BDay', subtype=None,feederNames=[], *args, **kwargs):
        if isinstance(name,dict):
            super(metadataIndicator, self).__init__(name, *args, **kwargs)
        else:
            super(metadataIndicator,self).__init__()
            self.name=name
            self.type=type
            self.subtype = subtype
            self.feederNames = feederNames
            self.freq=freq

            if endDT:
                if isinstance(endDT, datetime.date) and not isinstance(endDT, dt):
                    endDT = dt.combine(endDT, datetime.time())
                else:
                    endDT = uu.x2dti_date(endDT)
                endDT = endDT.replace(hour=0, minute=0, second=0, microsecond=0)
            if stDT:
                if isinstance(stDT, datetime.date) and not isinstance(stDT, dt):
                    stDT = dt.combine(stDT, datetime.time())
                else:
                    stDT = uu.x2dti_date(stDT)
                stDT = stDT.replace(hour=0, minute=0, second=0, microsecond=0)
            self.stDT = stDT
            self.endDT = endDT
            for k,v in kwargs.items():
                self[k]=v


class metadataFundamental(metadataBase):
    def __init__(self,name=None, type=None,stDT=None,endDT=None, currency='BRL', freq='1BDay', *args, **kwargs):
        if isinstance(name,dict):
            super(metadataFundamental, self).__init__(name, *args, **kwargs)
            self.checkMetadata()
        else:
            super(metadataFundamental, self).__init__()
            self.name=name
            #assert(type)
            self.type=type
            self.currency = currency
            if endDT:
                if isinstance(endDT,datetime.date):
                    endDT=dt.combine(endDT,datetime.time())
                else:
                    endDT = uu.x2dti_date(endDT)
                endDT=endDT.replace(hour=0, minute=0, second=0, microsecond=0)
            if stDT:
                if isinstance(stDT,datetime.date):
                    stDT=dt.combine(stDT,datetime.time())
                else:
                    stDT = uu.x2dti_date(stDT)
                stDT=stDT.replace(hour=0, minute=0, second=0, microsecond=0)
            self.stDT = stDT
            self.endDT = endDT
            self.freq = freq


class metadataOption(metadataAsset):
    def __init__(self,name=None, type=None, stDT=None,endDT=None,currency='BRL', fut_like=True,maturity=None,  freq='1BDay',subtype=None,strike=None,underlying=None,cp=None, *args, **kwargs):
        if isinstance(name,dict):
            super(metadataOption, self).__init__(name, *args, **kwargs)
            self.checkMetadata()
        else:
            super(metadataOption,self).__init__(name, type, stDT,endDT, currency, fut_like,maturity, freq, subtype,*args, **kwargs)
            #assert(not strike is None)
            #assert(not underlying is None)
            if not isinstance(name,metadataOption) and not isinstance(name,dict):
                self.strike=strike
                self.underlying = underlying
                self.cp=cp
    # def checkMetadata(self):
    #     attr=['name','type','currency','fut_like','maturity','stDT','endDT','freq','strike','underlying','cp']
        # for a in attr:
        #     assert(a in self)

class mDataFrame(pd.DataFrame):

    # temporary properties
#    _internal_names = pd.DataFrame._internal_names + ['internal_cache']
#    _internal_names_set = set(_internal_names)

    # normal properties
    _metadata = ['md']

    @property
    def _constructor(self):
        return mDataFrame


#file='C:\\Users\\bmori\\Python\\data\\datascope_csv\\_input\\es_ty_c2.csv.gz'
#file='C:\\Users\\bmori\\Python\\data\\datascope_csv\\done\\es_ty_c2.csv.gz'



def checkDF(df):
    assert(hasattr(df, 'md'))
    if isinstance(df.md,metadataAsset):
        for l in df.columns:
            assert(l in fields)

    assert(df.index.is_unique)
    nfreqm, sfreqm = splitFreq(df.md.freq)
    try:
        freq=pd.infer_freq(df.tail(30).index, warn=True)
        if freq:
            nfreq,sfreq=splitFreq(freq)
            if not sfreq in sfreqm or nfreq != nfreqm:
                warn('checkDF: Frequency of {} is stated as {} but looks as {}'.format(df.md.name,df.md.freq,freq))
    except:
        pass
    assert(sfreqm in frequencies)
    assert(df.md.freq[0].isdigit())


#def subclassMeta(meta):
#cur=mds.mongo.objDB.all.find({},['name'])
# - all
# - strategy
#

class feederPickler(pickle.Pickler):
    #see https://docs.python.org/3/library/pickle.html#pickle-persistent
    def persistent_id(self, obj):
        from feeder import feeder,pool,poolLoad,FEED_FROM_DB,FEED_FROM_DF,FEED_LIVE,PlaceHolder
        # import constants as c
        # Instead of pickling MemoRecord as a regular class instance, we emit a
        # persistent ID.
        if isinstance(obj, PlaceHolder):
            cls=type(obj).__module__ + '.' + type(obj).__name__
            id = obj.id#(obj.name, obj.freq, obj.library,cls)
            return ("placeholder", id)
        elif (not hasattr(obj,'blotter')) and ((isinstance(obj, feeder) and hasattr(obj,'mode') and obj.mode in [FEED_FROM_DB,FEED_LIVE])):
            cls=type(obj).__module__ + '.' + type(obj).__name__
            if hasattr(obj,'stDT0'):
                stDT0=obj.stDT0
            else:
                stDT0 = dt(1900,1,1)
            id = [obj.name,obj.freq,obj.library,stDT0,cls]
            if hasattr(obj,'fundCurrency'):
                id+=[obj.fundCurrency]
            return ("feeder", tuple(id))
        else:
            return None


class feederUnpickler(pickle.Unpickler):

    # def __init__(self):
    #     super().__init__(file)
    #     self.connection = connection

    def persistent_load(self, pid):
        # This method is invoked whenever a persistent ID is encountered.
        # Here, pid is the tuple returned by DBPickler.
        # cursor = self.connection.cursor()
        type_tag,id  = pid

        if type_tag == "placeholder":
            from feeder import FEED_LIVE
            # Fetch the referenced record from the database and return it.
            # id=list(id)
            cls = locate(id[-1])
            # try:
            obj= cls.load(name=id[0],freq=id[1],library=id[2])
            obj.setLive(obj.mode==FEED_LIVE)

            return obj

            # except:
            #     a=1

        elif type_tag == "feeder":
            # id=list(id)
            cls = locate(id[4])
            date_range = [id[3], dt(2100,1,1)] if not id[3] is None else None
            if len(id)>=6:
                kwargs = dict(fundCurrency=id[5])
            else:
                kwargs = dict()

            return cls.get(codes=id[0], freq=id[1], library=id[2], date_range=date_range,**kwargs)
        else:
            # Always raises an error if you cannot return the correct object.
            # Otherwise, the unpickler will think None is the object referenced
            # by the persistent ID.
            raise pickle.UnpicklingError("unsupported persistent object")




class mongoObjDB(object):
    MAX_SZ_MONGO=14*10**6
    def __init__(self,mongo:pymongo.mongo_client.MongoClient,
                 base='all',types=None,freqs=None,date_range=None,mds=None,setAttr=False):
        self.mongoCli=mongo
        self.base=base
        self.types=types
        self.date_range=date_range
        self.freqs=freqs
        self.mds=mds

        self.setAttr=setAttr
        if setAttr:
            colNames=self.mongoCli[DB_OBJ].list_collection_names()
            self.subColNames= [c[len(self.base)+1:].split('.')[0] for c in colNames if c.startswith(self.base+'.')]
            #aa
            if types and len(types>1):
                for typ in types:
                    setattr(self,typ,mongoObjDB(self.mongoCli,base=self.base,types=[typ],freqs=freqs,date_range=date_range))

            for c in self.subColNames:
                setattr(self, c, mongoObjDB(self.mongoCli, base=self.base+'.'+c, types=self.types,freqs=freqs, date_range=self.date_range))

    def __getattr__(self, item):
        #only called if not on the list of attributes above
        return self.load(item)[0]

    def getpath(self,path):
        if not path is None:
            if '/' in path:
                path = path.replace('/', '.')
            return path
        return ''

    def getdb(self,path=None):
        db = self.mongoCli[DB_OBJ][self.base]

        if not path is None:
            if '/' in path:
                path = path.replace('/', '.')
            db = db[path]
        return db


    def save(self,name,obj,path=None,saveStrategyAsAsset=True,**metadata):
        b=BytesIO()

        mds=self.mds
        db = self.getdb(path)

        if self.types and 'type' in metadata:
            assert(metadata['type'] in self.types)
        myObj = {}
        myObj['name'] = name
        myObj.update(metadata)
        # thebytes = pickle.dumps(obj)
        pickler=feederPickler(b,protocol=-1)
        # pickler=pickle.Pickler(b)

        # try:
        #     from strategy import strategy
        #     if isinstance(obj, (strategy,indicator)):
        #         obj._force_save = True
        # except:
        #     pass

        # thebytes0 = pickle.dumps(obj)
        pickler.dump(obj)
        thebytes = b.getbuffer().tobytes()
        path1=self.getpath(path)
        if len(thebytes)< mongoObjDB.MAX_SZ_MONGO:
            saveFile=False
            myObj['obj'] = Binary(thebytes)
        else:
            saveFile=True
            assert(not '/' in name)
            myObj['obj'] = path1+'/'+name

        e = db.find_one({'name':name})
        if e is None:
            db.insert_one(myObj)
        else:
            # for s in myObj:
            #     e[s]=myObj[s]
            e=myObj
            #e.update()
            d=db.replace_one({'name': name}, e,upsert=True)
            assert(d.raw_result['n']==1)
            assert (d.raw_result['ok'] == 1)

        if saveFile:
            file = os.path.join(globalM.dataRoot + '/obj/' + path1, name) + '.pkl'
            with open(file, 'wb') as fh:
                pickler = feederPickler(fh,protocol=-1)
                pickler.dump(obj)
            # uu.save_obj(obj,name,path=globalM.dataRoot +'/obj/'+path1,pickle=pickler)


        if saveStrategyAsAsset:
            try:
                from strategy import strategy
            except:
                return
            if isinstance(obj,strategy):
                if hasattr(obj,'_mdf'):
                    meta={}
                    meta['fut_like'] = obj.fut_like
                    if obj._dt.size > 0:
                        meta['stDT'] = uu.x2dti_date(obj._dt[0])
                        meta['endDT'] = uu.x2dti_date(obj._dt[-1])
                    else:
                        meta['stDT'] = None
                        meta['endDT'] = None
                    meta['currency'] = obj.currency
    
                    obj._mdf.md = metadataAsset(obj.name, 'strategy', meta['stDT'], meta['endDT'],
                                                obj.currency, obj.fut_like, None, obj.freq)
                    obj._mdf.md.firstDT = meta['stDT']
                    obj._mdf.md.lastDT = meta['endDT']
    
                    obj._mdf.subtype = obj.__class__.__name__
                    mds.write(obj._mdf,check_metadata=False)
                else:
                    obj.df.md=obj.md
                    mds.write(obj.df,check_metadata=False,library=obj.library)

    def load(self,name,path=None,unpicklerClass=feederUnpickler):
        db = self.getdb(path)

        if self.types:
            doc=db.find_one({'name':name, 'type':{'$in':self.types}})
        else:
            doc=db.find_one({'name':name})

        if doc is None:
            return None,doc
        else:
            if isinstance(doc['obj'],str):
                path1,name = doc['obj'].split('/')
                file=os.path.join(globalM.dataRoot +'/obj/'+path1, name) + '.pkl'
                with open(file,'rb') as fh:
                    unpickler=unpicklerClass(fh)
                # doc['obj'] = uu.load_obj(name,path=globalM.dataRoot +'/obj/'+path1,pickle=unpickler)
                    doc['obj'] = unpickler.load()
            else:
                # doc['obj']=pickle.loads(doc['obj'])
                unpickler = unpicklerClass(BytesIO(doc['obj']))
                doc['obj'] = unpickler.load()


            return doc['obj'],doc




    def find(self, path=None, query={},**kwargs):
        db = self.getdb(path)
        query1=query.copy()
        if self.types:
            query1.update({'type': {'$in': self.types}})

        lf=db.find(query1,**kwargs)

        lf = list(lf)
        for f in lf:
            name1=f['obj']
            try:
                if isinstance(name1,str):
                    path1,name = name1.split('/')
                    file = os.path.join(globalM.dataRoot + '/obj/' + path1, name) + '.pkl'
                    unpickler = feederUnpickler(file)
                else:
                    unpickler = feederUnpickler(BytesIO(f['obj']))
                f['obj'] = unpickler.load()
                    # f['obj']=pickle.loads(name1)
            except Exception as e:
                print('ERROR reading mongoDS: {}'.format(name1))
                uu.printException(e)
                f['obj']=None
                f['_Exception']=e

        return lf

    def find_one(self, path=None, query={},**kwargs):
        db = self.getdb(path)
        query1=query.copy()
        if self.types:
            query1.update({'type': {'$in': self.types}})
        f=db.find_one(query1,**kwargs)
        if f:
            if isinstance(f['obj'], str):
                path1, name = f['obj'].split('/')
                file = os.path.join(globalM.dataRoot + '/obj/' + path1, name) + '.pkl'
                unpickler = feederUnpickler(file)
            else:
                unpickler = feederUnpickler(BytesIO(f['obj']))
            f['obj'] = unpickler.load()
                # f['obj'] = pickle.loads(f['obj'])
            return f


    def delete(self,name,path=None,**query):
        db = self.getdb(path)
        if self.types:
            query.update({'type': {'$in': self.types}})

        return db.remove({'name': name}.update(query))

    def deleteCollection(self,path):
        db = self.getdb(path)

        return db.drop()


    def dropCollection(self,path):
        db = self.getdb(path)
        db.drop()

    @property
    def names(self):
        db = self.getdb()
        query={}
        if self.types:
            query.update({'type': {'$in': self.types}})

        cur=db.find(query, ['name'])
        names=[c['name'] for c in cur]
        return names

    def __dir__(self):
        if self.setAttr:
            return self.names + (self.types if self.types else []) +self.subColNames +super(mongoObjDB,self).__dir__()
        else:
            return super(mongoObjDB,self).__dir__()


class mongoDS(object):
    def __init__(self, mongoStr=mongoStr,**kwargs):
        global _arctic

        self.mongoCli=connect( mongoStr,**kwargs)
        _arctic=Arctic(self.mongoCli)
        self.arctic = _arctic

        #insert missing libraries
        libs=self.arctic.list_libraries()
        for i,l in enumerate(libraries):
            if not l in libs:
                self.arctic.initialize_library(l,lib_types[i] )

        for l in libraries:
            setattr(self,l,self.arctic[l])

        self.obj = mongoObjDB(self.mongoCli,mds=self)


    # def write_cache(self,name=['BZ1','UC1'],library='assetVS',freq='1BDay'):
    #     dfs=mds.read(name,freq,library,cache=False)
    #
    #     for i in range(len(dfs)):
    #         dfs[i]['name']=



    def getDI(self,filterMty=True,liqFilter=False,date_range=None):
        if date_range is None:
            dt1=dt(2001, 1, 1)
        else:
            dt1 =date_range[0]
        # raise('update query')
        lst = self.assetVS.list_symbols(name={'$regex': 'DI1.*'}, maturity={'$gte': dt1})
        code = np.char.replace(np.unique(lst), '_1BDay', '').tolist()
        if filterMty:
            code = [c for c in code if 'F' in c ] #or 'N' in c
        return code

    def getDI_intraday(self,filterMty=True,date_range=None):
        # raise('update query')
        lst = self.find(name={'$regex': 'DIJ.*'},freq=f.second,library=self.assetTS2,
                        maturity={'$gte': dt(2001, 1, 1)},date_range=date_range)
        code=lst[:,1]
        #code = np.char.replace(np.unique(lst), '_1second', '').tolist()

        if filterMty:
            code = [c for c in code if 'F' in c ]
        return code

    def getNTNB(self,filterMty=False,liqFilter=False):
        # raise('update query')

        lst = self.assetVS.list_symbols(name={'$regex': 'NTNB_.*'}, maturity={'$gte': dt(2000, 1, 1)})

        code = np.char.replace(np.unique(lst), '_1BDay', '').tolist()
        return code

    def readDI(self,filterMty=True,liqFilter=False):
        # code=code[:50]
        code=self.getDI(filterMty,liqFilter)
        with uu.Timer():
            dfs = self.read(code)
        return dfs



    def delete(self,name,freq,library,deleteMeta=None):

        if isinstance(library,str):
            library=getattr(self,library)

        library.delete(name + '_' +freq)

        library1 = getLibraryName(library)
        if deleteMeta is None:
            deleteMeta=uu.query_yes_no('Delete meta for {}/{}'.format(name,library1), default="yes")

        if deleteMeta:
            r=self.mongoCli.db_dws.mgmt.metadata.delete_one(dict(name=name,library=library1))

            if not r.raw_result['ok']==1:
                print('Error deleting metadata')


    def xlMetaAsset(self):
        df=self.findAsset(library=[self.assetVS,self.assetTS,self.assetTS2])
        uu.writeXL('metaAsset',df)

    def xlMetaFundamental(self):
        df=self.findFundamental()
        uu.writeXL('metaFund',df)


    def xlSeries(self,name,freq,date_range=None):
        df = self.read(name,freq,date_range=date_range)
        uu.writeXL(name+'_'+freq,df)

    @staticmethod
    def _getDFfromList(lst,flds,flds1):
        lst_=[]
        if lst.size>0:
            for fld in flds:
                lst_.append([l[fld] if fld in l else None for l in lst[:,2]])

            for fld in flds1:
                lst_.append([getattr(l,fld)  for l in lst[:,2]])

            lst1 = np.c_[lst[:,[0]],np.array(lst_,dtype=object).T]
            df = pd.DataFrame(lst1,lst[:,1],columns=['library']+flds+flds1)
        else:
            df = pd.DataFrame([],[],columns=['library']+flds+flds1)

        df.index=df.name+'_'+df.freq
        return df
    def findAsset(self,name=None,freq=None,library=None,metadata=True,date_range=None,include_options=True,**kwargs):
        kwargs0=kwargs.copy()
        kwargs['cls'] = ['mDataStore.mongo.mongo.metadataAsset','mDataStore.mongo.mongo.metadataStrategy','mDataStore.mongo.metadataAsset','mDataStore.mongo.metadataStrategy']
        if include_options:
            kwargs['cls']+=['mDataStore.mongo.mongo.metadataOption','mDataStore.mongo.metadataOption']
        kwargs['cls']={'$in':kwargs['cls']}
        lst=self.find(name,freq,library,metadata,date_range,**kwargs)

        #lst1=lst[:,[1,0]]
        flds=['name','type','subtype','freq','stDT','endDT','currency','fut_like','maturity','cls']
        flds1 = ['firstDT', 'lastDT']

        df=mongoDS._getDFfromList(lst, flds, flds1)

        df.index=df.name+'_'+df.freq
        if name is None and freq is None and library is None and metadata and \
            date_range is None and include_options and not kwargs0:
            self.obj.save('assetDF',df,dt=dt.now().replace(hour=0,minute=0,second=0, microsecond=0))

        return df

    def findFundamental(self,name=None,freq=None,library=None,metadata=True,date_range=None,**kwargs):
        kwargs0=kwargs.copy()
        kwargs['cls'] = ['mDataStore.mongo.metadataFundamental',]
        kwargs['cls']={'$in':kwargs['cls']}
        lst=self.find(name,freq,library,metadata,date_range,**kwargs)

        #lst1=lst[:,[1,0]]
        flds=['name','type','subtype','freq','stDT','endDT','currency','cls']
        flds1 = ['firstDT', 'lastDT']

        df=mongoDS._getDFfromList(lst, flds, flds1)
        if name is None and freq is None and library is None and metadata and \
            date_range is None  and not kwargs0:
            self.obj.save('fundamentalDF',df,dt=dt.now().replace(hour=0,minute=0,second=0, microsecond=0))


        return df

    def findOption(self,name=None,freq=None,library=None,metadata=True,date_range=None,**kwargs):
        lst=self.find(name,freq,library,metadata,date_range,**kwargs)


    def find(self,name=None,library=None,date_range=None,**kwargs):
        '''
        :param name:
        :param freq:
        :param library:
        :param metadata:
        :param date_range: list - [start, end]. Will include all records such that there is some date in interval
                            [start,end], according to stDT and endDT stored in metadata
        :param kwargs:
        :return:
        '''
        kwargs1=kwargs
        if not name is None:
            kwargs1['name']=name

        if not library is None:
            library1=getLibraryName(library)
            kwargs1['library']=library1
        else:
            library1 = None

        if date_range:
            if library1 is None:
                raise(Exception('Must specify library to query for date_range'))

            kwargs1['stDT_'+library1] = {'$not':{'$gt':date_range[1]}}
            kwargs1['endDT_'+library1] = {'$not':{'$lt': date_range[0]}}
            kwargs1['maturity'] = {'$not': {'$lt': date_range[0]}}

        lst=list(self.mongoCli.db_dws.mgmt.metadata.find(kwargs1))

        return lst


    def appendIfCheck(self,df,date_range,library=None,check_metadata=True,keep_metadata=False, prune_previous_version=True,replaceIntersection=False,lastChkDate=None,**kwargs):
        if not isinstance(df,mDataFrame):
            md=df.md
            df=mDataFrame(df)
            df.md=md

        if isinstance(library,str):
            library = getattr(self,library)


        try:
            df1 = self.read(df.md.name, df.md.freq, library=library, date_range=date_range)
            ################################ fix ###############################
            if not 'endDT' in df1.md or df1.md.endDT != df.index[-1]:
                df1.md.endDT = df.index[-1]
                self.write_metadata(df1.md,library=library)
            ##################################################################
            if not lastChkDate is None:
                df1=df1.loc[df1.index<=lastChkDate]
        except Exception as e:
            import traceback
            traceback.print_exception(type(e),e,e.__traceback__)
            warn('Unable to read {}/{}'.format(df.md.name, df.md.freq))
            successi = False
            return successi

        df_ = df[df1.columns]
        df_, df2 = df_.align(df1, join='inner')
        ############
        df_.md=None
        df2.md = None
        for i,c in enumerate(df2.columns):
            df_[c] =df_[c].astype(df2[c].dtype)
        #############
        I1=df_.isna()|df2.isna()
        df_[I1]=np.nan
        df2[I1] = np.nan
        if 'volume' in df_:
            del df_['volume']
            del df2['volume']
        if 'open_interest' in df_:
            del df_['open_interest']
            del df2['open_interest']


        if df_.shape[0]==0:
            successi = True
        elif df_.equals(df2):
            dff = df.loc[df.index > df2.index[-1]]
            if dff.shape[0]>0:
                if isinstance(library, arclib.arctic.tickstore.TickStore):
                    self.append(dff, library=library, check_metadata=check_metadata,replaceIntersection=replaceIntersection, **kwargs)
                else:
                    self.append(dff, library=library, check_metadata=check_metadata,replaceIntersection=replaceIntersection, prune_previous_version=prune_previous_version,**kwargs)
            successi = True
        else:
            successi = False
        return successi

    def append(self,df,library=None,check_metadata=True,keep_metadata=False,replaceIntersection=False,**kwargs):
        checkDF(df)

        if not isinstance(df,mDataFrame):
            md=df.md
            df=mDataFrame(df)
            df.md=md

        #checkDF(df)
        assert(library)

        if isinstance(library, string_types):
            library = self.arctic[library]

        id = df.md.name + '_' + df.md.freq
        if df.shape[0] == 0:
            warn('No data added for {} - df to insert was Null'.format(id))

        md_ant = self.read_metadata(df.md.name, df.md.freq, library)

        if check_metadata:
            if md_ant:
                md_ant1 = {k: v for k, v in md_ant.items() if
                           not k.startswith('stDT') and not k.startswith('endDT')}
                md1 = {k: v for k, v in df.md.items() if not k.startswith('stDT') and not k.startswith('endDT')}
                assert (md_ant1 == md1)  # change to ignore stDT e endDT




        if isinstance(library, arclib.arctic.tickstore.TickStore):
            if not df.index.tz:
                df.index = df.index.tz_localize(pytz.timezone('GMT'))  # Brazil/East

        force_write=False

        if md_ant:
            met1 = md_ant
            if (not replaceIntersection) and isinstance(library, arclib.tickstore.tickstore.TickStore):
                # assert(not replaceIntersection)

                dti = library.min_date(id)
                dtf = library.max_date(id)
                df = df[(df.index < dti) | (df.index > dtf)]
            elif not replaceIntersection and not isinstance(library, arclib.arctic.tickstore.TickStore):
                df2 = self.read(df.md.name,df.md.freq,library)
                dti = df2.index[0]
                dtf = df2.index[-1]
                df = df[(df.index < dti) | (df.index > dtf)]
            elif replaceIntersection and not isinstance(library, arclib.arctic.tickstore.TickStore):
                df2 = self.read(df.md.name, df.md.freq, library)
                dti = df.index[0]
                dtf = df.index[-1]
                df2 = df2[(df2.index < dti) | (df2.index > dtf)]
                md=df.md
                df=pd.concat([df2,df])
                df.md=md
                force_write=True

            else:
                pass
        updateDts(df, md_ant)

        if not keep_metadata:
            self.write_metadata(df.md, library, onlyGlobal=True)
        if df.shape[0] != 0:
            if replaceIntersection and isinstance(library,arclib.tickstore.tickstore.TickStore) :
                def call_fcn(*args,**kwargs):
                    return mongoDS.TS_appendDFWreplace(library, *args,**kwargs)
            elif isinstance(library,arclib.tickstore.tickstore.TickStore) or force_write:
                call_fcn=library.write
            else:
                call_fcn = library.append
            df=df.sort_index()
            if keep_metadata and l1.size > 0:
                call_fcn(id, df, **kwargs)
            else:
                if 'date_range' in kwargs:
                    kwargs.pop('date_range')
                call_fcn(id, df, metadata=df.md, **kwargs)

        else:
            warn('No data added for {} - data was already in DB'.format(id))

    def write(self, df, library=None, check_metadata=True, keep_metadata=False, **kwargs): # prune_previous_version=True

        if not isinstance(df, mDataFrame):
            md = df.md
            df = mDataFrame(df)
            df.md = md

        checkDF(df)
        assert(library)
#         if not library:
# #            library = df.md.library
# #            if library is None:
#             library=df.md.getLibrary()
        if isinstance(library, string_types):
            library = self.arctic[library]

        id = df.md.name+'_'+df.md.freq
        if df.shape[0] == 0:
            warn('No data added for {} - df to insert was Null'.format(id))

        md_ant = self.read_metadata(df.md.name,df.md.freq, library)

        if check_metadata:
            if md_ant:
                md_ant1={k:v for k,v in md_ant.items() if not k.startswith('stDT') and not k.startswith('endDT')}
                md1={k:v for k,v in df.md.items() if not k.startswith('stDT') and not k.startswith('endDT')}
                assert(md_ant1 == md1) # change to ignore stDT e endDT

        updateDts(df, md_ant)

        uu.cast_types2basic(df.md)
        # if isinstance(df.md.endDT,(np.int32,np.int64)):
        #     df.md.endDT=int(df.md.endDT)
        # if isinstance(df.md.stDT,(np.int32,np.int64)):
        #     df.md.stDT=int(df.md.stDT)

        if df.shape[0]!=0:
            if keep_metadata and l1.size>0:
                library.write(id, df, **kwargs)
            else:
                if isinstance(library,arclib.tickstore.tickstore.TickStore):
                    library.write(id, df, metadata=df.md, **kwargs)
                else:
                    try:
                        library.write(id,df,metadata=df.md,**kwargs)
                    except Exception as e:
                        import traceback
                        traceback.print_exception(type(e),e,e.__traceback__)
                        kwargs2=kwargs.copy()
                        try:
                            kwargs2.pop('prune_previous_version')
                            warn('UNABLE TO PRUNE WHILE writing for {}'.format(id))
                        except:
                            pass
                        library.write(id, df, metadata=df.md, **kwargs2)

                self.write_metadata(df.md,library,onlyGlobal=True)

        else:
            warn('No data added for {} - data was already in DB'.format(id))

    def _adjustMetadataOnWrite(self,md0,library):
        md1 = copy(md0)
        md1.library = getLibraryName(library)
        md1.pop('freq')
        if 'stDT' in md1:
            md1['stDT' + '_' + md1.library] = md1.pop('stDT')
        if 'endDT' in md1:
            md1['endDT' + '_' + md1.library] = md1.pop('endDT')
        return md1
    def mapLibraryGlobalMetadata(self,library):
        if not isinstance(library,str):
            library = getLibraryName(library)
        return library if library != 'assetTS2' else 'assetVS'

    def write_metadata(self,metadata,library,onlyGlobal=False):

        # if library is None:
        #     library = metadata.getLibrary()
        if isinstance(library, string_types):
            library = self.arctic[library]

        if not onlyGlobal:
            symbol=metadata.name+'_'+metadata.freq
            if isinstance(library,arclib.tickstore.tickstore.TickStore):
                library._metadata.replace_one({SYMBOL: symbol},
                                           {SYMBOL: symbol, META: metadata},
                                           upsert=True)

            else:
                library.write_metadata(symbol,metadata)

        library1 = getLibraryName(library)
        library1 = self.mapLibraryGlobalMetadata(library1)
        md1 = self._adjustMetadataOnWrite(metadata, library1)

        r=self.mongoCli.db_dws.mgmt.metadata.replace_one(dict(name=md1.name,library=library1), md1, upsert=True)
        if r.raw_result['ok'] != 1:
            raise Exception('UNABLE TO UPSERT meta(mongo) {}'.format(md1['name']))



    def readi(self,name,freq=f.minute,library='assetTS2',date_range=None,merge_mode=None,tz=None,treatCloseNA='drop',**kwargs):

        if date_range is None:
            dt1 = dt.now().replace(hour=0, minute=0, second=0, microsecond=0)+datetime.timedelta(2)
            dt0 = dt1 - datetime.timedelta(3*252+2)
            date_range = [dt0,dt1]

        return self.read(name,freq=freq,library=library,date_range=date_range,merge_mode=merge_mode,tz=tz,treatCloseNA=treatCloseNA,**kwargs)

    def readio(self,name,freq=f.minute,library='onlineTS',date_range=None,merge_mode=None,tz=None,treatCloseNA='drop',**kwargs):
        return self.readi(name,freq=freq,library=library,date_range=date_range,merge_mode=merge_mode,tz=tz,treatCloseNA=treatCloseNA,**kwargs)

    def reado(self,name,freq=f.bday,library='onlineVS',date_range=None,merge_mode=None,tz=None,treatCloseNA='drop',**kwargs):
        return self.read(name,freq=freq,library=library,date_range=date_range,merge_mode=merge_mode,tz=tz,treatCloseNA=treatCloseNA,**kwargs)


    def read(self,name,freq=f.bday,library='assetVS',columns=None,date_range=None,merge_mode=None,tz=None,treatCloseNA='drop',**kwargs):
        '''
        :param name: list of strings or string
        :param freq:  list of strings or string
        :param library: list of strings or string
        :param columns: list of strings or string
        :param date_range:
        :param kwargs:
        :param kwargs:
        :return:
        '''
        #version store: as_of=None, date_range=None, from_version=None, allow_secondary=None
        #tickstore: date_range=None, columns=None, include_images=False, allow_secondary=None
        if isinstance(tz,str):
            tz=pytz.timezone(tz)
        if isinstance(date_range,list) or isinstance(date_range,tuple):
            date_range=list(date_range.copy())

            if date_range[0] and date_range[1]:
                date_range[0]=pd.to_datetime(date_range[0])
                date_range[1]=pd.to_datetime(date_range[1])
                if date_range[1].tzinfo and not date_range[0].tzinfo:
                    tz1=pytz.timezone(date_range[1].tzinfo.zone)
                    date_range[0]=pd.to_datetime(date_range[0]).tz_localize(tz1,True,'shift_backward' )
                if date_range[0].tzinfo and not date_range[1].tzinfo:
                    tz1=pytz.timezone(date_range[0].tzinfo.zone)
                    date_range[1]= (pd.to_datetime(date_range[1])+pd.Timedelta('1 day') ).tz_localize(tz1,True,'shift_backward' )

            date_range=DateRange(date_range[0],date_range[1])

        if isinstance(name, list) or isinstance(name, tuple):
            df_=[]
            for i,name_ in enumerate(name):
                if isinstance(freq, string_types):
                    per_ = freq
                else:
                    per_=freq[i]
                try:
                    df_.append(self.read(name_,per_,library,columns,date_range,merge_mode,**kwargs))
                except:
                    warn('unable to read {} (list read)'.format(name_))
            return df_
            # for d_ in df_:
            #     for j,c in enumerate(d_.columns):
            #         c=df_.md.name + '_' +c
            #
            # if len(df_)>1:
            #     return df_[0].join(df_[1:],how=merge_mode)
            # else:
            #     return df_[0]
        if isinstance(library,list):
            for i,l in enumerate(library):
                try:
                    df=self.read( name, freq, l, columns, date_range, merge_mode, **kwargs)
                    return df
                except:
                    if i==len(library)-1:
                        raise
                    continue

        # if not library:
            # lst = self.find(name, freq,metadata=False)
            # assert(lst.size>0)
            # library = self.arctic[lst[0,0]]
            # library = self._getLibraryOnRead(name,freq)[0]


        # if not self.read_metadata(name,freq,library) is None:
        #     return _convTypes(self.read_(name,freq,library,columns,date_range,merge_mode,tz,**kwargs))
        # else:
        try:
            df = self.read_(name, freq, library, columns, date_range, merge_mode, tz, treatCloseNA, **kwargs)
            return _convTypes(df)
        except:
            pass

        print('Aggregating higher frequency on read')
        nfreq,sfreq=splitFreq(freq)

        # if 'minute' in sfreq.lower() and nfreq%10==0:
        #     freqBase=f.minute10
        if 'minute' in sfreq.lower():
            freqBase = f.minute
        elif 'second' in sfreq.lower() and nfreq!=1:
            freqBase = f.second
        elif 'day' in sfreq.lower() and nfreq!=1:
            freqBase = f.bday
        elif 'month' in sfreq.lower() or 'quarter' in sfreq.lower() or 'year' in sfreq.lower():
            freqBase = f.bday
        else:
            freqBase = freq
            # raise Exception('Unable to find series {}-{} and there is also no convertion possible'.format(name,freq))

        df=self.read_(name, freqBase, library, columns, date_range, merge_mode, tz,treatCloseNA, **kwargs)
        if freqBase != freq:
            return convertFreq(_convTypes(df),freq)
        else:
            return _convTypes(df)

    def read_metadata(self,name,freq,library):
        library0 = getLibraryName(library)
        library1 = self.mapLibraryGlobalMetadata(library0)
        library_=getattr(self,library1)
        meta1 = self.mongoCli.db_dws.mgmt.metadata.find_one(dict(name=name,library=library1))
        if meta1 is None:
            if not isinstance(library_,arclib.tickstore.tickstore.TickStore):
                try:
                    meta1 = library_.read_metadata(name+'_'+freq).metadata
                    meta1 = locate(meta1['cls'])(meta1)
                    warn('Using metadata from the assetVS base !')
                except:
                    pass
            else:
                try:
                    meta1=library_._metadata.find_one({'sy': name+'_'+freq}, {'_id': 0, 'sy': 0})['md']
                    meta1 = locate(meta1['cls'])(meta1)
                    warn('Using metadata from the assetVS base !')
                except:
                    pass

            return meta1

        meta1.pop('library')

        meta1['freq'] = freq
        if 'stDT' + '_' + library0 in meta1:
            meta1['stDT'] = meta1['stDT' + '_' + library1]
        else:
            meta1['stDT'] = None
        if 'endDT' + '_' + library0 in meta1:
            meta1['endDT'] = meta1['endDT' + '_' + library1]
        else:
            meta1['stDT'] = None

        meta1 = locate(meta1['cls'])(meta1)
        return meta1


    def read_(self,name,freq=f.bday,library=None,columns=None,date_range=None,merge_mode=None,tz=None,treatCloseNA='drop',**kwargs):

        if isinstance(library,str):
            library=getattr(self,library)

        id=name + '_' + freq
        if isinstance(library,arclib.arctic.tickstore.TickStore):

            if not date_range is None:
                dt0_ = pd.Timestamp(date_range[0]) if not date_range[0] is None else pd.Timestamp(dt(1900,1,1))
                dt1_ = pd.Timestamp(date_range[1]) if not date_range[1] is None else pd.Timestamp(dt(2200, 1, 1))
                if dt0_.tz is None and not dt1_.tz is None:
                    dt0_=pd.Timestamp(dt0_)
                    dt0_=dt0_.tz_localize(dt1_.tz)
                elif dt1_.tz is None and not dt0_.tz is None:
                    dt1_=pd.Timestamp(dt1_)
                    dt1_=dt1_.tz_localize(dt0_.tz)

                date_range=deepcopy(date_range)
                date_range.start=dt0_
                date_range.end = dt1_
            try:
                rdf = library.read(id, columns=columns, date_range=date_range, **kwargs)
            except arctic.exceptions.NoDataFoundException:
                rdf = library.read(id, columns=columns, **kwargs)
                # rdf = pd.DataFrame(index=pd.to_datetime([]), data=np.zeros((0, 1)), columns=['close'])
                rdf=rdf.iloc[0:0]
                rdf.index = rdf.index.tz_convert(tzInsert)
            except:
                try:
                    rdf = library.read(id, columns=columns, date_range=date_range, **kwargs)
                except:
                    rdf = library.read(id, columns=columns, date_range=date_range, **kwargs)

            # rdf.index=rdf.index.tz_convert('GMT').tz_localize(None).tz_localize(tzInsert)
            # print('Time adjustment (fix DB)')

            df =mDataFrame(rdf)
            # meta1=library.read_metadata(id)
            meta1=self.read_metadata(name,freq,library)

            df.md=meta1
            ########
            # tzG=df.index.tz
            tzG = pytz.timezone(df.index.tz.zone)
            # tzG = pytz.timezone('GMT')
            # if df.index.tz!=tzG:
                #delta1 = pd.to_timedelta(df.gmt_off, unit='h')
                #df.index = df.index - delta1
                # warn('forcing to GMT')

                #df.index = df.index.tz_localize(None).tz_localize(tz)
                #mutreta para converter duas vezes. O ajuste esta errado na base. Eh necessario refazer a base
                # df.index=df.index.tz_convert(tzG)
                # df.index = df.index.tz_localize(None).tz_localize(pytz.timezone('Brazil/East'))
                # df.index=df.index.tz_convert(tzG)
            # from tzlocal import get_localzone
            # local_tz = get_localzone()


            if isinstance(df.md.stDT, dt):
                df.md.stDT = tzG.localize(df.md.stDT)
            if isinstance(df.md.endDT, dt):
                df.md.endDT = tzG.localize(df.md.endDT)
            if not tz is None:
                df.index=df.index.tz_convert(tz)
                if isinstance(df.md.stDT, dt):
                    df.md.stDT = df.md.stDT.astimezone(tz)
                if isinstance(df.md.endDT, dt):
                    df.md.endDT =df.md.endDT.astimezone(tz)
        #######
        else:
            date_range1=deepcopy(date_range)

            if not date_range1 is None:
                if isinstance(date_range1.start,pd.Timestamp):
                    date_range1.start=date_range1.start.normalize()
                    date_range1.start=date_range1.start.tz_localize(None)
                if isinstance(date_range1.end,pd.Timestamp):
                    date_range1.end=date_range1.end.normalize()
                    date_range1.end = date_range1.end.tz_localize(None)
            try:
                rdf=library.read(id,date_range=date_range1, **kwargs)
            except arctic.exceptions.NoDataFoundException:
                # rdf = pd.DataFrame(index=pd.to_datetime([]), data=np.zeros((0, 1)), columns=['close'])
                rdf = library.read(id, columns=columns, **kwargs)
                # rdf = pd.DataFrame(index=pd.to_datetime([]), data=np.zeros((0, 1)), columns=['close'])
                rdf=rdf.iloc[0:0]

            if columns:
                rdf.data=rdf.data[columns]

            df =mDataFrame(rdf.data)
            if not date_range1 is None:
                dt0_ = date_range1[0] if not date_range1[0] is None else dt(1900,1,1)
                dt1_ = date_range1[1] if not date_range1[1] is None else dt(2200, 1, 1)
                df=df.loc[(df.index>=dt0_)&(df.index<=dt1_)]

            meta1=self.read_metadata(name,freq,library)

            df.md=meta1#locate(rdf.metadata['cls'])(meta1)
        # if any(df.index != df.index.normalize()):
        #     if isinstance(tz,str):
        #         tz=pytz.timezone(tz)
        #     df.index=df.index.tz_convert(tz)

        # df.md.getDates()
        checkDF(df)
        df1=df.sort_index()

        if 'close' in df1:
            close_cols = ['close']

            if treatCloseNA.lower() == 'drop':
                if 'yield_close' in df1:
                    close_cols.append('yield_close')

                df1.dropna(subset=close_cols,how='all',inplace=True)
            else:
                df1.close.fillna(method=treatCloseNA,inplace=True)

        if not df1.values.flags.c_contiguous: #return must be contiguous array
            md = df1.md
            df1 = mDataFrame(np.ascontiguousarray(df1.values),df1.index,df1.columns)
            df1.md=md


        return df1


    def runScript(self,script):
        os.chdir(os.path.dirname(bloomberg.__file__) + '/scripts')

        cmd = ['mongo', '--host', self.mongoCli.primary[0] + ':{}'.format(self.mongoCli.primary[1]),
               script]
        result = subprocess.run(cmd, stdout=subprocess.PIPE)
        out=result.stdout.decode('utf-8')
        out1 = out.split('\r\n')
        if len(out1)>3:
            out="\r\n".join(out1[3:])
        else:
            out=""

        return out,result

    def getRSConfig(self):
        #cmd=['mongo', '--host',self.mongoCli.primary[0]+':{}'.format(self.mongoCli.primary[1]),'--eval','"rs.config()"']
        out,result=self.runScript('rsconfig.js')
        out=out.replace('false','False')
        out=out.replace('true','True')
        out=out.replace('ObjectId','')
        out=out.replace('NumberLong','')

        return eval(out)


    def setPrimary(self,newPrimHost,primPriority=1,secPriority=0.5):
        cfg=self.getRSConfig()

        primHost=self.mongoCli.primary[0]
        curPrimId=-1
        newPrimId=-1
        #find indexes for new and old primary (only needs new!)
        for i,ci in enumerate(cfg['members']):
            s=ci['host'].split(':')
            if newPrimHost==s[0]:
                newPrimId=i
            if primHost == s[0]:
                curPrimId = i
        assert(curPrimId>=0 and newPrimId>=0)

        #generate script
        script=['cfg = rs.conf()']
        for i,ci in enumerate(cfg['members']):
            if i==newPrimId:
                p=primPriority
            else:
                p=secPriority+np.round(np.random.normal(0,1,1),4)[0]/100
            str = 'cfg.members[{}].priority ={}'.format(i,p)
            script.append(str)

        script.append('printjson(rs.reconfig(cfg))')
        script = '\r\n'.join(script)

        #save and run script in old primary
        os.chdir(os.path.dirname(bloomberg.__file__) + '/scripts')
        with open('priority.js','w') as scriptFile:
            scriptFile.write(script)

        ret=self.runScript('priority.js')

        return ret

    @staticmethod
    def TS_deleteDateRange(libTS, symbol, date_range, df):
        # self=mds.assetTS

        import arctic as arclib

        DateRange = arclib.date.DateRange

        to_pandas_closed_closed = arclib.date.to_pandas_closed_closed
        SYMBOL = arclib.tickstore.tickstore.SYMBOL
        INDEX = arclib.tickstore.tickstore.INDEX
        START = arclib.tickstore.tickstore.START
        END = arclib.tickstore.tickstore.END

        # date_range=dt_rg
        query = {SYMBOL: symbol}
        date_range = to_pandas_closed_closed(date_range)
        assert date_range.start and date_range.end
        query[START] = {'$lte': date_range.end}
        query[END] = {'$gte': date_range.start}

        cur = libTS._collection.find(query)
        res = [c for c in cur]

        dt_start = min([r[START] for r in res])
        dt_end = max([r[END] for r in res])

        tz = date_range.start.to_pydatetime().tzinfo
        dt_start = dt_start.replace(tzinfo=datetime.timezone.utc).astimezone(tz)
        dt_end = dt_end.replace(tzinfo=datetime.timezone.utc).astimezone(tz)

        # dt_rng1=to_pandas_closed_closed(ds.DateRange(dt_start,dt_end))

        df0 = df.loc[dt_start:dt_end]
        uu.save_obj(df0, 'recoverDeleted')
        df_rep = df0[(df0.index > date_range.end) | (df0.index < date_range.start)]
        uu.save_obj(df_rep, 'recoverTorecover')

        # dt_start1=df.index[df.index.get_loc(df0.index[0])-1]
        # dt_end1=df.index[df.index.get_loc(df0.index[-1])+1]
        rdel = libTS.delete(symbol, date_range=DateRange(dt_start, dt_end))
        libTS.write(symbol,df_rep)
        return rdel




    @staticmethod
    def TS_appendDFWreplace(libTS, symbol, df,*args,**kwargs):
        # self=mds.assetTS
        #dt1 = pd.Timestamp(dt(2050,1,1))
        if df.shape[0] ==0:
            return
        from tzlocal import get_localzone
        local_tz = get_localzone()

        df=df.tz_convert(local_tz)
        # from tzlocal import get_localzone  # $ pip install tzlocal
        # assert date_range.start>=df.index[0] and date_range.end<=df.index[0].index[-1]
        import arctic as arclib
        DateRange = arclib.date.DateRange
        utc_dt_to_local_dt= arclib.date.utc_dt_to_local_dt
        date_range = DateRange(df.index[0],df.index[-1])


        to_pandas_closed_closed = arclib.date.to_pandas_closed_closed
        SYMBOL = arclib.tickstore.tickstore.SYMBOL
        INDEX = arclib.tickstore.tickstore.INDEX
        START = arclib.tickstore.tickstore.START
        END = arclib.tickstore.tickstore.END

        # date_range=dt_rg
        query = {SYMBOL: symbol}
        date_range = to_pandas_closed_closed(date_range)
        assert date_range.start and date_range.end

        query[START] = {'$lte': date_range.end} #any intersection
        query[END] = {'$gte': date_range.start}

        cur = libTS._collection.find(query)
        res = [c for c in cur]


        if len(res) >0:
            dt_start = min([r[START] for r in res])
            dt_end = max([r[END] for r in res])
            dt_start1=utc_dt_to_local_dt(dt_start)
            dt_end1 = utc_dt_to_local_dt(dt_end)
            # tz = date_range.start.to_pydatetime().tzinfo
            # dt_start = dt_start.replace(tzinfo=datetime.timezone.utc).astimezone(tz)
            # dt_end = dt_end.replace(tzinfo=datetime.timezone.utc).astimezone(tz)

            # dt_rng1=to_pandas_closed_closed(ds.DateRange(dt_start,dt_end))
            # df_ = df.copy()
            if dt_start1< df.index[0]:
                df0 = libTS.read(symbol,date_range=DateRange(dt_start1,df.index[0]))
                df0=df0.iloc[:-1]
                df0=df0.tz_convert(local_tz)
                df=pd.concat([df0,df],axis=0)
            if dt_end1> df.index[-1]:
                df1 = libTS.read(symbol,date_range=DateRange(df.index[-1],dt_end1))
                df1=df1.iloc[1:]
                df1 = df1.tz_convert(local_tz)
                df=pd.concat([df,df1],axis=0)

            # df0 = df.loc[dt_start:dt_end]
            # uu.save_obj(df0, 'recoverDeleted')
            # df_rep = df0[(df0.index > date_range.end) | (df0.index < date_range.start)]
            # uu.save_obj(df_rep, 'recoverTorecover')

            # dt_start1=df.index[df.index.get_loc(df0.index[0])-1]
            # dt_end1=df.index[df.index.get_loc(df0.index[-1])+1]
            # rdel = libTS.delete(symbol, date_range=DateRange(dt_start, dt_end))
            libTS._collection.delete_many(query)

        libTS.write(symbol,df,*args,**kwargs)
        # return rdel


# def read

# function signature correction, passing [md_ant] parameter
# sazevedo on 2019-10-29
#



def updateDts(df, md_ant):
    df = df.sort_index()

    if df.index.shape[0] > 0:
        df.md.endDT = df.index[-1]
        if md_ant and not md_ant.stDT is None:
            df.md.stDT = np.minimum(df.index[0], md_ant.stDT)
        else:
            df.md.stDT = df.index[0]
    else:
        df.md.stDT = None
        df.md.endDT = None


def splitFreq(freq):
    m=re.match(r'\d+',freq)
    if m:
        sfreq= freq[m.end():]
        nfreq=int(freq[:m.end()])
    else:
        sfreq=freq
        nfreq=1
    return nfreq,sfreq

# if not 'localhost' in globalM.mongoStr:
#     mds=mongoDS(replicaSet='r1') #,readPreference='nearest'
# else:
#     mds = mongoDS()

#try:

# except:
#     warn('UNABLE TO START MONGO-DB. Setting mds=None')
#     mds=None

#
# class mongoISADB(mongoObjDB):
#     #DB for Indiactors, Strategies and Assets
#     def __init__(self,mds,base='all',types=None,freqs=None,date_range=None):
#         self.mongoCli=_mongo
#         self.base=base
#         self.types=types
#         self.date_range=date_range
#
#         colNames=self.mongoCli[DB_OBJ].list_collection_names()
#         self.subColNames= [c[len(self.base)+1:].split('.')[0] for c in colNames if c.startswith(self.base+'.')]
#         #aa
#         self.mds=mds
#         freqs1=np.array([[item,getattr(f,item)] for item in dir(f) if not item.startswith("__")])
#
#         assets = np.array([[v.replace('.','_').replace(' ','_'),v] for v in mds.assetDF.index.values])
#         self.freqs=pd.DataFrame(freqs1[:,0],freqs1[:,1],['val'])
#         self.assets=pd.DataFrame(assets[:,0],assets[:,1],['val'])
#
#         self.freqs=self.freqs.loc[self.mds.assetDF.freq.unique()]
#         if freqs:
#             self.freqs=self.freqs.loc[freqs]
#
#         if not types and not 'indicator' in self.base:
#             types = self.mds.assetDF.type.unique().tolist()
#         if types and len(types)>1:
#             for typ in types:
#                 setattr(self,typ,mongoISADB(self.mds,base=self.base,types=[typ],freqs=freqs,date_range=date_range))
#
#         if self.freqs.shape[0] >1:
#             for freq in self.freqs.index:
#                 setattr(self,freq,mongoISADB(self.mds,base=self.base,types=types,freqs=[freq],date_range=date_range))
#
#         for c in self.subColNames:
#             setattr(self, c, mongoISADB(self.mds, base=self.base+'.'+c, types=self.types,freqs=freqs, date_range=self.date_range))
#
#     @staticmethod
#     def _getType(obj):
#         from strategy import strategy
#         from indicator import indicator
#
#         typ = obj.__class__.__name__
#         if isinstance(obj,strategy):
#             typ0='strategy'
#         elif isinstance(obj,indicator):
#             typ0 = 'indicator'
#         else:
#             raise(Exception('UNSUPPORTED type for save {}'.format(typ)))
#
#         if typ0=='strategy':
#             typ0a='asset.strategy'
#         else:
#             typ0a =typ0
#         return typ, typ0, typ0a
#
#     def delete(self,name,path=None,**metadata):
#         super(mongoISADB,self).delete(name)
#         if name is self.mds.assetDF.name:
#             types = self.mds.type[name==self.mds.assetDF.name]
#             assert(len(types)==1)
#             assert (types[0] == 'strategy')
#             self.mds.delete(name)
#
#
#     def save(self,name,obj,path=None,**metadata):
#         from strategy import strategy
#         from asset import asset
#         from indicator import indicator
#
#         assert(isinstance(obj,asset) or isinstance(obj,indicator))
#
#         typ,typ0,typ0a=mongoISADB._getType(obj)
#         meta={}
#         assert((not isinstance(obj,asset) )or isinstance(obj,strategy))
#         if isinstance(obj,strategy):
#             meta['fut_like'] = obj.fut_like
#             if obj._dt.size>0:
#                 meta['stDT'] = uu.x2dti_date(obj._dt[0])
#                 meta['endDT'] = uu.x2dti_date(obj._dt[-1])
#             else:
#                 meta['stDT'] =None
#                 meta['endDT'] =None
#             meta['currency']=obj.currency
#
#         super(mongoISADB,self).save(obj.name,obj,
#                 type=typ0,freq=obj.freq,**meta,subtype=typ)
#
#         if isinstance(obj,strategy):
#             obj._mdf.md=metadataAsset(obj.name,typ0,meta['stDT'],meta['endDT'],
#                                    obj.currency,obj.fut_like,obj.maturity,obj.freq)
#             obj._mdf.md.firstDT=meta['stDT']
#             obj._mdf.md.lastDT = meta['endDT']
#
#             obj._mdf.subtype=typ
#             self.mds.write(obj._mdf)
#
#
#     def __getattr__(self, item):
#         from asset import asset
#         from strategy import strategy
#         val=item#self.names[item]
#         if val in super(mongoISADB,self).names:
#             obj=super(mongoISADB,self).__getattr__(val)
# #            obj.update()
#             return obj
#         else:
#             if len(self.freqs)==1:
#                 df=self.mds.read(val,freq=self.freqs[0],date_range=self.date_range)
#             else:
#                 df=self.mds.read(val,date_range=self.date_range)
#             if df.md.type=='strategy':
#                 return strategy(df)
#             else:
#                 return asset(df)
#
#     def __dir__(self):
#         lst=super(mongoISADB, self).__dir__()
#         if not 'indicator' in self.base:
#             df1=self.mds.assetDF
#             if self.types:
#                 df1=df1.loc[df1.type.isin(self.types)]
#
#             if self.freqs.size>0:
#                 df1 = df1.loc[df1.freq.isin(self.freqs.index)]
#
#
#             fval=df1.freq.unique()
#             nval=df1.name.unique()
#             fidx=self.freqs.index[self.freqs.val.isin(fval)]
#             #nidx = self.names.index[self.names.val.isin(nval)]
#             lst += fidx.tolist()
#             lst += nval.tolist()
#         return lst



#TODO: make fast update of metadata!
# lstVS=ds.mongo.findVS(mds.assetVS._versions)
# cur=mds.assetTS._metadata.find()
# lstTS = [c for c in cur]

def getLibraryName(l):
        return l if isinstance(l, string_types) else l._collection.name


def convertFreq(df1,freq=f.minute15,h_interval=None,label='right'):
    from copy import deepcopy

    if df1.shape[0]==0:
        return df1
    df1.index = uu.x2dti_date(df1.index)
    # freqPD=freq.lower().replace('minute','min').replace('second','sec')
    freqPD = freq.lower()
    for k,v in f.conv2pandas.items():
        freqPD=freqPD.replace(k,v)


    df2=mDataFrame(index=df1.index.to_series().resample(freqPD, label=label).last().index)
    # df2=df2.asfreq(freqPD)
    # df2 = pd.DataFrame(index=df1.index).asfreq(freqPD)

    # print('close..', end='')
    if 'close' in df1:
        df2['close'] = pd.DataFrame(df1.close.resample(freqPD, label=label).last())

    if 'yield_close' in df1:
        df2['yield_close'] = pd.DataFrame(df1.yield_close.resample(freqPD, label=label).last())

    if 'alpha_close' in df1:
        df2['alpha_close'] = df1.alpha_close.resample(freqPD, label=label).last()

    # print('open..', end='')
    if 'open' in df1:
        df2['open'] = df1.open.resample(freqPD, label=label).first()
    elif 'close' in df1:
        df2['open'] = df1.close.resample(freqPD, label=label).first()

    # print('high..', end='')
    if 'high' in df1:
        df2['high'] = df1.high.resample(freqPD, label=label).max()
    elif 'close' in df1:
        df2['high'] = df1.close.resample(freqPD, label=label).max()

    # print('low..', end='')
    if 'low' in df1:
        df2['low'] = df1.low.resample(freqPD, label=label).min()
    elif 'close' in df1:
        df2['low'] = df1.close.resample(freqPD, label=label).min()

    # print('vwap..', end='')
    if 'vwap' in df1:
        px_vwap=df1.vwap
    else:
        if 'close' in df1:
            px_vwap=df1.close
        elif 'yield_close' in df1:
            px_vwap=df1.yield_close
        else:
            px_vwap = None

    # print('volume..', end='')
    if 'volume' in df1:
        df2['volume'] = df1.volume.resample(freqPD, label=label).sum()
        if not px_vwap is None:
            df2['vwap'] = (px_vwap*df1.volume).resample(freqPD, label=label).sum()
            vol1=((~px_vwap.isna())*df1.volume).resample(freqPD, label=label).sum()
            df2['vwap'] = df2['vwap']/vol1
    else:
        if not px_vwap is None:
            df2['vwap'] = px_vwap.resample(freqPD, label=label).mean()

    # print('bid..', end='')
    if 'bid' in df1:
        df2['bid'] = df1.bid.resample(freqPD, label=label).last()

    if 'yield_bid' in df1:
        df2['yield_bid'] = pd.DataFrame(df1.yield_bid.resample(freqPD, label=label).last())

    # print('ask..', end='')
    if 'ask' in df1:
        df2['ask'] = df1.ask.resample(freqPD, label=label).last()

    if 'yield_ask' in df1:
        df2['yield_ask'] = pd.DataFrame(df1.yield_ask.resample(freqPD, label=label).last())


    colsAlreadyTreated=['close','alpha_close','yield_close','open','high','low','ask','bid','yield_ask','yield_bid','vwap','volume']

    cols = df1.columns.difference(colsAlreadyTreated)

    df2[cols]=df1[cols].resample(freqPD, label=label).last()

    # df2=df2.between_time('9:00','18:00')

    if not h_interval is None:
        df2 = df2.between_time(h_interval[0], h_interval[1])

    # II=df2.index.normalize().isin(df1.index.normalize())
    # df2=df2.loc[II]

    # print('dropna..', end='')
    if 'close' in df1 or 'yield_close'  in df1:
        # df2.close=df2.close.fillna(method='ffill')
        if 'close' in df1:
            df1.close[df1.close==0]=np.nan
            lst=['close']
        else:
            df1.yield_close[df1.yield_close==0]=np.nan
            lst = ['yield_close']

        if 'bid' in df2:
            lst.append('bid')
        if 'ask' in df2:
            lst.append('ask')
        df2 = df2.dropna(subset=lst,how='all')


    if 'alpha_close' in df1:
        df2.alpha_close=df2.alpha_close.fillna(method='ffill')

    df2.md=deepcopy(df1.md)
    df2.md.freq = freq
    # print('done convert..')
    df2.md.lastIndexBeforeConvertion=df1.index[-1]
    return df2




#@mongo_retry
def findVS(self, regex=None, as_of=None, **kwargs): #from list_symbols in store metadata
    """
     Return the symbols in this library.
     Parameters
     ----------
     as_of : `datetime.datetime`
        filter symbols valid at given time
     regex : `str`
         filter symbols by the passed in regular expression
     kwargs :
         kwarg keys are used as fields to query for symbols with metadata matching
         the kwargs query
     Returns
     -------
     String list of symbols in the library
    """

    # Skip aggregation pipeline
    # if not (regex or as_of or kwargs):
    #     return self.distinct('symbol')

    # Index-based query part
    index_query = {}
    if as_of is not None:
        index_query['start_time'] = {'$lte': as_of}

    if regex or as_of:
        # make sure that symbol is present in query even if only as_of is specified to avoid document scans
        # see 'Pipeline Operators and Indexes' at https://docs.mongodb.com/manual/core/aggregation-pipeline/#aggregation-pipeline-operators-and-performance
        index_query['symbol'] = {'$regex': regex or '^'}

    # Document query part
    data_query = {}
    if kwargs:
        for k, v in six.iteritems(kwargs):
            data_query['metadata.' + k] = v

    # Sort using index, relying on https://docs.mongodb.com/manual/core/aggregation-pipeline-optimization/
    pipeline = [{'$sort': {'symbol': pymongo.ASCENDING,
                           'start_time': pymongo.DESCENDING}}]

    # Index-based filter on symbol and start_time
    if index_query:
        pipeline.append({'$match': index_query})
    # Group by 'symbol' and get the latest known data
    pipeline.append({'$group': {'_id': '$symbol',
                                'metadata': {'$last': '$metadata'}}})
    # Match the data fields
    if data_query:
        pipeline.append({'$match': data_query})
    # Return only 'symbol' field value
    #pipeline.append({'$project': {'_id': 0, 'symbol': '$_id'}})



    return [r for r in self.aggregate(pipeline)]




###########DELETE###############
def move2assetTS2():
    from mDataStore.globalMongo import mds
    import mDataStore as ds
    lst=mds.find(freq=ds.freqHelper.minute,library=mds.assetTS)
    lst2=mds.find(freq=ds.freqHelper.minute10, library=mds.assetTS)
    lst=r_[lst,lst2]

    for i in range(lst.shape[0]):
        print('{}/{}'.format(i,lst.shape[0]))
        df=mds.read(lst[i,1],lst[i,2]['freq'],library=mds.assetTS,date_range=[dt(1999,1,1),dt.now()])
        mds.write(df,library=mds.assetTS2)
        df2=mds.read(lst[i,1],lst[i,2]['freq'],library=mds.assetTS2,date_range=[dt(1999,1,1),dt.now()])
        # assert(df.equals(df2))
        mds.delete(lst[i,1],lst[i,2]['freq'],library=mds.assetTS)


def _convTypes(df):
    for col in df.columns:
        try:
            df[col] = df[col].astype(np.float64)
        except:
            try:
                df[col] = df[col].astype(str)
            except:
                pass
    return df


def teste():
    from mDataStore.globalMongo import mds
    df = pd.DataFrame(zeros((5,5)))

    df = pd.DataFrame(zeros((5, 5)),index=arange(1,6),columns=[arange(2,7)] )
    df.md =  metadataFundamental('teste1')

    mds.write(df,library=mds.fundoVS)

    df=mds.read('teste1',library='fundoVS')

    mds.delete('teste1','1Bday',mds.assetVS)


def assetVS_update_multiplier():

    from mDataStore.globalMongo import mds

    df = mds.read("ESU9_OFF", library=mds.assetVS)

    lib = mds.find(library="assetVS")

    for asset in lib:

        md = asset[2]

        if md.type == 'equity':
            md.multiplier = 1.0
            md.minTrade = 100.0
            mds.write_metadata(md,library="assetVS")

        if md.type == 'future' and md.name.startswith('IND'):
            md.multiplier = 1.0
            md.minTrade = 1.0
            mds.write_metadata(md,library="assetVS")

        if md.type == 'future' and md.name.startswith('DOL'):
            md.multiplier = 50.0
            md.minTrade = 1.0
            mds.write_metadata(md,library="assetVS")

        if md.type == 'future' and md.name.startswith('ES'):
            md.multiplier = 50.0
            md.minTrade = 1.0
            mds.write_metadata(md,library="assetVS")

        if md.type == 'future' and md.name.startswith('TY'):
            md.multiplier = 1000.0
            md.minTrade = 1.0
            mds.write_metadata(md,library="assetVS")

        if md.type == 'future' and md.name.startswith('PE'):
            md.multiplier = 5000.0
            md.minTrade = 1.0
            mds.write_metadata(md,library="assetVS")

        if md.type == 'future' and md.name.startswith('ISP'):
            md.multiplier = 50.0
            md.minTrade = 1.0
            mds.write_metadata(md,library="assetVS")

        if md.type == 'future' and md.subtype == 'di_fut':
            md.multiplier = 1.0
            md.minTrade = 1.0
            mds.write_metadata(md,library="assetVS")


def metadata_first_load():

    from mDataStore.globalMongo import mds

    lib = mds.find(library="assetVS")

    for asset in lib:

        md1 = asset[2]
        md1.library = "assetVS"
        md1.pop('freq')
        mds.mongoCli.db_dws.mgmt.metadata.replace_one(dict(name=md1.name,library=md1.library), md1, upsert=True)


def metadata_insert_max_amount():

    from mDataStore.globalMongo import mds

    for curr in mds.mongoCli.db_dws.mgmt.metadata.find():

        md = Dict(curr)

        try:
            if md.type == 'future' and md.subtype == 'di_fut':
                print("Updating di_fut [max_amount] of: " + md.name)
                md.max_amount = 100000
                mds.mongoCli.db_dws.mgmt.metadata.replace_one(dict(_id=md._id), md, upsert=True)

            elif md.type == 'future' or md.type == 'equity':
                print("Updating " + md.type + " [max_amount] of: " + md.name)
                md.max_amount = 1000
                mds.mongoCli.db_dws.mgmt.metadata.replace_one(dict(_id=md._id), md, upsert=True)

        except DuplicateKeyError:
            warn("Duplicate error: " + md.name)


if __name__ == '__main__':
    # teste()

    # assetVS_update_multiplier()

    # metadata_first_load()

    from mDataStore.globalMongo import mds
    lst = mds.find(name='PETR4')

    lst1 = mds.find(library=mds.assetVS)


    lst2 = mds.find(date_range=[dt(2005,1,1),dt(2010,1,1)],library=mds.assetVS)


    a=1


    # metadata_insert_max_amount()