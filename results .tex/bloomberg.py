from py_init import *
from warnings import warn
from mUtil import Dict
from numpy import *
import pandas as pd
from datetime import datetime as dt
import numpy as np
from tqdm import tqdm
# from mDataStore.mongo import mongoDS

from mDataStore.util import LogController

import globalM
import collections
import logging

# tqdm=lambda x:x

try:
    import blpapi
    from blpapi.datatype import DataType
    BAR_DATA = blpapi.Name("barData")
    BAR_TICK_DATA = blpapi.Name("barTickData")
    OPEN = blpapi.Name("open")
    HIGH = blpapi.Name("high")
    LOW = blpapi.Name("low")
    CLOSE = blpapi.Name("close")
    VOLUME = blpapi.Name("volume")
    VALUE = blpapi.Name("value")
    NUM_EVENTS = blpapi.Name("numEvents")
    TIME = blpapi.Name("time")
    RESPONSE_ERROR = blpapi.Name("responseError")
    SESSION_TERMINATED = blpapi.Name("SessionTerminated")
    CATEGORY = blpapi.Name("category")
    MESSAGE = blpapi.Name("message")
    EXCEPTIONS = blpapi.Name("exceptions")
    FIELD_ID = blpapi.Name("fieldId")
    REASON = blpapi.Name("reason")
    DESCRIPTION = blpapi.Name("description")

except:
    warn('unable to import bloomberg')



def getValue(v):
    vv=v.getValue()
    if isinstance(vv,blpapi.element.Element):
        Ni = v.numValues()
        vv1=[]
        title=[]
        for ii in range(Ni):
            vv = v.getValue(ii)
            Nj = vv.numElements()
            vv1.append([])
            for jj in range(Nj):
                if ii == 0:
                    title.append(vv.getElement(jj).name().__str__())
                vv1[-1].append( vv.getElement(jj).getValue(0))

        vv1=[title]+vv1
        return vv1
    else:
        return vv



