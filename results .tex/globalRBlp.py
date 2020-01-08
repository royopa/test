# import globalM
from mDataStore.bloomberg.remote import rBLP
# import time
# if globalM.useLocalDB:
# mds = mongoDS()
blp = rBLP()
#     pass
# else:
#     mds = mongoDS(replicaSet='r1',doAssetDF=False)
#
#     if globalM.doSetPrimary:
#         if mds.mongo.primary[0] != globalM.myMongoHost.split(':')[0]:
#             mds.setPrimary(globalM.myMongoHost)
#             time.sleep(10)
#     mds = mongoDS(replicaSet='r1',doAssetDF=True)
