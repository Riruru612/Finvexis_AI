import pandas as pd 
import numpy as np 
from typing import Dict ,Any ,List 

def calculate_growth_rate (current :float ,previous :float )->float :
    if previous ==0 or pd .isna (previous ):
        return 0.0 
    return ((current -previous )/previous )*100 

def normalize_score (value :float ,min_val :float ,max_val :float ,reverse :bool =False )->float :
    if max_val ==min_val :
        return 50.0 
    score =((value -min_val )/(max_val -min_val ))*100 
    if reverse :
        score =100 -score 
    return max (0 ,min (100 ,score ))

def detect_anomalies (series :pd .Series ,threshold :float =2.0 )->List [int ]:
    if len (series )<5 :
        return []
    rolling_mean =series .rolling (window =5 ,center =True ).mean ().fillna (series .mean ())
    rolling_std =series .rolling (window =5 ,center =True ).std ().fillna (series .std ())
    z_scores =(series -rolling_mean )/rolling_std .replace (0 ,1 )
    return series .index [np .abs (z_scores )>threshold ].tolist ()

def calculate_confidence_score (series :pd .Series )->float :
    n =len (series )
    if n <3 :return 0.3 
    cv =(series .std ()/series .mean ())if series .mean ()!=0 else 1.0 
    size_factor =min (1.0 ,n /12 )
    stability_factor =max (0.0 ,1.0 -cv )
    return round ((size_factor *0.4 +stability_factor *0.6 ),4 )
