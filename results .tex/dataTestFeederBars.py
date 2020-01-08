from mDataStore.dataFeeder import blpFeederServer
import socket
import time
import pandas as pd
import globalM
hostname = socket.gethostbyname(socket.gethostname())
# print('host: {}'.format(hostname))

onlineTable = pd.read_excel(globalM.dataRoot+'/metadata.xlsx','onlineBars')


server = blpFeederServer(hostname,8021)
# qry = [intradayQuery('BZ1','BZ1 index','1Minute',updateInterval=5),intradayQuery('FUT_USD_BRL','UC1 curncy','1Minute',updateInterval=15),intradayQuery('ES1','ES1 index','1Minute',updateInterval=15),
#        intradayQuery('DI1F21','ODF21 comdty','1Minute',updateInterval=15),intradayQuery('ITUB4','ITUB4 equity','1Minute',updateInterval=15)]


server.subscribeIntradaybars(onlineTable)
server.startServeBars()
# for i in range(100):
#     time.sleep(3)
#     server.doBars()

server.listen()