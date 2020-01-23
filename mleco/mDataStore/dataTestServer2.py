from mDataStore.dataFeeder.dataComm import dataServer

dsv = dataServer('127.0.0.1',8083)
dsv.listen()

