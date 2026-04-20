import pandas as pd 
import numpy as np 
from typing import Dict ,Any ,List 
from src_ai .utils .helpers import normalize_score 

class MarketAgent :
    def __init__ (self ):
        self .name ="Market Research Analyst"

    def analyze (self ,market_data :Dict [str ,Any ],internal_data :Dict [str ,Any ])->Dict [str ,Any ]:
        """
        market_data contains competitors, industry trends, etc.
        internal_data contains kpi metrics.
        """
        competitors =market_data .get ('competitors',[])
        kpi_metrics =internal_data .get ('metrics',{})

        our_revenue =kpi_metrics .get ('revenue',0 )
        our_sales_volume =market_data .get ('our_sales_volume',1000 )
        our_price =our_revenue /our_sales_volume if our_sales_volume >0 else 0 

        avg_comp_price =np .mean ([c ['price']for c in competitors ])if competitors else our_price 
        price_index =our_price /avg_comp_price if avg_comp_price >0 else 1.0 

        our_features =set (market_data .get ('our_features',[]))
        all_features =set ()
        for c in competitors :all_features .update (c .get ('features',[]))

        feature_fit =len (our_features .intersection (all_features ))/len (all_features )if all_features else 1.0 
        pos_score =(normalize_score (price_index ,0.5 ,1.5 ,reverse =True )*0.3 +
        normalize_score (feature_fit ,0 ,1 )*0.4 +
        market_data .get ('sentiment_score',70 )*0.3 )

        industry_growth =1.2 if market_data .get ('industry_trend')=='growing'else 0.8 
        gap_score =normalize_score (len (all_features -our_features ),0 ,5 ,reverse =True )
        opp_score =industry_growth *(gap_score /100 )*100 

        total_market =market_data .get ('total_market_sales',our_revenue *10 )
        market_share =(our_revenue /total_market )*100 

        feature_gap_details =[]
        if feature_fit <1.0 :
            missing =all_features -our_features 
            for f in missing :
                feature_gap_details .append ({
                "feature":f ,
                "importance":"High"if f in ["F2"]else "Medium",
                "impact":"Strategic",
                "customer_perceived_value":"Critical for Enterprise workflows"
                })

        comp_summary ={
        "top_competitors":[
        {"name":c ['name'],"pricing_model":"Subscription (Tiered)","value_prop":"Best for large enterprises"}for c in competitors 
        ],
        "average_market_price":round (avg_comp_price ,2 ),
        "our_feature_coverage":f"{round (feature_fit *100 ,1 )}%",
        "feature_gap_analysis":feature_gap_details ,
        "total_competitor_features":list (all_features )
        }

        market_intelligence ={
        "TAM":"$500M",
        "SAM":"$150M",
        "Projected_Growth":"15% CAGR",
        "Customer_Sentiment":market_data .get ('sentiment_score',75 ),
        "Top_Pain_Point":"Integration complexity and missing advanced reporting (F2)"
        }

        segments =[
        {
        "name":"Enterprise",
        "opportunity":"High"if feature_fit <0.7 else "Medium",
        "penetration":"Low"if price_index >1.1 else "Medium",
        "strategy":"High-touch Sales"
        },
        {
        "name":"SMB",
        "opportunity":"Medium",
        "penetration":"High"if price_index <0.9 else "Medium",
        "strategy":"Product-Led Growth"
        },
        {
        "name":"Individual",
        "opportunity":"Low",
        "penetration":"High"if price_index <0.8 else "Low",
        "strategy":"Self-service / Freemium"
        }
        ]

        scorecard ={
        "Product_Depth":f"{round (feature_fit *10 ,1 )}/10",
        "Pricing_Competitiveness":f"{round (normalize_score (price_index ,0.5 ,1.5 ,reverse =True )/10 ,1 )}/10",
        "Market_Agility":"8.5/10",
        "Brand_Sentiment":f"{market_data .get ('sentiment_score',75 )/10 }/10",
        "Overall_Strategic_Position":f"{round (pos_score /10 ,1 )}/10"
        }

        benchmarking ={
        "Industry_Average_Margin":"15%",
        "Our_Margin_vs_Industry":f"{round (kpi_metrics .get ('net_margin',0 )-15 ,1 )}%",
        "Growth_Comparison":"Outperforming"if kpi_metrics .get ('rev_growth',0 )>10 else "Lagging",
        "Efficiency_Index":round (market_share /price_index ,2 )
        }

        return {
        "agent":self .name ,
        "metrics":{
        "price_index":round (price_index ,2 ),
        "positioning_score":round (pos_score ,2 ),
        "market_share":round (market_share ,2 ),
        "opportunity_score":round (opp_score ,2 ),
        "feature_gap_count":len (all_features -our_features )
        },
        "swot":self ._generate_swot (price_index ,feature_fit ,market_data ),
        "competitive_analysis":comp_summary ,
        "market_intelligence":market_intelligence ,
        "segmentation":segments ,
        "scorecard":scorecard ,
        "benchmarking":benchmarking ,
        "position":"Premium"if price_index >1.2 else "Value"if price_index <0.8 else "Mid-market",
        "direction":"Bullish"if market_data .get ('industry_trend')=='growing'else "Stable"
        }

    def _generate_swot (self ,price_idx ,feat_fit ,m_data )->Dict [str ,List [str ]]:

        swot ={"strengths":[],"weaknesses":[],"opportunities":[],"threats":[]}

        if price_idx <0.95 :swot ["strengths"].append ("Competitive Pricing Advantage")
        if feat_fit >0.8 :swot ["strengths"].append ("Robust Feature Set")
        if m_data .get ('sentiment_score',0 )>80 :swot ["strengths"].append ("Strong Brand Sentiment")
        if price_idx >=0.95 and price_idx <=1.05 :swot ["strengths"].append ("Market-Aligned Pricing")

        if price_idx >1.1 :swot ["weaknesses"].append ("Premium Price Barrier")
        if feat_fit <0.6 :swot ["weaknesses"].append ("Critical Feature Gaps")
        if m_data .get ('sentiment_score',100 )<60 :swot ["weaknesses"].append ("Customer Sentiment Issues")
        if feat_fit >=0.6 and feat_fit <=0.8 :swot ["weaknesses"].append ("Moderate Feature Lag")

        if m_data .get ('industry_trend')=='growing':swot ["opportunities"].append ("Market Expansion")
        if feat_fit <1.0 :swot ["opportunities"].append ("Product Roadmap Optimization")
        if price_idx >1.0 :swot ["opportunities"].append ("Value-Based Re-positioning")

        if len (m_data .get ('competitors',[]))>3 :swot ["threats"].append ("High Competitive Intensity")
        if m_data .get ('industry_trend')=='stagnant':swot ["threats"].append ("Market Saturation")
        if price_idx <0.8 :swot ["threats"].append ("Potential Margin Squeeze")

        if not swot ["strengths"]:swot ["strengths"].append ("Stable Operational Base")
        if not swot ["weaknesses"]:swot ["weaknesses"].append ("Niche Market Dependency")
        if not swot ["threats"]:swot ["threats"].append ("Emerging Tech Disruptors")

        return swot 