class blp(object):

    def __init__(self,options={'host': 'localhost', 'port': 8194},eventHandler = None):
        options = Dict(options)
        session_options = blpapi.SessionOptions()
        session_options.setServerHost(options.host)
        session_options.setServerPort(options.port)
        self.session = blpapi.Session(session_options)

        session_options_live = blpapi.SessionOptions()
        session_options_live.setServerHost(options.host)
        session_options_live.setServerPort(options.port)

        if eventHandler is None:
            self.eventHandler = blpEventHandler()
        else:
            self.eventHandler=eventHandler
        # Create a Session
        self.session_live = blpapi.Session(session_options_live, self.eventHandler.processEvent)

        # Start a Session
        if not self.session.start():
            raise(Exception("Failed to start session."))

        if not self.session.openService("//blp/refdata"):
            raise(Exception("Failed to open //blp/refdata"))

        self.refDataService = self.session.getService("//blp/refdata")

        ### LIVE
        if not self.session_live.start():
            raise(Exception("Failed to start live session."))

        if not self.session_live.openService("//blp/mktdata"):
            raise(Exception("Failed to open //blp/mktdata (live)"))

        self.mktDataService = self.session_live.getService("//blp/mktdata")


    def stop(self):
        if hasattr(self, 'session'):
            self.session.stop()
        if hasattr(self, 'session_live'):
            self.session_live.stop()

    def __del__(self):
        self.stop()

    def getRefData(self, securities0, fields, overrides=None, **kwargs):
        securities0=np.atleast_1d(securities0)
        securities=np.unique(securities0)
        # assert (np.unique(securities).size == securities.size)
        request = self.refDataService.createRequest("ReferenceDataRequest")
        for s in securities:
            request.getElement("securities").appendValue(s)
        for f in fields:
            request.getElement("fields").appendValue(f)

        if not overrides is None:
            overrides_ = request.getElement("overrides")

            for k in overrides:
                override1 = overrides_.appendElement()
                override1.setElement("fieldId", k)
                override1.setElement("value", overrides[k])

        cid=self.session.sendRequest(request)
        ReferenceDataResponse = blpapi.Name('ReferenceDataResponse')
        securityData = blpapi.Name('securityData')
        security = blpapi.Name('security')
        fieldData1 = blpapi.Name('fieldData')
        D = Dict()

        while True:
            # We provide timeout to give the chance for Ctrl+C handling:
            ev = self.session.nextEvent(500)


            for msg in ev:
                #print(msg)
                if cid in msg.correlationIds():
                    elto=msg.asElement()
                    #out.append(elto)
                    if elto.name()==ReferenceDataResponse:
                        secdata=elto.getElement(securityData)
                        for secdataI in secdata.values():
                            d=Dict()
                            secName=secdataI.getElementAsString(security)
                            fieldData = secdataI.getElement(fieldData1)
                            for v in fieldData.elements():
                                d[v.name().__str__()]=getValue(v) #v.getValue()

                            D[secName]=d

            if ev.eventType() == blpapi.Event.RESPONSE:
                # Response completly received, so we could exit
                break
        df =pd.DataFrame.from_dict(D,'index')
        return df

    def getHistoricData(self, securities0, fields, startDate,endDate, **kwargs):
        """
        Make historical data request to bloomberg blpapi engine.
        :param securities: List of securities that one wants to retrieve the historical data
        :param fields: List of fields required
        :param startDate: Starting date
        :param endDate: Ending date
        :param kwargs: Option arguments
        :return:
        """
        securities0 = np.atleast_1d(securities0)
        securities=np.unique(securities0)
        # assert(.size == securities.size)
        request = self.refDataService.createRequest("HistoricalDataRequest")

        for s in securities:
            request.getElement("securities").appendValue(s)

        for f in fields:
            request.getElement("fields").appendValue(f)
        #request.set("periodicityAdjustment", "ACTUAL")
        #request.set("periodicitySelection", "MONTHLY")
        if not startDate is None:
            request.set("startDate", "{:%Y%m%d}".format(startDate))

        if not endDate is None:
            request.set("endDate", "{:%Y%m%d}".format(endDate))

        for s in kwargs:
            request.set(s,kwargs[s])

        #print("Sending Request:", request)
        # Send the request
        cid = self.session.sendRequest(request)
        HistoricalDataResponse = blpapi.Name('HistoricalDataResponse')
        securityData = blpapi.Name('securityData')
        security = blpapi.Name('security')
        fieldData1 = blpapi.Name('fieldData')

        D = Dict()
        for s in securities:
            d = Dict()
            d['date'] = []
            for f in fields:
                d[f] = []
            D[s] = d

        while True:
            # We provide timeout to give the chance for Ctrl+C handling:
            ev = self.session.nextEvent(500)

            for msg in ev:
                if cid in msg.correlationIds():
                    elto = msg.asElement()
                    if elto.name() == HistoricalDataResponse:
                        secdata = elto.getElement(securityData)
                        secName = secdata.getElementAsString(security)
                        d = D[secName]
                        fieldData = secdata.getElement(fieldData1)

                        for v in fieldData.values():
                            flds=[]

                            for ve in v.elements():
                                d[ve.name().__str__()].append(ve.getValue())
                                flds.append(ve.name().__str__())
                                # if ve.datatype() in [DataType.DATE, DataType.DATETIME,DataType.TIME]: #datetime
                                #     d[ve.name().__str__()].append(ve.getValueAsDatetime())
                                # elif ve.datatype() in [DataType.FLOAT32,DataType.FLOAT64,DataType.DECIMAL]:
                                #     d[ve.name().__str__()].append(ve())
                                #
                                # else:
                                #     raise(Exception)

                            for f in fields:
                                if f not in flds:
                                    d[f].append(nan)


              #  print(msg)

            if ev.eventType() == blpapi.Event.RESPONSE:
                # Response completly received, so we could exit
                break

        # out=Dict()
        # for s in D:
        #     s1=s.replace(" ","_").replace("/","_")
        #     out[s1] = pd.DataFrame.from_dict(D[s])
        #     out[s1]=out[s1].set_index('date')
        out = []
        for s in D:
            df = pd.DataFrame.from_dict(D[s]).set_index('date')
            df.index = pd.DatetimeIndex(df.index)
            out.append(df)

        out1=dict(zip(securities,out))
        out=[out1[k] for k in securities0]

        return out

    def getIntradayHistoricDataBA(self, feeder_id, interval, startDate, endDate, md, event='TRADE', mds=None, **kwargs):

        if mds is None:
            from mDataStore.globalMongo import mds
        from mDataStore.mongo import mDataFrame

        df = mDataFrame(self.getIntradayHistoricData(feeder_id,interval , startDate, endDate,event='TRADE', **kwargs))
        df_bid = self.getIntradayHistoricData(feeder_id,interval , startDate, endDate,event='BID', **kwargs)
        df_ask = self.getIntradayHistoricData(feeder_id,interval , startDate, endDate,event='ASK', **kwargs)
        #desc1 = mds.blp.getRefData(feeder_id, desc)

        df.md=md

        df.rename(columns={'numEvents': 'trades'}, inplace=True)

        df.index=df.index.tz_localize('GMT')
        df_bid.index = df_bid.index.tz_localize('GMT')
        df_ask.index = df_ask.index.tz_localize('GMT')
        # overwrite=True

        if md.subtype in ['fut_nrol','fut_rol']:
            dts = mds.read(df.md.name.lower() + '_dates', library=mds.fundamentalVS)
            dts1=pd.Index(pd.to_datetime(dts.iloc[:,1]))
            dts1=dts1.tz_localize(df.index.tzinfo.zone)

            I = dts1.get_indexer(df.index,method='bfill')
            underlying=dts.iloc[I,0]
            df['underlying']=underlying.values

        df['bid'] =nan
        J = df_bid.index.get_indexer(df.index)
        df.loc[J>=0,'bid']=df_bid.close.iloc[J[J>=0]].values

        df['ask'] =nan
        J = df_ask.index.get_indexer(df.index)
        df.loc[J>=0,'ask']=df_ask.close.iloc[J[J>=0]].values

        # df['vwap'] =
        df=df.rename(columns={'trades':'gmt_off'})

        df['vwap']= df['value']/df['volume']

        del df['value']
        return df

    def getIntradayHistoricData(self, security, interval, startDate, endDate, event='TRADE', **kwargs):
        """
        Make request for intraday historical data (bar) to blpapi engine.
        :param security: Target security
        :param interval: Intraday interval (minutes/hours)
        :param startDate: Starting date
        :param endDate: Ending date
        :param event: Blpapi event.
        :param kwargs: Option arguments.
        :return:
        """
        if isinstance(security,list) or isinstance(security,ndarray):
            ret = [self.getIntradayHistoricData(s,interval,startDate,endDate,event='TRADE',**kwargs) for s in security]
            return ret

        request = self.refDataService.createRequest("IntradayBarRequest")
        request.set("security",security)
        request.set("interval", interval)
        request.set("eventType", event)

        # for f in fields:
        #     request.getElement("fields").appendValue(f)
        #request.set("periodicityAdjustment", "ACTUAL")
        #request.set("periodicitySelection", "MONTHLY")

        if not startDate is None:
            request.set("startDateTime", startDate )#"{:%Y%m%d}".format(startDate)
        if not endDate is None:
            request.set("endDateTime", endDate ) #"{:%Y%m%d}".format(endDate)

        for s in kwargs:
            request.set(s, kwargs[s])

        #print("Sending Request:", request)
        # Send the request
        # cid=self.session.sendRequest(request)
        # securityData=blpapi.Name('securityData')
        # security=blpapi.Name('security')
        # fieldData1=blpapi.Name('fieldData')
        self.session.sendRequest(request)
        fields=['time', 'open', 'high', 'low', 'close', 'numEvents', 'volume', 'value']
        d = Dict()
        for f in fields:
            d[f] = []

        eventLoop(self.session, d)

        df=pd.DataFrame.from_dict(d).set_index('time')
        df.index=pd.DatetimeIndex(df.index)
        df.index.tz_localize('GMT')

        return df

    def subscribe(self, securities, fields, options=[]):
        try:
            subscriptions = blpapi.SubscriptionList()

            service = "//blp/mktdata"
            id = []
            for t in securities:
                topic = service
                if not t.startswith("/"):
                    topic += "/"
                topic += t
                id.append(blpapi.CorrelationId(t)) #blpapi.CorrelationId(t)
                subscriptions.add(topic, fields, options, id[-1])

            print("Subscribing...")
            self.session_live.subscribe(subscriptions)
        except Exception as ex:
            print("Subscription Failed")
            uu.printException(ex)
            return None
        return id

    def unsubscribe(self,securities,fields,options=[]):
        subscriptions = blpapi.SubscriptionList()
        try:
            service = "//blp/mktdata"
            id=[]
            for t in securities:
                topic = service
                if not t.startswith("/"):
                    topic += "/"
                topic += t
                id.append(blpapi.CorrelationId(t)) #blpapi.CorrelationId(t)
                subscriptions.add(topic, fields, options,
                                  id[-1])
            print("UnSubscribing...")
            self.session_live.unsubscribe(subscriptions)
        except Exception as e:
            print("Error Unsubscribing")
            uu.printException(e)


    # def unsubscribe(self, securities, fields, options=[]):
    #     pass



