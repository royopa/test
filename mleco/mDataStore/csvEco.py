from py_init import *
from mDataStore.mongo import metadataFundamental
path1=globalM.dataRoot+'/eco_csv'

for f in os.listdir(path1):
    df = pd.read_csv(path1+'/'+f)
    df.columns=['dt']+df.columns[1:].tolist()
    df.set_index('dt',inplace=True)
    try:
        df.index = pd.to_datetime(df.index,format='%m/%d/%Y')
    except:
        df.index = pd.to_datetime(df.index, format='%YM%m')
    for c in df.columns:
        df1=pd.DataFrame(df[c].dropna())

        df1.md = metadataFundamental(c, 'eco_data', stDT=df.index[0])
        df1.md.subtype=f.split('.')[0]
        #df.md = metadataFundamental(f.split('.')[0],'eco_data',stDT=df.index[0])
        mds.write(df1,mds.fundamentalVS,check_metadata=False,prune_previous_version=True)




