# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 10:18:56 2019

@author: marcgut
"""
#import sys
#sys.path.append(r'F:\SISTDAD\MEMPGRP\BMORIER\python\lib')
#sys.path.append(r'Z:\Macroeconomia\codes\Projetos\MLEco')
#sys.path.append(r'Z:\Macroeconomia\codes')
#sys.path.append(r'Z:\Macroeconomia\databases')

import xlwings as xw
from S_complete import S_complete
import pandas as pd

def update_model():
    wb = xw.Book.caller()
    model_name = wb.sheets('parametros').range(6,2).value
    transf = wb.sheets('parametros').range(8,2).value
    freq_ = wb.sheets('parametros').range(7,2).value
    
    mod_obj = S_complete(model_name, transf, freq_)
    
    mongo_list = wb.sheets('parametros').range(12,2).value
    if mongo_list == 'None':
        mongo_list = None
    
    lags_x = wb.sheets('parametros').range(14,2).value
    el1 = 0
    el2 = 0
    counter = 0
    for s in lags_x:
        try:
            if counter == 0:
                el1 = int(s)
                counter += 1
            elif counter == 1:
                el2 = int(s)
        except ValueError:
            pass
    
    lags_x = tuple([el1,el2])
    
    k = wb.sheets('parametros').range(15,2).value
    if k == 'None':
        k = None
    
    paste_plan = wb.sheets('parametros').range(21,2).value
    
    config_dic = {'check_real':wb.sheets('parametros').range(9,2).value,
                  'check_seas':wb.sheets('parametros').range(10,2).value,
                  'min_y_sample':wb.sheets('parametros').range(11,2).value,
                  'mongo_list':mongo_list,
                  'lags_y':int(wb.sheets('parametros').range(13,2).value),
                  'lags_x':lags_x,
                  'k':k,
                  'prop':wb.sheets('parametros').range(16,2).value,
                  'method':wb.sheets('parametros').range(17,2).value,
                  'saz':wb.sheets('parametros').range(18,2).value,
                  'min_est_prop':wb.sheets('parametros').range(19,2).value,
                  'work_days': wb.sheets('parametros').range(20,2).value}
    
    mod_obj.run_(False, **config_dic)
    
    
    
    
    
    return









































