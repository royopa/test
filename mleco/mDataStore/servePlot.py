from py_init import *
from mDataStore.globalMongo import mds
from bokeh.plotting import curdoc, figure
from bokeh.layouts import row, column, gridplot
from bokeh.driving import count
from mDataStore.mongo import convertFreq
TEST=False

mds.obj.save('plot_cfg0',{'TK':['BZ1 index','UC1 curncy','ES1 index'],
    'freq':[ds.freqHelper.minute15,ds.freqHelper.minute15,ds.freqHelper.minute15],'library':[mds.mktBars,mds.mktBars,mds.mktBars]},
             path='plot_data',saveStrategyAsAsset=False )
# TK='ES1 index'
N=0
obj1,dobj=mds.obj.load('plot_cfg{}'.format(N),'plot_data')

TK = obj1['TK']
freq=obj1['freq']
library=obj1['library']

df = [mds.read(TK1,freq[i],date_range=[dt(2010,1,1),dt(2020,1,1)],
            library=library[i]).tz_convert('America/Sao_Paulo') for i,TK1 in enumerate(TK)]

# for i,freq1 in enumerate(freq):
#     if freq1 != ds.freqHelper.minute:
#         df[i]=convertFreq(df[i],freq1)


# df2 = mds.read('BZ1 index',ds.freqHelper.minute,date_range=[dt(2010,1,1),dt(2020,1,1)],library=mds.mktBars).tz_convert('America/Sao_Paulo')
if TEST:
    T=1000
    for i in range(len(df)):
        df[i]=df[i].iloc[:-T]

fig=[]
inc_source=[]
for i,df1 in enumerate(df):
    fig_,inc_source_=uu.candlestick_plot(df1,df1.md.name)

    df1['Date'] = df1.index
    df1['idx'] = np.arange(df1.shape[0])
    df1 = df1.set_index('idx')
    fig.append(fig_)
    inc_source.append(inc_source_)

INCREASING_COLOR = '#17BECF'
DECREASING_COLOR = '#7F7F7F'


@count()
def update(tt):
    global df
    for i,TK1 in enumerate(TK):
        df1=df[i]
        inc_source1=inc_source[i]
        fig1=fig[i]
        freq1 = freq[i]


        dt0=df1.index[-1]
        xaxis_dt_format = '%d %b %Y, %H:%M:%S'
        print(' ### READ ####')
        df1_ = mds.read(TK1, freq1, date_range=[dt(2010,1,1), dt(2035, 1, 1)],
                       library=library[i]).tz_convert('America/Sao_Paulo')

        # if freq1 != ds.freqHelper.minute:
        #     df1_ = convertFreq(df1_, freq1)

        if TEST:
            df1_ = df1_.iloc[:-T + tt]
            if tt%2==0:
                df1_.high=df1_.high*1.0001
            else:
                df1_.high=df1_.high/1.0001

        df1_['Date']=df1_.index
        df1_['idx'] = np.arange(df1_.shape[0])
        df1_=df1_.set_index('idx')

        # t=df1_.index.get_loc(dt0,'nearest')
        t=len(inc_source1.data['high1'])
        inc_source1.data['high1']=df1_.high.iloc[:t].values.tolist()
        inc_source1.data['low1'] = df1_.low.iloc[:t].values.tolist()
        inc_source1.data['close1'] = df1_.close.iloc[:t].values.tolist()
        inc_source1.data['open1'] = df1_.open.iloc[:t].values.tolist()
        inc_source1.data['high1'] = df1_.high.iloc[:t].values.tolist()
        inc = df1_.close.iloc[:t] > df1_.open.iloc[:t]
        inc_source1.data['color'] = np.where(inc,INCREASING_COLOR,DECREASING_COLOR).tolist()

        if df1_.index[-1] != df1.index[-1]:
            for t1 in range(t,df1_.shape[0]):
                inc = df1_.close.iloc[-1] > df1_.open.iloc[-1]
                color=INCREASING_COLOR if inc else DECREASING_COLOR
                new_data = dict(
                    x1= [df1_.index[t1]],
                    Date1=[df1_.Date.values[t1]],
                    open1=[df1_.open.iloc[t1]],
                    high1=[df1_.high.iloc[t1]],
                    low1=[df1_.low.iloc[t1]],
                    close1=[df1_.close.iloc[t1]],
                    color=[color],
                )

                inc_source1.stream(new_data)

                dt1=pd.Index(df1_.Date).tz_localize(None).values

                fig1.xaxis.major_label_overrides = {
                    j: date.strftime(xaxis_dt_format) for j, date in enumerate(pd.to_datetime(dt1))
                }

            a=1

        df[i]=df1_
    print(' ### DONE ####')


# update()

curdoc().add_root(column(gridplot([[fig1] for fig1 in fig], toolbar_location="left", plot_width=1000)))
# curdoc().add_root(column(gridplot([[fig],[fig2]], toolbar_location="left", plot_width=1000)))
curdoc().add_periodic_callback(update, 5000)
curdoc().title = "OHLC"