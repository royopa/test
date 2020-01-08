from py_init import *
from mDataStore.globalMongo import mds

df1 = pd.DataFrame(np.random.normal(300),index=pd.date_range(dt(2010,1,1),dt(2012,1,1),periods=300),columns=['close'] )

md1=ds.metadataAsset(name='teste',type='index',subtype='index')

df1.md=md1

mds.write(df1,library='testVS')
dff=mds.read('teste',library='testVS')
