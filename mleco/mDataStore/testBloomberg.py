
from py_init import *
import mDataStore as ds
from mUtil import Dict
#import globalM
#mds = ds.mongo.mongoDS('remote')
#mds = globalM.mds#ds.mongo.mongoDS()

df1 = mds.read('DI1F21')
uu.ismember(df1.index,df1.index)
mds.bloombergInsertNew(dt(1900,8,10),False)

a=1

