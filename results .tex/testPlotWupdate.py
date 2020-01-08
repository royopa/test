from py_init import *
from mDataStore.globalMongo import mds
from bokeh.plotting import curdoc, figure
from bokeh.layouts import row, column, gridplot

TK='ES1 index'
TEST=False
df1 = mds.read(TK,ds.freqHelper.minute,date_range=[dt(2010,1,1),dt(2020,1,1)],library=mds.mktBars).tz_convert('America/Sao_Paulo')
# df2 = mds.read('BZ1 index',ds.freqHelper.minute,date_range=[dt(2010,1,1),dt(2020,1,1)],library=mds.mktBars).tz_convert('America/Sao_Paulo')
if TEST:
    T=1000
    df1=df1.iloc[:-T]

fig,inc_source=uu.candlestick_plot(df1,df1.md.name)

df1['Date'] = df1.index
df1['idx'] = np.arange(df1.shape[0])
df1 = df1.set_index('idx')

INCREASING_COLOR = '#17BECF'
DECREASING_COLOR = '#7F7F7F'

from bokeh.driving import count

@count()
def update(tt):
    global df1
    dt0=df1.index[-1]
    xaxis_dt_format = '%d %b %Y, %H:%M:%S'
    print(' ### READ ####')
    df1_ = mds.read(TK, ds.freqHelper.minute, date_range=[dt(2010,1,1), dt(2035, 1, 1)],
                   library=mds.mktBars).tz_convert('America/Sao_Paulo')

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
    t=len(inc_source.data['high1'])
    inc_source.data['high1']=df1_.high.iloc[:t].values.tolist()
    inc_source.data['low1'] = df1_.low.iloc[:t].values.tolist()
    inc_source.data['close1'] = df1_.close.iloc[:t].values.tolist()
    inc_source.data['open1'] = df1_.open.iloc[:t].values.tolist()
    inc_source.data['high1'] = df1_.high.iloc[:t].values.tolist()
    inc = df1_.close.iloc[:t] > df1_.open.iloc[:t]
    inc_source.data['color'] = np.where(inc,INCREASING_COLOR,DECREASING_COLOR).tolist()

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

            inc_source.stream(new_data)

            dt1=pd.Index(df1_.Date).tz_localize(None).values

            fig.xaxis.major_label_overrides = {
                i: date.strftime(xaxis_dt_format) for i, date in enumerate(pd.to_datetime(dt1))
            }

        a=1

    df1=df1_
    print(' ### DONE ####')


update()

curdoc().add_root(column(gridplot([[fig]], toolbar_location="left", plot_width=1000)))
# curdoc().add_root(column(gridplot([[fig],[fig2]], toolbar_location="left", plot_width=1000)))
curdoc().add_periodic_callback(update, 1000)
curdoc().title = "OHLC"