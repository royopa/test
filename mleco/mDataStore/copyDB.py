import arctic
# arctic.Arctic.DB_PREFIX = 'db_dws'
from mDataStore import mongo
from arctic.store.version_store import VersionStore
import pandas as pd
import re

mds0Str='localhost:27018'
mds1Str ='mongodb://assetDB:h8wG765g@mongo15-hml.safra.com.br:32611'
#erase

onlyArctic=True
if not onlyArctic:

    nmDB = ['db_dws','arctic','meta_db']

    # m0 = mongo.connect(mds0Str)
    m1 = mongo.connect(mds1Str)

    for nmDB1 in nmDB:
        nm=m1[nmDB1].list_collection_names()

        for n in nm:
            m1[nmDB1].drop_collection(n)


    mds0=mongo.mongoDS(mds0Str)
    mds1=mongo.mongoDS(mds1Str)

    print('IMPONRTING db_dws')

    db0 = mds0.mongoCli['db_dws']
    db1 = mds1.mongoCli['db_dws']


    for c in db0.list_collection_names():
        c0 = db0[c]
        cursor = c0.find({})

        for document in cursor:
            db1[c].insert(document)
else:
    mds0=mongo.mongoDS(mds0Str)
    mds1=mongo.mongoDS(mds1Str)

print('IMPORTING ARCTIC')

for l in  ['b3VS', 'b3VS_XML']:#mds0.arctic.list_libraries():
    l1 = getattr(mds0, l)
    print('Starting {}'.format(l))
    if isinstance(l1,VersionStore):
        lst = mds0.find(library=l,metadata=False)
        lst1 = mds1.find( library=l, metadata=False)
        for ls in lst:

            nms = ls[1].split('_')
            name='_'.join(nms[:-1])
            freq = nms[-1]
            if ls[1] in [l[1] for l in lst1]:
                print('skipping {} - {}'.format(name,freq))
                continue

            # lst1 = mds1.find(name,freq,library=l, metadata=False)

            # if len(lst1)==0:
            print('inserting {} - {}'.format(name,freq))

            df=mds0.read(name,freq,l)
            mds1.write(df,library=l)
            # else:
            #     print('skipping {} - {}'.format(name,freq))

    else:
        lst = mds0.find(library=l,metadata=False)
        for ls in lst:

            print('inserting {} - {}'.format(name,freq))

            dti = l1.min_date(name+'_'+freq)
            dtf = l1.max_date(name+'_'+freq)

            dts = pd.date_range(dti,dtf, freq='1Y').to_pydatetime().tolist()
            dts = [dti,]+dts+[dtf,]

            for i,dt1 in enumerate(dts[1:]):
                if dts[-1] != dt1:
                    try:
                        df=mds0.read(name,freq,l,date_range=[dts[i],dt1])
                        mds1.append(df,library=l)
                    except Exception as e:
                        import traceback
                        print('Exception on dates: {} - {}'.format(dts[i-1],dt1))
                        traceback.print_exception(type(e),e,e.__traceback__)



"""

db.adminCommand('listDatabases')

use db_dws
db.dropDatabase();

db.copyDatabase("objDB","db_dws","localhost")
use objDB
db.dropDatabase();


"""

#
# def rename_db():
#     from mDataStore.globalMongo import mds
#     nms=mds.mongoCli.list_database_names()
#
#     if 'objDB' in nms:
#         if 'db_dws' in nms:
#             mds.mongoCli.drop_database('db_dws')

