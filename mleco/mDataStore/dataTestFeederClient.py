import mDataStore.dataFeeder as dataFeeder
import mDataStore.dataFeeder.dataComm as dataComm


dataComm.DEBUG = True
dataFeeder.DEBUG=True

from mDataStore.dataFeeder import blpFeederClient
import mUtil as uu
ipBlp=uu.getBLPIP()
client = blpFeederClient( server_addr=[(ipBlp,8021)] )

# client.subscribe(['ES1 Index'], ['LAST_PRICE'])
client.subscribe(['BZ1 Index'], ['LAST_PRICE'])

client.listen()


