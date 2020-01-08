import numpy as np

def _convDict(index,v,p_col):

    l=[]
    d0={}
    d0[np.uint8(0)]=index[0]
    for i in range(v.shape[1]):
        d0[np.uint8(i+1)]=v[0,i]
    l.append(d0)
    for t in range(v.shape[0]):
        d0={}
        d0[np.uint8(0)] = index[t]
        for i in range(v.shape[1]):
            if p_col[i]==1:
                if v[t, i] != v[t-1, i]:
                    d0[np.uint8(i + 1)] = v[0, i]
            else:
                if not np.isnan(v[t, i]):
                    d0[np.uint8(i + 1)] = v[0, i]
        if len(d0)>1:
            l.append(d0)

    return l