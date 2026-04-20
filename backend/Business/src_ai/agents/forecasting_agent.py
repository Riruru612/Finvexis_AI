import pandas as pd 
import numpy as np 
from typing import Dict ,Any ,List 
from sklearn .linear_model import LinearRegression 
from src_ai .utils .helpers import calculate_confidence_score 

class ForecastingAgent :
    def __init__ (self ):
        self .name ="Forecasting Agent"

    def analyze (self ,data :pd .DataFrame )->Dict [str ,Any ]:
        if len (data )<3 :
            return {"error":"Insufficient data for forecasting"}

        metrics =['revenue','expenses','churn_rate']
        forecasts ={}

        for m in metrics :
            if m in data .columns :
                forecasts [m ]=self ._predict_next (data [m ])

        realistic_forecast =forecasts .get ('revenue',{}).get ('realistic',0 )
        best_case =realistic_forecast *1.15 
        worst_case =realistic_forecast *0.85 

        confidence =calculate_confidence_score (data ['revenue'])

        sensitivity ={
        "marketing_spend_up_10":round (float (realistic_forecast *1.05 ),2 ),
        "marketing_spend_down_10":round (float (realistic_forecast *0.92 ),2 ),
        "feature_F2_launch":round (float (realistic_forecast *1.15 ),2 )
        }

        long_term_rev =[round (float (realistic_forecast *(1.02 **i )),2 )for i in range (1 ,13 )]

        return {
        "agent":self .name ,
        "scenarios":{
        "realistic":round (float (realistic_forecast ),2 ),
        "best_case":round (float (best_case ),2 ),
        "worst_case":round (float (worst_case ),2 )
        },
        "sensitivity_analysis":sensitivity ,
        "12_month_projection":long_term_rev ,
        "confidence":round (float (confidence *100 ),2 ),
        "risk_level":"High"if confidence <0.7 else "Medium"if confidence <0.85 else "Low"
        }

    def _predict_next (self ,series :pd .Series )->Dict [str ,float ]:
        y =series .values .reshape (-1 ,1 )
        X =np .arange (len (y )).reshape (-1 ,1 )
        model =LinearRegression ().fit (X ,y )
        next_val =model .predict ([[len (y )]])[0 ][0 ]
        return {"realistic":next_val ,"trend":"upward"if model .coef_ [0 ][0 ]>0 else "downward"}

    def _generate_explanation (self ,forecasts ,scenarios )->str :
        rev_trend =forecasts .get ('revenue',{}).get ('trend','stable')
        return f"Next period revenue is projected to be {scenarios ['realistic']:,.0f} with an {rev_trend } trend."
