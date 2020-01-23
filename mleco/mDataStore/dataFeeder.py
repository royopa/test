from mDataStore.bloomberg import blp,blpEventHandler
from mDataStore.dataFeeder.dataComm import dataServer,dataClient
import xlwings as xw
from mDataStore.globalMongo import mds
import pandas as pd
import time
import mUtil as uu
DEBUG=True
from datetime import datetime as dt
import datetime
from dataclasses import dataclass, field
from dask.distributed import Client,LocalCluster,  get_worker
from mUtil import Dict
from warnings import warn
from numpy import *


class blpEventHandler1(blpEventHandler):
    def __init__(self, feeder:dataServer):
        self.feeder = feeder
        super(blpEventHandler1, self).__init__()

    def onBlpReceive(self, obj,topic, dti):
        #sending to everyone - try to separate
        if DEBUG:
            print('blp sending: {}'.format(obj))
        # if not hasattr(self,'ii'):
        #     self.ii=-1
        # self.ii+=1
        # obj1={}
        obj1 = {k:v for k,v in obj.items() if (isinstance(k,str) and isinstance(v,(dt,datetime.time,float,int,str))) }
        for k,v in obj1.items():
            try:
                if isinstance(v,dt):
                    v1=dt(int(v.year),int(v.month),int(v.day),int(v.hour),int(v.minute),int(v.second))

                elif isinstance(v,datetime.time):
                    v1=datetime.time(v.hour,v.minute,v.second)
                #     v1=v.replace(tzinfo=None)
                else:
                    v1=v
                obj1[k]=v1
            except Exception as e:
                print('Unable to include date: {}'.format(v))
                uu.printException(e)


        obj2 = {k:v for k,v in obj.items() if not k in obj1 }

        if len(obj2)>0:
            print('########################################################################################################################')
            print('Not Builtin: {}'.format(obj2))

            print(
            '########################################################################################################################')
        self.feeder.putData((topic,dti,obj1))

        # self.feeder.putData({'a':self.ii})
        #see structure, convert to df and save to tickstore
        # mds.obj.save('',obj,'mktdata.')

# @dataclass
# class intradayQuery():
#     name:str
#     security:str
#     freq:str='1Minute'
#     # startDate:dt
#     updateInterval:int=30
#     t0:float=time.time()
#     kwargs:dict=field(default_factory=dict)
#     addrs:list=field(default_factory=list)
#     event:str='TRADE'

