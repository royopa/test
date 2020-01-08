import numpy as np
import mUtil as uu
import pandas as pd
from numba import njit

def findBadTicks(srs1):
    ret = np.diff(np.log(srs1.values))
    # r0=srs1.rolling(W,center=True)
    #    mean0= r0.apply(uu.mean_t)

    #    ret[isOvernight1[1:]]=ret[isOvernight1[1:]]-mean0[isOvernight1[1:]] #devolve a media de retorno, estimativa robusta do gap overnight
    # srs_ = pd.Series(np.cumsum(ret))
    srs_ = srs1
    W = 60
    nstd = 5
    nstd0 = 1.5
    # nstd=3
    # nstd0=0.5

    std0 = uu.std_t(ret) * W ** 0.5
    r = srs_.rolling(W, center=True)
    std1 = r.apply(uu.std_t)
    mean1 = r.apply(uu.mean_t)

    I = np.abs(srs1.values - mean1) > nstd * std1 + nstd0 * std0 * mean1

    return I

def equal_dicts(d1, d2, ignore_keys):
    d1_filtered = dict((k, v) for k,v in d1.items() if k not in ignore_keys)
    d2_filtered = dict((k, v) for k,v in d2.items() if k not in ignore_keys)
    return d1_filtered == d2_filtered



import xml.etree.ElementTree as ElementTree

class XmlListConfig(list):
    def __init__(self, aList):
        super(XmlListConfig, self).__init__()
        for element in aList:
            if element is not None:
                # treat like dict
                if len(element) == 1 or element[0].tag != element[1].tag:
                    self.append(XmlDictConfig(element))
                # treat like list
                elif element[0].tag == element[1].tag:
                    self.append(XmlListConfig(element))
            elif element.text:
                text = element.text.strip()
                if text:
                    self.append(text)


class XmlDictConfig(dict):
    '''
    Example usage:

    tree = ElementTree.parse('your_file.xml')
    root = tree.getroot()
    xmldict = XmlDictConfig(root)

    Or, if you want to use an XML string:

    root = ElementTree.XML(xml_string)
    xmldict = XmlDictConfig(root)

    And then use xmldict for what it is... a dict.
    '''
    def __init__(self, parent_element):
        super(XmlDictConfig,self).__init__()
        if parent_element.items():
            self.update(dict(parent_element.items()))
        for element in parent_element:
            if element is not None:
                # treat like dict - we assume that if the first two tags
                # in a series are different, then they are all different.
                if len(element) == 1 or element[0].tag != element[1].tag:
                    aDict = XmlDictConfig(element)
                # treat like list - we assume that if the first two tags
                # in a series are the same, then the rest are the same.
                else:
                    # here, we put the list in dictionary; the key is the
                    # tag name the list elements all share in common, and
                    # the value is the list itself
                    aDict = {element[0].tag: XmlListConfig(element)}
                # if the tag has attributes, add those to the dict
                if element.items():
                    aDict.update(dict(element.items()))
                self.update({element.tag: aDict})
            # this assumes that if you've got an attribute in a tag,
            # you won't be having any text. This may or may not be a
            # good idea -- time will tell. It works for the way we are
            # currently doing XML configuration files...
            elif element.items():
                self.update({element.tag: dict(element.items())})
            # finally, if there are no child tags and no attributes, extract
            # the text
            else:
                self.update({element.tag: element.text})


from lxml import etree, objectify

def removeNamespace(root):

    ####
    for elem in root.getiterator():
        if not hasattr(elem.tag, 'find'): continue  # (1)
        i = elem.tag.find('}')
        if i >= 0:
            elem.tag = elem.tag[i+1:]
    objectify.deannotate(root, cleanup_namespaces=True)


#import mDataStore.util_cython as util_cython

def df2ldict(df1):

    colObjs = [col for col in df1.columns if df1[col].dtype==object]
    df2=df1.copy()

    cats={}
    for col in colObjs:
        df2[col]=pd.Categorical(df2[col])
        cats[col]=df2[col].cat.categories
        df2[col] = df2[col].cat.codes

    v=df2.values
    index = uu.dti2x_date(df2.index)

    p_col = df1.columns.map(lambda x:0 if x in ['close','volume'] else 1)
    l_i, l_k, l_v = _convList(index.values, v, p_col.values)
    ld = [{**{'index':l_i[j]},**{l_k_1:l_v[j][i] for i,l_k_1 in enumerate(l_k_0)}} for j,l_k_0 in enumerate(l_k)]
    #this is faster (as of 2018) than Cython, pandas(to_dict) and usual python loop
    #But is slower than simply store the whole dataframe and load it in arctic
    #Arctic compreses lz4. So we will keep everything in dataframe. They might change and better
    # support for list of dicts of other sparse format (ie sparse dataframe)

    # with uu.Timer():
    #     d=_convDict(index,v,p_col.values)
    # with uu.Timer():
    #     d=util_cython._convDict(index,v,p_col.values)


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


@njit
def _convList(index,v,p_col):

    l_i=[index[0]]
    l_v=[v[0,:]]
    K=np.array([np.uint8(i) for i in range(v.shape[1])])
    l_k=[K]
    for t in range(1,v.shape[0]):
        b = np.zeros((v.shape[1],))
        for i in range(v.shape[1]):
            if p_col[i]==1:
                if v[t, i] != v[t-1, i]:
                    b[i]=1
            else:
                if not np.isnan(v[t, i]):
                    b[i]=1
        if sum(b)>0:
            l_i.append(index[t])
            l_k.append(K[b==1])
            l_v.append(v[t][b==1])

    return l_i,l_k,l_v


#
# v=np.arange(5)
# b=np.array([True,False,True,True,True])
# @njit
# def tst1(v,b):
#     b = np.zeros((v.shape[0],))==1
#     return v[b]
#
# tst1(v,b)

class LogController:

    @staticmethod
    def configure(log_path, log_file_name):

        import logging

        log_formatter = logging.Formatter(
            "%(asctime)s [%(threadName)-12.12s] [%(name)-20.20s] [%(levelname)-5.5s]  %(message)s")

        root_logger = logging.getLogger()

        file_handler = logging.FileHandler("{0}/{1}.log".format(log_path, log_file_name))
        file_handler.setFormatter(log_formatter)
        root_logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        root_logger.addHandler(console_handler)
        root_logger.setLevel(level=logging.INFO)