###### LIVE #################

class blpEventHandler(object):
    def __init__(self,maxHist=1000):
        self.data={}
        self.time={}
        self.maxHist=maxHist

    def getTimeStamp(self):
        return time.strftime("%Y/%m/%d %X")

    def processSubscriptionStatus(self, event):
        timeStamp = self.getTimeStamp()
        print("Processing SUBSCRIPTION_STATUS")
        for msg in event:
            topic = msg.correlationIds()[0].value()
            print("%s: %s - %s" % (timeStamp, topic, msg.messageType()))

            if msg.hasElement(REASON):
                # This can occur on SubscriptionFailure.
                reason = msg.getElement(REASON)
                # print("        %s: %s" % (
                #     reason.getElement(CATEGORY).getValueAsString(),
                #     reason.getElement(DESCRIPTION).getValueAsString()))

            if msg.hasElement(EXCEPTIONS):
                # This can occur on SubscriptionStarted if at least
                # one field is good while the rest are bad.
                exceptions = msg.getElement(EXCEPTIONS)
                for exInfo in list(exceptions.values()):
                    fieldId = exInfo.getElement(FIELD_ID)
                    reason = exInfo.getElement(REASON)
                    print("        %s: %s" % (
                        fieldId.getValueAsString(),
                        reason.getElement(CATEGORY).getValueAsString()))

    def processSubscriptionDataEvent(self, event):
        timeStamp = self.getTimeStamp()
        # print()
        # print("Processing SUBSCRIPTION_DATA")
        dti=dt.now()
        for msg in event:
            topic = msg.correlationIds()[0].value()
            print("%s: %s - %s" % (timeStamp, topic, msg.messageType()))
            print("MESSAGE: %s", msg)
            if not topic in self.data:
                self.data[topic] = {}
            if not dti in self.data[topic]:
                self.data[topic][dti]={}
            if len(self.data[topic][dti])>self.maxHist:
                self.data[topic].popitem(last=False)

            for field in msg.asElement().elements():
                if field.numValues() < 1:
                    # print("        %s is NULL" % field.name())
                    continue

                # Assume all values are scalar.
                # print("        %s = %s" % (field.name(),
                #                            field.getValueAsString()))

                # test - This field does not return any value, but still passes through early condition.
                if field.name() == "PROXY_TIME_OF_LAST_UPDATE_RT":
                    continue

                try:
                    v = field.getValue()
                    if isinstance(v, blpapi.name.Name):
                        vv = v.__str__()
                    else:
                        vv = v
                except Exception as e:
                    print("Error on extracting field: " + field.name().__str__())
                    uu.printException(e)
                    vv = None
                self.data[topic][dti][field.name().__str__()] = vv  #.__str__()

            self.onBlpReceive(self.data[topic][dti], topic, dti)


    def onBlpReceive(self,obj,topic,dti):
        pass

    def processMiscEvents(self, event):
        timeStamp = self.getTimeStamp()
        # for msg in event:
        #     print("%s: %s" % (timeStamp, msg.messageType()))

    def processEvent(self, event, session):
        try:
            if event.eventType() == blpapi.Event.SUBSCRIPTION_DATA:
                return self.processSubscriptionDataEvent(event)
            elif event.eventType() == blpapi.Event.SUBSCRIPTION_STATUS:
                return self.processSubscriptionStatus(event)
            else:
                return self.processMiscEvents(event)
        except blpapi.Exception as e:
            print("Library Exception !!! %s" % e.description())
        return False






