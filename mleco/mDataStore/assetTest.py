from py_init import *
#TODO fazer calculadoras para cada subtype, refazer construtor do asset/strategy  e finalmente fazer o bt do pre

#mds.setPrimary('euler.sytes.net')

lst = mds.assetVS.list_symbols(name={'$regex':'DI1.*'})
code = np.char.replace(np.unique(lst),'_1BDay','').tolist()
with uu.Timer():
    dfs=mds.read(code)
#uu.networkdays(dfs[0].index,dfs[0].md.maturity)
a=1

def selChangeMetadata():
    df1 = uu.getXLselection()
    #df1=xw.books.active.app.selection.options(pd.DataFrame, expand='table').value

    for i in range(df1.shape[0]):
        md = mds.read_metadata(df1.name[i],df1.freq[i])
        md.type=df1.type[i]
        md.subtype = df1.subtype[i]
        mds.write_metadata(md)


