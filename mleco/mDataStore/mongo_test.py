import mDataStore as ds
from py_init import *
from mUtil import Dict
#mds = ds.mongo.mongoDS('remote')
#mds=ds.mongo.mongoDS('remote','192.168.0.100')
mds=ds.mongo.mongoDS('remote','mongodb://bmorier:Ghc955maxmax!@knuth.sytes.net')
mds=ds.mongo.mongoDS('remote','mongodb://18.219.2.106',replicaSet='r1',readPreference='nearest')

mds=ds.mongo.mongoDS('remote','mongodb://18.219.2.106,knuth.sytes.net,34.227.50.120',replicaSet='r1',readPreference='nearest')
mds=ds.mongo.mongoDS('remote','mongodb://34.227.50.120',replicaSet='r1',readPreference='nearest')

#mds = ds.mongo.mongoDS()


#mds.assetTS._metadata.find_one({'md.name':'TYc1'})
mds.assetVS.list_symbols(endDT={'$gt':dt(3000,1,1)})
lst=mds.find()
#lo=np.array(lst,dtype=object)
#print(lst[0][2])

#print(mds.find())

df = pd.DataFrame({'bid': [1.0, 2.0, 3.0],'ask': [2.0, 3.0, 4.0]},
                  [dt(2014, 1, 4), dt(2014, 1, 5), dt(2014, 1, 6)])
df=ds.mongo.mDataFrame(df)
df.md=ds.metadataAsset('teste1','equity')
lst1=mds.findAsset(date_range=[dt(2000,1,1),dt(2002,1,1)])

mds.xlMetaTable()
mds.xlMetaTable()
mds.xlSeries('INDc1',ds.f.second,[dt(2004,1,1),dt(2004,2,1)])


mds.write(df,check_metadata=False)

# df1=pd.SparseDataFrame(df)
# df1.bid[2]=NaN
# df1.bid[1]=NaN
#
# df1.md=ds.metadataAsset('teste5','equity')
# mds.write(df1,check_metadata=False)




print(mds.read('teste1'))
df.md.freq=ds.f.second10
#mds.delete('teste1',ds.f.second10)
mds.write(df,check_metadata=False)

print(mds.read('teste1',ds.f.second10))

mds.reutersUpdateRoutine()


df1=mds.read('ESc1',ds.f.second5,date_range=ds.DateRange(dt(2018,1,1),dt(2018,5,1)))

print(df1)

df1.md.currency= 'USD'
mds.write_metadata(df1.md)


df1=mds.read('DOLc1',ds.f.second,date_range=ds.DateRange(dt(2018,1,1),dt(2018,5,1)))


def basicMeta():
    lst1 = mds.findAsset()

    for l in lst1.index:

        md1=mds.read_metadata(lst1.name[l],lst1.freq[l])
        md1.getDates()
        md1.stDT = md1.firstDT
        md1.endDT = None #md1.lastDT
        md1.maturity=None
        if md1.name[:3] in ['ESc','TYc']:
            md1.currency='USD'
            md1.type = 'fut_cat'
            md1.fut_like=True
        elif md1.name[:4] in ['DIJc','DOLc','INDc']:
            md1.type = 'fut_cat'
            md1.fut_like=True

        mds.write_metadata(md1)







#basicMeta()