######## INTRADAY ###########

def processMessage(msg,d):
    data = msg.getElement(BAR_DATA).getElement(BAR_TICK_DATA)
    #print("Datetime\t\tOpen\t\tHigh\t\tLow\t\tClose\t\tNumEvents\tVolume")

    for bar in list(data.values()):
        d['time'].append(bar.getElementAsDatetime(TIME))
        d['open'].append(bar.getElementAsFloat(OPEN))
        d['high'].append(bar.getElementAsFloat(HIGH))
        d['low'].append(bar.getElementAsFloat(LOW))
        d['close'].append( bar.getElementAsFloat(CLOSE))
        d['numEvents'].append( bar.getElementAsInteger(NUM_EVENTS))
        d['volume'].append( bar.getElementAsInteger(VOLUME))
        d['value'].append(bar.getElementAsFloat(VALUE))

        # print("%s\t\t%.3f\t\t%.3f\t\t%.3f\t\t%.3f\t\t%d\t\t%d" % \
        #     (time.strftime("%m/%d/%y %H:%M"), open, high, low, close,
        #      numEvents, volume))

def processResponseEvent(event,d):
    for msg in event:
        # print(msg)
        if msg.hasElement(RESPONSE_ERROR):
            printErrorInfo("REQUEST FAILED: ", msg.getElement(RESPONSE_ERROR))
            continue
        processMessage(msg,d)

