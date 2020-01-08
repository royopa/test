from mDataStore.dataFeeder.dataComm import dataClient

dsv = dataClient(server_addr=[('10.96.82.93',8082)]) #,('127.0.0.1',8083)]
dsv.listen()

