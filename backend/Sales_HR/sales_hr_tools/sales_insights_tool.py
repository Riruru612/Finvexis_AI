from langchain .tools import tool 
from langchain_groq import ChatGroq 
from langchain_core .prompts import ChatPromptTemplate 
from db .db import get_connection 
from dotenv import load_dotenv 
import os 
from collections import Counter ,defaultdict 

load_dotenv ()

llm =ChatGroq (
model ="llama-3.1-8b-instant",
groq_api_key =os .getenv ("GROQ_API_KEY")or os .getenv ("GROQ_API")
)

def calculate_rich_metrics ():
    """
    DETERMINISTIC INTELLIGENCE ENGINE
    Calculates all metrics and prepares business-impact context in Python.
    """
    conn =get_connection ()
    cursor =conn .cursor ()
    cursor .execute ("SELECT id, name, email, company, status, deal_stage, lead_score FROM customers")
    customers =cursor .fetchall ()
    cursor .execute ("SELECT customer_id, type FROM interactions")
    interactions =cursor .fetchall ()
    conn .close ()

    if not customers :
        return None 

    total =len (customers )
    stage_counts =Counter ([c [5 ].lower ()if c [5 ]else 'new'for c in customers ])
    int_map =defaultdict (int )
    for cid ,_ in interactions :
        int_map [cid ]+=1 

    closed =stage_counts .get ('closed',0 )or stage_counts .get ('closed_won',0 )
    lost =stage_counts .get ('lost',0 )or stage_counts .get ('closed_lost',0 )
    conv_rate =(closed /total *100 )if total >0 else 0 
    win_rate =(closed /(closed +lost )*100 )if (closed +lost )>0 else 0 

    new =stage_counts .get ('new',0 )
    qualified =stage_counts .get ('qualified',0 )
    proposal =stage_counts .get ('proposal',0 )
    q_to_p =(proposal /(qualified +proposal )*100 )if (qualified +proposal )>0 else 0 
    p_to_c =(closed /(proposal +closed )*100 )if (proposal +closed )>0 else 0 

    if q_to_p <40 and qualified >0 :
        bottleneck ="Qualification Stage"
        impact =f"Leads are stalling before reaching the proposal stage (only {q_to_p :.1f}% progression)."
        action ="Increase the frequency of personalized follow-ups for qualified leads to move them to 'Proposal'."
    elif p_to_c <50 and proposal >0 :
        bottleneck ="Proposal Stage"
        impact =f"Deals are stalling after the proposal is sent ({p_to_c :.1f}% closing rate)."
        action ="Schedule objection-handling calls immediately after sending proposals to address pricing or contract concerns."
    else :
        bottleneck ="Top of Funnel"
        impact ="Your funnel is efficient, but your lead volume is too low to drive significant growth."
        action ="Focus on outbound lead generation and marketing campaigns to increase the number of 'New' leads."

    inactive =[c for c in customers if int_map [c [0 ]]==0 ]
    inactive_count =len (inactive )
    inactive_pct =(inactive_count /total *100 )if total >0 else 0 
    avg_ints =len (interactions )/total if total >0 else 0 

    high_score_inactive =[c for c in customers if (c [6 ]or 0 )>=80 and int_map [c [0 ]]==0 ]
    top_lead_names =[c [1 ]for c in sorted (customers ,key =lambda x :x [6 ]or 0 ,reverse =True )[:3 ]]

    return {
    "SUMMARY":{
    "metrics":f"Conversion: {conv_rate :.1f}%, Win Rate: {win_rate :.1f}%, Leads: {total }, Closed: {closed }",
    "context":f"Overall performance is stable. The funnel is currently dominated by {stage_counts .most_common (1 )[0 ][0 ].upper ()} deals."
    },
    "PROBLEM":{
    "metrics":f"Primary Bottleneck: {bottleneck }. Progression Rate: {q_to_p if bottleneck =='Qualification'else p_to_c :.1f}%.",
    "context":f"This stage is where your pipeline is leaking most. {impact }"
    },
    "METRIC":{
    "metrics":f"Conv: {conv_rate :.1f}%, Win: {win_rate :.1f}%, Leads: {total }, Avg Lead Score: {sum ([c [6 ]for c in customers if c [6 ]])/len ([c for c in customers if c [6 ]])if [c for c in customers if c [6 ]]else 0 :.1f}",
    "context":"These represent your core success KPIs."
    },
    "ENGAGEMENT":{
    "metrics":f"Avg Interactions: {avg_ints :.1f} per lead. Inactive leads: {inactive_count } ({inactive_pct :.1f}%).",
    "context":f"Engagement activity shows {inactive_pct :.1f}% of your leads are currently getting zero attention."
    },
    "PRIORITY":{
    "metrics":f"Neglected Leads: {len (high_score_inactive )} high-score leads (80+) with zero interaction.",
    "context":f"You should immediately focus on {', '.join (top_lead_names )} as they are your highest-value opportunities."
    },
    "ACTION":{
    "metrics":f"Top Priority: {action }",
    "context":f"Based on the {bottleneck } bottleneck, this action will have the highest ROI on your sales growth."
    }
    }

@tool 
def sales_insights_tool (query :str ):
    """
    Production-Level Sales Intelligence Assistant.
    Handles 6 categories: SUMMARY, PROBLEM, METRIC, ENGAGEMENT, PRIORITY, ACTION.
    """
    data =calculate_rich_metrics ()
    if not data :
        return "No CRM data found."

    q =query .lower ()

    if any (k in q for k in ["action","improve","fix","strategy","what to do","increase"]):
        intent ="ACTION"
    elif any (k in q for k in ["problem","stuck","bottleneck","why","leakage","wrong"]):
        intent ="PROBLEM"
    elif any (k in q for k in ["metric","rate","percentage","how many","win rate","conversion rate"]):
        intent ="METRIC"
    elif any (k in q for k in ["engagement","activity","follow","inactive","interaction"]):
        intent ="ENGAGEMENT"
    elif any (k in q for k in ["priority","focus","important","potential"]):
        intent ="PRIORITY"
    else :

        intent ="SUMMARY"

    fact_set =data [intent ]

    prompt =ChatPromptTemplate .from_template ("""
You are a senior Sales Strategy Consultant.
Explain the provided DATA FACT to the user in simple, professional English (3-4 lines).

USER QUESTION: {query}
INTENT: {intent}
DATA FACT: {metrics}
BUSINESS CONTEXT: {context}

INSTRUCTIONS:
1. Directly answer the user's question using the metrics provided.
2. Explain the *meaning* and *impact* of the numbers (e.g., "This means 1 in 10 leads are converting").
3. For ACTION intent, provide a specific, confident strategy based on the metrics.
4. For PROBLEM intent, highlight exactly where the funnel is leaking.
5. Use natural, conversational language. Avoid sounding like a data dump.
6. STRICT: Use ONLY the provided numbers. Do NOT hallucinate.
7. Length: Exactly 3-4 lines of simple English.
8. Start with "Sales Insights: "
""")

    try :
        chain =prompt |llm 
        response =chain .invoke ({
        "query":query ,
        "intent":intent ,
        "metrics":fact_set ["metrics"],
        "context":fact_set ["context"]
        })
        return response .content .strip ()
    except Exception as e :
        return f"Sales Insights: {fact_set ['metrics']} {fact_set ['context']}"
