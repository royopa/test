import xlwings as xw
import pandas as pd
from mDataStore.globalMongo import mds
from mDataStore.bloomberg.remote import rBLP

blp1 = rBLP()
def updateDB():
    input = xw.Book.caller().sheets['db_input']
    out = xw.Book.caller().sheets['db']
    
    tb_blp = input.range('blp_hist_inp[#ALL]').options(pd.DataFrame, expand='table').value
    tb_db = input.range('db_inp[#ALL]').options(pd.DataFrame, expand='table').value

    out.clear_contents()

    k=1
    for i in range(tb_db.shape[0]):
        at=tb_db.index[i]
        freq=tb_db.freq[i]
        library=tb_db.library[i]
        dti = tb_db.dt_start[i]
        dtf = tb_db.dt_end[i]
        dfO = mds.read(at,freq,library=library,date_range=[dti,dtf])

        out.cells(1,k).value = pd.DataFrame(dfO)
        out.cells(1, k).value = at+'_'+freq
        k+=dfO.shape[1]+2

    for i in range(tb_blp.shape[0]):
        at=tb_blp.index[i]
        dti = tb_blp.dt_start[i]
        dtf = tb_blp.dt_end[i]
        fields = tb_blp.iloc[i,2:]
        fields = fields[~fields.isna()].values.tolist()

        dfs=blp1.getHistoricData([at],fields,dti,dtf)
        dfs=dfs[0]
        out.cells(1, k).value = pd.DataFrame(dfs)
        out.cells(1, k).value = at

        k+=dfs.shape[1]+2






    # out.range('A1').value = pd.DataFrame(tb_blp)
    # out.range('J1').value = pd.DataFrame(tb_db)
