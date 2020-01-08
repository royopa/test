from arctic.exceptions import NoDataFoundException

from mDataStore.globalMongo import mds
from py_init import *


if __name__ == '__main__':

    print('Report: {:%d-%m-%Y}'.format(dt.now()))

    # diario
    al = ['BZ1', 'UC1', 'DI1F22', 'DI1F23', 'DI1F25', 'IMAB', 'IBOV',
          'PRE_1A', 'PRE_2A', 'ES1', 'TY1']
    freq = ['1BDay']
    library = ['assetVS']

    # get current date (d0)
    dt0 = dt.now().replace(hour=0, minute=0, second=0, microsecond=0)

    # get the workday before (d-1)
    dtm1 = pd.to_datetime(uu.workday(dt0, -1)[0])

    # set date interval
    expDT = [dtm1, dt0]

    print('ativo \t\t\t\tdata \t\tdata_exp \tstatus')
    print('------------------------------------------------------')

    for a in al:
        for f in freq:
            for i, l in enumerate(library):
                expDT_ = expDT[i]
                try:
                    dff = mds.read(a, freq=f, library=l)
                    print('{:_<18} \t{:%d-%m-%Y} \t{:%d-%m-%Y} \t{}'.format(a, dff.index[-1], expDT_,
                          'ok' if dff.index[-1] >= expDT_ else 'ERROR'))
                except NoDataFoundException:
                    print('{:_<20} \t{:%d-%m-%Y} \t{:%d-%m-%Y} \t{}'.format(a, dff.index[-1], expDT_,
                          'ERROR! Serie not found.'))
    print('------------------------------------------------------')
