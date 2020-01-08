from py_init import *
import mDataStore as ds
mds = ds.mongo.mongoDS()

def updateB3():
    ds.b3.importBMFAll()

def updateBLP():
    pass


def updateReuters():
    mds.reutersUpdateRoutine()


def updateECONOMATICA():
    ds.economatica.updateAll()



def updateAll():

    updateBLP()
    updateB3()
    updateReuters()
    updateECONOMATICA()




def insertBLP():
    mds.bloombergInsertNew(dt(1900,1,1))


if __name__ == '__main__':
    insertBLP()
    #updateB3()
    #updateAll()
