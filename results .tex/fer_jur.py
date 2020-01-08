from py_init import *
from mDataStore.globalMongo import mds

fer_jur=uu.getXLselection()
fer_jur1=pd.DatetimeIndex(fer_jur.index[:-1]).values

mds.obj.save('fer_jur',fer_jur1,'holidays')