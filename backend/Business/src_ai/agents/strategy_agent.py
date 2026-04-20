from typing import Dict ,Any ,List 
import os 
import json 
from langchain_groq import ChatGroq 
from langchain_core .prompts import ChatPromptTemplate 
from dotenv import load_dotenv 

load_dotenv ()

class StrategyAgent :
    def __init__ (self ,use_llm :bool =True ,provider :str ="openai"):
        self .name ="Strategic Recommendation Agent"
        self .use_llm =use_llm 
        self .llm =self ._init_llm (provider )

    def _init_llm (self ,provider :str ):
        raw_api_key =os .getenv ("GROQ_API_KEY")
        if not raw_api_key :return None 
        api_key =raw_api_key .strip ()
        try :

            return ChatGroq (model ="llama-3.3-70b-versatile",groq_api_key =api_key ,temperature =0 )
        except :return None 

    def generate_recommendations (self ,kpi :Dict ,market :Dict ,forecast :Dict )->Dict [str ,Any ]:
        k_metrics =kpi .get ('metrics',{})

        priorities =self ._generate_base_priorities (kpi ,market ,forecast )

        if self .use_llm and self .llm :
            try :
                return self ._get_llm_strategy (kpi ,market ,forecast ,priorities )
            except :
                pass 

        risk_matrix =[
        {"risk":"Market Saturation","impact":"High","probability":"Medium","mitigation":"Differentiate via Feature F2"},
        {"risk":"Price War","impact":"Medium","probability":"Low","mitigation":"Focus on high-value Enterprise tier"},
        {"risk":"Customer Churn","impact":"Critical","probability":"High"if k_metrics .get ('churn',0 )>8 else "Low","mitigation":"Proactive success outreach"}
        ]

        resource_allocation ={
        "Product_Development":"40%",
        "Sales_Marketing":"35%",
        "Operations_Support":"15%",
        "Research_Innovation":"10%"
        }

        return {
        "agent":self .name ,
        "executive_summary":"Strategic analysis complete based on current business metrics.",
        "top_priorities":priorities [:4 ],
        "action_plan":{
        "immediate":[p ['action']for p in priorities [:2 ]],
        "medium_term":["Optimize Operational Leverage","Expand SMB Penetration"],
        "long_term":["Scale Global Operations","Invest in AI-driven R&D"]
        },
        "risk_matrix":risk_matrix ,
        "resource_allocation":resource_allocation ,
        "note":"Using rule-based fallback (LLM unavailable)."
        }

    def _generate_base_priorities (self ,kpi ,market ,forecast )->List [Dict ]:
        recs =[]
        k_metrics =kpi .get ('metrics',{})
        m_metrics =market .get ('metrics',{})

        if k_metrics .get ('net_margin',0 )<10 :
            recs .append ({
            "action":"Cost Audit & Optimization",
            "impact":"High",
            "urgency":"High",
            "effort":4 ,
            "smart_kpi":"Reduce G&A expenses by 15% in 90 days",
            "resources_required":"Finance Team, Department Heads",
            "risk_mitigation":"Ensure R&D budgets remain untouched to preserve innovation"
            })

        if k_metrics .get ('churn',0 )>8 :
            recs .append ({
            "action":"Customer Retention Program",
            "impact":"High",
            "urgency":"Critical",
            "effort":6 ,
            "smart_kpi":"Reduce churn rate to under 5% by Q3",
            "resources_required":"Customer Success Team, CRM Tools",
            "risk_mitigation":"Focus on high-LTV segments first to stabilize revenue"
            })

        if m_metrics .get ('opportunity_score',0 )>60 :
            recs .append ({
            "action":"Market Expansion (Feature Launch)",
            "impact":"Medium",
            "urgency":"Medium",
            "effort":8 ,
            "smart_kpi":"Capture 2% additional market share via Feature F2",
            "resources_required":"Product & Engineering, Marketing",
            "risk_mitigation":"A/B test feature with SMB segment before full rollout"
            })

        if m_metrics .get ('price_index',1.0 )>1.2 :
            recs .append ({
            "action":"Value Proposition Alignment",
            "impact":"High",
            "urgency":"Medium",
            "effort":5 ,
            "smart_kpi":"Increase conversion rate by 10% through value-based messaging",
            "resources_required":"Marketing, Sales Enablement",
            "risk_mitigation":"Monitor competitor price drops closely"
            })

        impact_map ={"High":10 ,"Medium":7 ,"Low":4 ,"Critical":12 }
        for r in recs :
            r ['priority_score']=(impact_map .get (r ['impact'],5 )*impact_map .get (r ['urgency'],5 ))/r ['effort']

        return sorted (recs ,key =lambda x :x ['priority_score'],reverse =True )

    def _get_llm_strategy (self ,kpi ,market ,forecast ,base_priorities )->Dict [str ,Any ]:
        prompt =ChatPromptTemplate .from_template ("""
            You are a CEO-level Strategy Consultant. 
            Analyze this DEEP BI data and produce a high-impact Strategic Execution Framework.
            
            KPI Data (incl. LTV, ROMI, Expense Breakdown): {kpi}
            Market Data (incl. TAM, Competitor Props, Feature Gap): {market}
            Forecast Data (incl. Sensitivity, 12-month projections): {forecast}
            
            Output ONLY a JSON object with this structure:
            {{
                "executive_summary": "...",
                "top_priorities": [
                    {{ 
                        "action": "...", 
                        "impact": "High/Med", 
                        "urgency": "High/Med",
                        "smart_kpi": "...",
                        "resources_required": "...",
                        "risk_mitigation": "..."
                    }}
                ],
                "action_plan": {{ 
                    "immediate": ["action1 (SMART KPI)", "action2"], 
                    "medium_term": [], 
                    "long_term": [] 
                }},
                "strategic_moat": "...",
                "resource_allocation": {{
                    "Product_Development": "X%",
                    "Sales_Marketing": "Y%",
                    "Operations": "Z%",
                    "Innovation": "W%"
                }},
                "risk_matrix": [
                    {{ "risk": "...", "impact": "...", "probability": "...", "mitigation": "..." }}
                ]
            }}
        """)
        chain =prompt |self .llm 
        resp =chain .invoke ({
        "kpi":json .dumps (kpi ),"market":json .dumps (market ),
        "forecast":json .dumps (forecast ),"base":json .dumps (base_priorities )
        })
        return json .loads (resp .content .replace ("```json","").replace ("```","").strip ())