def printErrorInfo(leadingStr, errorInfo):
    print("%s%s (%s)" % (leadingStr, errorInfo.getElementAsString(CATEGORY),
                         errorInfo.getElementAsString(MESSAGE)))

def eventLoop(session,d):
    done = False
    while not done:
        # nextEvent() method below is called with a timeout to let
        # the program catch Ctrl-C between arrivals of new events
        event = session.nextEvent(500)
        if event.eventType() == blpapi.Event.PARTIAL_RESPONSE:
  #          print("Processing Partial Response")
            processResponseEvent(event,d)
        elif event.eventType() == blpapi.Event.RESPONSE:
   #         print("Processing Response")
            processResponseEvent(event,d)
            done = True
        else:
            for msg in event:
                if event.eventType() == blpapi.Event.SESSION_STATUS:
                    if msg.messageType() == SESSION_TERMINATED:
                        done = True

#########################################################



def printFields():

    for a in dir(DataType):
        if not a.startswith('__'):
            print('{} - {}'.format(a, getattr(DataType, a)))


def teste():
    blp1 = blp()
    # df1 = blp1.getRefData(['BZ1 index'], ['FUT_CHAIN_LAST_TRADE_DATES'], {"INCLUDE_EXPIRED_CONTRACTS": "Y"})

    a = 1 #BPPPCPNZ Index

    # hist = blp1.getHistoricData(['BPPPCPNZ Index', 'BPPPCPCH Index', 'BPPPCPAU Index', 'BPPPCPEU Index',\
    #                             'BPPPCPGB Index', 'BPPPCPCA Index', 'BPPPCPNO Index', 'BPPPCPJP Index',\
    #                             'BPPPCPSE Index '], ['PX_LAST'], dt(2000, 10, 15), dt(2018, 10, 15))

    hist = blp1.getHistoricData(['NZD Curncy'],['PX_OPEN', 'PX_HIGH', 'PX_LOW', 'PX_LAST', 'PX_VOLUME', 'EQY_WEIGHTED_AVG_PX'],
                                dt(2000, 10, 15), dt(2018, 10, 15))

    hist = blp1.getHistoricData(['NZD Curncy'], [], dt(2000, 10, 15), dt(2018, 10, 15))

    hist = blp1.getHistoricData(['BZ1 Index', 'UC1 Curncy', 'ODF21 Comdty','BNTNB 6 08/15/50 Corp'],
                                ['PX_LAST', 'OPEN', 'LOW', 'HIGH', 'VOLUME'], dt(2017, 10, 15), dt(2018, 10, 15))
    # hist1 = blp1.getHistoricData(['BZ1 Index'],
    #                             ['PX_LAST', 'OPEN', 'LOW', 'HIGH', 'VOLUME'], dt(1980, 10, 15), dt(2018, 10, 15))
    data1 = blp1.getRefData(['EC537521@ANDE Corp', 'EK026741@ANDE Corp'], ['PX_DIRTY_BID', 'YLD_YTM_BID'],
                            {'SETTLE_DT': '20150505'})
    data2 = blp1.getRefData(['EC537521@ANDE Corp', 'EK026741@ANDE Corp'], ['PX_DIRTY_BID', 'YLD_YTM_BID'],
                            {'SETTLE_DT': '20181022'})

    # this is the way
    data3 = blp1.getRefData(['EC537521@ANDE Corp'], ['PX_DIRTY_BID', 'YLD_YTM_BID', 'DUR_ADJ_BID'],
                            {'SETTLE_DT':'20150505', 'PX_BID': 3359.00})

    out = blp1.getHistoricData(['BZPIIPCM Index'], ['ECO_RELEASE_DT'], dt(2017, 10, 15), dt(2018, 10, 15))

    out = blp1.getRefData(['BZIPTLYO Index'], ['ECO_FUTURE_RELEASE_DATE_LIST'],
                          {'START_DT': '20150505', 'END_DT': '20190501'})

    print(hist.BZ1_Index)
    print(hist.UC1_Curncy)


if __name__ == '__main__':

    teste()
    globalM.loadBLP = True

    # bloombergUpdateRoutine()
    blp1 = blp()
    # blp1.startLiveFeed(['BZ1 Index'],['LAST_PRICE'])
    blp1.subscribe(['IBM US Equity'], ['LAST_PRICE'])

    #IBM US Equity
    try:
        # Wait for enter key to exit application
        print("Press ENTER to quit")
        input()
    finally:
        # Stop the session
        blp1.session_live.stop()

    a = 1
    # blp1.startLiveFeed(['BZ1 Index','UC1 Curncy'],['BID','ASK','LAST_TRADE'])

    # bloombergInitialRoutine()