class blpFeederServer(dataServer):

    def __init__(self,host,port,dailybarsUpdateInterval=5):

        self.startBLP()
        super(blpFeederServer,self).__init__(host,port)
        self.sublist={}
        self.t0=time.time()
        self.onlineTable = None

        self.dailybarsUpdateInterval=dailybarsUpdateInterval

        self.t0_intra = []
        self.t0_daily = []
        self.updateCDI()

    def updateCDI(self):
        df = mds.read('CDI','1BDay',library=mds.assetVS)
        dt0 = dt.now().replace(hour=0,minute=0,second=0,microsecond=0)

        cdi0 = self.blp.getRefData(['BZDIOVRA Index'],['px_last']).values[0]/100

        cdi0=(1+cdi0)**(1/252)-1

        j = df.index.get_loc(dt0,method='ffill')

        if df.index[j]==dt0:
            cdi_tm1 = df.close[j-1]
        else:
            cdi_tm1 = df.close[j]

        df.loc[dt0]=cdi_tm1*(1+cdi0)

        mds.delete(df.md.name,df.md.freq,library=mds.onlineVS)
        mds.write(df,library=mds.onlineVS,check_metadata=False)




    def subscribeIntradaybars(self,onlineTable):
        # if isinstance(intradayQuery,(list,tuple)):
        #     self.intradayQueries=self.intradayQueries+intradayQuery
        # else:
        #     self.intradayQueries.append(intradayQuery)
        if self.onlineTable is None:
            self.onlineTable=onlineTable
        else:
            self.onlineTable = self.onlineTable.append(onlineTable)

        self.t0_intra+=[0]*onlineTable.shape[0]
        self.t0_daily+=[0]*onlineTable.shape[0]

    def startBLP(self):
        self.evenHandler = blpEventHandler1(self)
        self.blp=blp(eventHandler=self.evenHandler)


    def onReceive(self,addr,obj):
        if DEBUG:
            print('received: {}'.format(obj))

        if obj['order']=='subscribe':

            ids=self.blp.subscribe(obj['securities'],obj['fields'],obj['options'])
            if not addr in self.sublist:
                self.sublist[addr]=[]
            self.sublist[addr].append((ids,(obj['securities'],obj['fields'],obj['options'])) )

        elif obj['order']=='unsubscribe':
            self.blp.unsubscribe(obj['securities'],obj['fields'],obj['options'])


    def onEndConnection(self,addr,conn):
        if addr in self.sublist:
            for l in self.sublist[addr]:
                self.blp.unsubscribe(*l[1])

    def onListen(self):
        self.doBars()


    def startServeBars(self,interval=5):
        from threading import Thread
        # self.clientBars = Client(LocalCluster(1,1,False))
        self.loopBars = True

        def barsLoop(self):
            while self.loopBars:
                time.sleep(interval)
                self.doBars()
        self.barsThread = Thread(target=barsLoop,args=(self,))
        self.barsThread.start()

    def stopServeBars(self):
        self.loopBars = False


    def doBars(self): #for intraday bars
        from mDataStore.mongo import mDataFrame, metadataAsset
        from mDataStore import mongo

        if self.onlineTable is None:
            return

        t1=time.time()
        # print('doBars1')
        if hasattr(self,'t0_bars') and (t1-self.t0_bars<1):
            return

        self.t0_bars=t1
        dt_today = dt.today().replace(hour=0,minute=0,second=0,microsecond=0)
        dt_today_loc = pd.Timestamp(dt_today).tz_localize('America/Sao_Paulo')
        dt_max = dt.today().replace(year=dt_today.year+1,hour=0,minute=0,second=0,microsecond=0)
        if not 'lastBlpIndex' in self.onlineTable:
            self.onlineTable['lastBlpIndex']=dt_today_loc
        for i in range(self.onlineTable.shape[0]):
            a = Dict(self.onlineTable.iloc[i].to_dict())
            if (not isinstance(a.INTRA_SHORT_NAME,str)) or (not isinstance(a.freq,str)):
                continue

            nfreq, sfreq = mongo.splitFreq(a.freq) #assume freq is minutes

            if (t1-self.t0_intra[i]>a.updateInterval):
                # st1 = dt.now() - datetime.timedelta(seconds=a.updateInterval*5) #np.maximum(a.startDate,dt_today)
                # try:
                #     df_ = mds.read(a.security,a.freq,library=mds.mktBars,date_range=[st1,dt_max])
                #     df1 = self.blp.getIntradayHistoricData(a.security, nfreq, st1, dt_max, event=a.event,
                #                                            **a.kwargs)
                # except Exception as e: #first query of the day - get all times
                #     df1 = self.blp.getIntradayHistoricData(a.security, nfreq, dt_today, dt_max, event=a.event,
                #                                            **a.kwargs)
                # df1 = self.blp.getIntradayHistoricData(a.security, nfreq, dt_today, dt_max, event=a.event,**a.kwargs)

                self.t0_intra[i] = t1
                try:
                    md = mds.read_metadata(a.INTRA_SHORT_NAME,'1Minute',mds.assetTS2)#a.security.split(' ')[0]
                    md.freq=a.freq
                except:
                    md = metadataAsset(a.INTRA_SHORT_NAME, 'equity', freq=a.freq,feeder_id=a.FEEDER_ID)
                mds.blp=self.blp
                #dt_today
                df1 = self.blp.getIntradayHistoricDataBA(a.FEEDER_ID, nfreq, self.onlineTable.lastBlpIndex[i], dt_max,md, event=a.event,mds=mds)
                if df1.shape[0]==0:
                    continue

                self.onlineTable.lastBlpIndex.values[i]=df1.index[-1]
                                                       #                                            **a.kwargs)
                df1=df1.rename(columns={'numEvents':'trades'})
                if df1.index.tzinfo is None:
                    df1=df1.tz_localize('GMT')
                print('doBars2 - ' + a.FEEDER_ID)
                try:
                    mds.append(df1,library=mds.onlineTS,replaceIntersection=True,check_metadata=False)
                except Exception as e:
                    warn('Unable to append {}'.format(df1.md.name))
                    uu.printException(e)
                # if len(a.addrs) :
                #     self.putData({'messageType':'barsUpdate','data':a},a.addrs)


                if (t1-self.t0_daily[i]>a.dailyUpdateInterval) :
                    # for each series in intradayQueries, check if the daily series is in onlineVS up to yesterday
                    # If not, simply copy the series from assetVS to onlineVS. If it is not up-to-date, warn
                    #
                    self.t0_daily[i] = t1

                    dt_today1 = dt_today + datetime.timedelta(1)
                    dt0 = dt(1900, 1, 1)



                    if (df1.shape[0] ==0 )or df1.index[-1] < dt_today_loc:
                        warn('No prices for {}/{} today ({}) in bars - (intraday/onlineTS)'.format(a.INTRA_SHORT_NAME,nfreq,dt_today ))
                        continue


                    try:
                        dfd = mds.read(a.daily_shortname, '1BDay', library=mds.assetVS, date_range=[dt0, dt_today1])
                    except Exception as e:
                        print('Unable to read {}/{} from assetVS in bars - daily'.format(
                            a.security,nfreq ))
                        uu.printException(e)
                        continue
                    # df1 = df1.loc[df1.index<dt_today_loc]
                    c1=dfd.columns.intersection(df1.columns)
                    c2=dfd.columns.difference(df1.columns)
                    dfi1 = df1[c1].iloc[-1]
                    lastUpdate=dfi1.name
                    dfi1.name=dfi1.name.normalize().tz_localize(None)



                    for c in c2:
                        dfi1[c] = array(nan)

                    # if md.subtype == 'fut_rol':
                    if 'underlying' in dfd:
                        if not 'underlying' in df1:
                            warn('Ignoring {}/{} for Daily. Underlying not present in bloomberg results'.format(a.INTRA_SHORT_NAME,nfreq))
                            continue
                        dfi1['underlying'] = dfi1['underlying'].split(' ')[0]
                        if dfd.underlying[-1] != dfi1['underlying']:
                            continue

                        #check if it is the corerct future, if not continue

                    dfd_=pd.DataFrame(dfi1).T



                    for c in dfd_.columns:
                        # if dfd[c].dtype in [float32,float64,int32,int64]:
                        dfd_[c]=dfd_[c].astype(dfd[c].dtype)

                    if dfd.md.subtype == 'di_fut':
                        dfd_['yield_close']=dfd_['close']
                        dfd_['close']=NaN

                    df2 = pd.concat((dfd,dfd_))
                    df2.md=dfd.md
                    df2.md.lastUpdate=lastUpdate
                    # if (not 't0_daily' in a): #first uptade in the day
                    try:
                        mds.delete(df2.md.name,df2.md.freq,library=mds.onlineVS) #make sure not accumulating versions
                    except Exception as e:
                        pass
                    try:
                        mds.write(df2,library=mds.onlineVS,check_metadata=False,prune_previous_version=True)
                    except Exception as e:
                        print('Unable to read {}/{} from assetVS in bars - daily'.format(
                            a.security,nfreq ))
                        uu.printException(e)





