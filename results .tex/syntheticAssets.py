# from indicator import *
from strategies import * #fixVertStrat
from asset import *
## intraday fix vert
dt_range=[dt(2002,1,5),dt.now()]
codes=mds.getDI(date_range=dt_range)
with uu.Timer():
    adii = asset.get(codes,date_range=dt_range)

vertsi=[0.5, 1.0, 2.0, 3.0, 4.0, 5.0]
# vertsi=[5.0]
vv=[int(v) if int(v)==v else v for v in vertsi]
fixVS = [fixVert(adii, name='PRE_{}A'.format(vv[i]), rebal='tuesday', vert=v,library='assetVS') for i,v in enumerate(vertsi)] #, rebal='tuesday'
for s in fixVS:
    with uu.Timer():
        s.once()
        s.save()
    #     s.update()
    # with uu.Timer():
    #     s.calc()
        # fixVert.load(s.name,library='assetVS')
        # a1=1

# with uu.Timer():
#     adii = asset.get(codes,date_range=dt_range,library=mds.onlineVS)
#
#
# fixVS = [fixVert(adii, name='PRE_{}A'.format(vv[i]), rebal='tuesday', vert=v) for i,v in enumerate(vertsi)] #, rebal='tuesday'
# for s in fixVS:
#     with uu.Timer():
#         s.once()
#         s.save()