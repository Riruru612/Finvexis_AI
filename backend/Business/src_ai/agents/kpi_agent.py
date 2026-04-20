import pandas as pd 
import numpy as np 
from typing import Dict ,Any ,List 
from src_ai .utils .helpers import calculate_growth_rate ,normalize_score ,detect_anomalies 

class KPIAgent :
    def __init__ (self ):
        self .name ="Business KPI Tracker"

    def analyze (self ,data :pd .DataFrame )->Dict [str ,Any ]:
        if data .empty :
            return {"error":"No data provided"}

        latest =data .iloc [-1 ]
        previous =data .iloc [-2 ]if len (data )>1 else latest 

        revenue =float (latest .get ('revenue',0 ))
        expenses =float (latest .get ('expenses',0 ))
        profit =revenue -expenses 

        prev_revenue =float (previous .get ('revenue',0 ))
        prev_expenses =float (previous .get ('expenses',0 ))

        rev_growth =calculate_growth_rate (revenue ,prev_revenue )
        exp_growth =calculate_growth_rate (expenses ,prev_expenses )

        net_margin =(profit /revenue *100 )if revenue >0 else 0 

        cac =float (latest .get ('marketing_spend',0 )/latest .get ('customers_acquired',1 ))if 'customers_acquired'in latest and latest ['customers_acquired']>0 else 0 

        churn =float (latest .get ('churn_rate',0 ))
        if 'customers_lost'in latest and 'active_customers'in previous :
             churn =(latest ['customers_lost']/previous ['active_customers']*100 )

        retention =100 -churn 

        avg_revenue_per_user =round (float (revenue /latest ['active_customers']),2 )if 'active_customers'in latest and latest ['active_customers']>0 else 0 
        ltv =round (float (avg_revenue_per_user /(churn /100 )),2 )if churn >0 else round (float (avg_revenue_per_user *12 ),2 )

        marketing_spend =float (latest .get ('marketing_spend',0 ))
        romi =round (float (revenue /marketing_spend ),2 )if marketing_spend >0 else 0 

        expense_breakdown ={
        "COGS":round (float (expenses *0.4 ),2 ),
        "Marketing & Sales":round (float (marketing_spend ),2 ),
        "R&D":round (float (expenses *0.25 ),2 ),
        "G&A":round (float (expenses *0.15 ),2 )
        }

        segment_metrics ={
        "Enterprise":{"LTV":round (float (ltv *2.5 ),2 ),"CAC":round (float (cac *3 ),2 ),"Revenue_Share":"45%"},
        "SMB":{"LTV":round (float (ltv ),2 ),"CAC":round (float (cac ),2 ),"Revenue_Share":"35%"},
        "Individual":{"LTV":round (float (ltv *0.4 ),2 ),"CAC":round (float (cac *0.5 ),2 ),"Revenue_Share":"20%"}
        }

        health_score =round (float (self ._calculate_health_score (rev_growth ,net_margin ,churn ,cac ,revenue ,expenses )),2 )

        anomalies ={}
        for col in ['revenue','expenses','churn_rate']:
            if col in data .columns :
                anomalies [col ]=detect_anomalies (data [col ])

        observations =[]
        if rev_growth >10 :observations .append ("Strong revenue growth detected.")
        elif rev_growth <0 :observations .append ("Revenue decline observed.")

        if net_margin <5 :observations .append ("Net margins are thin; consider cost optimization.")
        if exp_growth >rev_growth :observations .append ("Expenses are scaling faster than revenue.")
        if cac >(ltv /3 ):observations .append ("High CAC relative to LTV; acquisition efficiency is low.")

        growth_status ="Expanding"if rev_growth >5 else "Declining"if rev_growth <-5 else "Stable"

        efficiency_metrics ={
        "Revenue_per_Active_Customer":round (float (avg_revenue_per_user ),2 ),
        "Burn_Rate":round (float (expenses ),2 ),
        "Runway_Months":round (float (revenue /expenses *12 ),1 )if expenses >0 else 12.0 ,
        "Operating_Leverage":round (float (rev_growth /exp_growth ),2 )if exp_growth !=0 else 0.0 ,
        "Profit_Efficiency":round (float (profit /marketing_spend ),2 )if marketing_spend >0 else 0.0 
        }

        return {
        "agent":self .name ,
        "metrics":{
        "revenue":revenue ,
        "expenses":expenses ,
        "profit":profit ,
        "rev_growth":round (rev_growth ,2 ),
        "rev_growth_status":growth_status ,
        "net_margin":round (net_margin ,2 ),
        "cac":round (cac ,2 ),
        "churn":round (churn ,2 ),
        "retention":round (retention ,2 ),
        "ltv":round (ltv ,2 ),
        "romi":round (romi ,2 ),
        "health_score":round (health_score ,2 ),
        "expense_breakdown":expense_breakdown ,
        "segment_performance":segment_metrics ,
        "efficiency":efficiency_metrics 
        },
        "anomalies":anomalies ,
        "observations":observations ,
        "status":"Good"if health_score >75 else "Warning"if health_score >50 else "Critical"
        }

    def _calculate_health_score (self ,rev_growth ,margin ,churn ,cac ,rev ,exp )->float :
        s1 =normalize_score (rev_growth ,-10 ,20 )*0.3 
        s2 =normalize_score (margin ,0 ,25 )*0.3 
        s3 =normalize_score (churn ,2 ,15 ,reverse =True )*0.2 
        s4 =(100 if rev >exp else 0 )*0.2 
        return s1 +s2 +s3 +s4 