class blpFeederClient(dataClient):

    def __init__(self,server_addr,maxHist=1000):
        super(blpFeederClient, self).__init__(server_addr)
        self.objs=[]
        self.maxHist=maxHist

    def onReceive(self, addr, obj):
        if DEBUG:
            print('received: {}'.format(obj))
        self.objs.append(obj)
        if len(self.objs)>self.maxHist:
            self.objs.pop(0)


    def subscribe(self,securities,fields,options=[]):
        obj=dict(order='subscribe',securities=securities,fields=fields,options=options)
        self.putData(obj)

    def unsubscribe(self,securities,fields,options=[]):
        obj=dict(order='unsubscribe',securities=securities,fields=fields,options=options)
        self.putData(obj)




class xlBlpFeederClient(blpFeederClient):
    def __init__(self, server_addr, sheets=[],maxHist=1000):
        super(xlBlpFeederClient,self).__init__(server_addr,maxHist)
        self.sheets=[]
        self.tickers = []
        self.fields = []
        self.columns = []
        self.ranges = []
        cluster = LocalCluster(1,1,False)
        self.client = Client(cluster)
        for sheet in sheets:
            self.addSheet(sheet)

    def addSheet(self,sheet,range_name='blp_rt_inp[#ALL]'):
        if isinstance(sheet,str):
            sheet=xw.sheets[sheet]

        df=sheet.range(range_name).options(pd.DataFrame, expand='table').value

        self.sheets.append(sheet)
        self.ranges.append(sheet.range(range_name))

        self.tickers.append( pd.Index(df['code']) )
        self.fields.append(pd.Index(df['field_']))
        self.columns.append( df.columns )

        def addsheet1(sheet_name,range_name):
            worker=get_worker()
            if not hasattr(worker,'sheets'):
                worker.sheets=[]
                worker.ranges=[]

            sheet = xw.sheets[sheet_name]
            worker.sheets.append(sheet)
            worker.ranges.append(sheet.range(range_name))

        self.client.submit(addsheet1,sheet.name,range_name)

        for i,v in enumerate(df['code']):
            self.subscribe([v],[df['field_'][i]],['interval=2'])
        # self.tickers.append( pd.Index([c.split('_')[0] for c in cods]) )
        # self.fields.append(pd.Index([c.split('_')[0] for c in cods]))


    def onReceive(self, addr, obj):
        super(xlBlpFeederClient, self).onReceive( addr, obj)
        dt_today = datetime.date.today()
        ticker,dti,obj=obj
        if not hasattr(self,'onReceive_t0'):
            self.onReceive_t0=time.time()

        self.ups={}
        for i,rng in enumerate(self.ranges):
            try:
                l = self.tickers[i].get_loc(ticker)
            except Exception as e:
                # print('unable to find {} in {}'.format(cod,sheet.name))
                continue

            obj1 = {k:v for k,v in obj.items() if k in self.columns[i]}

            for k,v in obj1.items():
                j = self.columns[i].get_loc(k)
                if isinstance(obj1[k],datetime.time):
                    v_xl = dt.combine(dt_today,obj1[k])
                else:
                    v_xl = obj1[k]
                self.ups[(i,l+1,j+1)]=v_xl
                # rng[l+1,j+1].value=v_xl
        t1=time.time()
        if t1-self.onReceive_t0>0.3:
            def update1(ups):
                worker = get_worker()
                for up, v in ups.items():
                    i, l1, j1 = up
                    worker.ranges[i][l1, j1].value = v

            if not hasattr(self,'f') or self.f.status=='finished':
                self.f=self.client.submit(update1,self.ups)



            self.onReceive_t0=t1

            # self.ups={}






