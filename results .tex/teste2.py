import mDataStore as ds
from py_init import *
#mds = ds.mongo.mongoDS('remote')
mds = ds.mongo.mongoDS()

mds.assetVS.list_symbols(True,endDT={'$gt':dt(2014,1,1,0,0,0,0)})

tst1=mds.read('teste1')
tst1.md.name='teste2'
mds.write(tst1)

mds.assetVS._prune_previous_versions('teste1_1BDay',keep_mins=0)
mds.assetVS.list_versions('teste1_1BDay')
mds.assetVS._delete_version('teste1_1BDay',5)