import globalM
from dask.distributed import Client
import mUtil as uu
from datetime import datetime as dt

from mUtil import getBLPIP


class rBLP():

    def __init__(self, addr=None):
        if addr is None:
            addr = getBLPIP()+':8786'
        self.addr = addr
        self.c = Client(getBLPIP()+':8786')


    def getHistoricData(self, securities, fields, startDate, endDate, **kwargs):
        def fcn(securities, fields, startDate, endDate,kwargs):
            global blp1
            from mDataStore.bloomberg import blp
            # if blp1 is None:
            blp1 = blp()

            dfs = blp1.getHistoricData(securities, fields, startDate, endDate, **kwargs)

            return dfs
        f = self.c.submit(fcn,securities, fields, startDate, endDate,kwargs)

        return f.result()


    def getRefData(self,securities,fields,overrides=None,**kwargs):
        def fcn(securities,fields,overrides,kwargs):
            from mDataStore.bloomberg import blp
            blp1 = blp()
            res = blp1.getRefData(securities,fields,overrides,**kwargs)

            return res

        f = self.c.submit(fcn, securities,fields,overrides,kwargs)

        return f.result()

    def getIntradayHistoricData(self,security,interval,startDate,endDate,event='TRADE',**kwargs):
        def fcn(security,interval,startDate,endDate,event,kwargs):
            from mDataStore.bloomberg import blp
            blp1 = blp()
            df = blp1.getIntradayHistoricData(security,interval,startDate,endDate,event,**kwargs)

            return df

        f = self.c.submit(fcn, security, interval, startDate, endDate, event, kwargs)

        return f.result()

    def getIntradayHistoricDataBA(self, feeder_id, interval, startDate, endDate, md, event='TRADE', mds=None, **kwargs):
        def fcn(feeder_id, interval, startDate, endDate, md, event='TRADE', mds=None, **kwargs):
            from mDataStore.bloomberg import blp
            blp1 = blp()
            df = blp1.getIntradayHistoricDataBA(feeder_id, interval, startDate, endDate, md, event='TRADE', mds=None, **kwargs)
            return df

        f = self.c.submit(fcn, feeder_id, interval, startDate, endDate, md, event='TRADE', mds=None, **kwargs)

        return f.result()






if __name__ =='__main__':

    blp1 = rBLP()

    # hist = blp1.getHistoricData(['BZ1 Index', 'UC1 Curncy', 'ODF21 Comdty', 'BNTNB 6 08/15/50 Corp'],
    #                             ['PX_LAST', 'OPEN', 'LOW', 'HIGH', 'VOLUME'], dt(2017, 10, 15), dt(2018, 10, 15))

    data1 = blp1.getRefData(['ES1 Index', 'TY1 comdty'], ['LAST_TRADE', 'TIME'])
    data1 = blp1.getRefData(['EUR Curncy', 'JPY Curncy'], ['LAST_PRICE', 'TIME'])

    data1 = blp1.getRefData(['ES1 Index', 'TY1 comdty'], ['TIME'])

    a = 1
