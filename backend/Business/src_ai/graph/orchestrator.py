from concurrent .futures import ThreadPoolExecutor 
from typing import Dict ,Any ,List 
import pandas as pd 
from src_ai .agents .kpi_agent import KPIAgent 
from src_ai .agents .market_agent import MarketAgent 
from src_ai .agents .forecasting_agent import ForecastingAgent 
from src_ai .agents .strategy_agent import StrategyAgent 
from src_ai .utils .data_processing import clean_business_data 

class FinvexisOrchestrator :
    def __init__ (self ,use_llm =True ,llm_provider ="google"):
        self .kpi_agent =KPIAgent ()
        self .market_agent =MarketAgent ()
        self .forecast_agent =ForecastingAgent ()
        self .strategy_agent =StrategyAgent (use_llm =use_llm ,provider =llm_provider )

    def run_full_analysis (self ,raw_data :pd .DataFrame ,market_context :Dict )->Dict [str ,Any ]:
        df =clean_business_data (raw_data )

        with ThreadPoolExecutor ()as executor :
            kpi_f =executor .submit (self .kpi_agent .analyze ,df )
            forecast_f =executor .submit (self .forecast_agent .analyze ,df )

            kpi_res =kpi_f .result ()
            forecast_res =forecast_f .result ()

            market_res =self .market_agent .analyze (market_context ,kpi_res )
            strategy_res =self .strategy_agent .generate_recommendations (kpi_res ,market_res ,forecast_res )

        return {
        "kpi":kpi_res ,
        "market":market_res ,
        "forecast":forecast_res ,
        "strategy":strategy_res ,
        "timestamp":pd .Timestamp .now ().isoformat ()
        }
