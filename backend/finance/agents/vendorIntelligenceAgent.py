"""
vendorIntelligenceAgent.py
===========================
Vendor Intelligence Agent — Finvexis AI Finance Pipeline

Entry point for orchestrator:
    run_vendor_intelligence(query: str) -> dict

Entry point for direct use:
    run_vendor_intelligence(query: str) -> dict   (same function)

─────────────────────────────────────────────────────────────
ORCHESTRATOR INTEGRATION
─────────────────────────────────────────────────────────────
When the master orchestrator routes a query to this agent, it calls:

    from finance.agents.vendorIntelligenceAgent import run_vendor_intelligence

    result = run_vendor_intelligence(query=user_query)

The orchestrator passes a plain string query. No file upload or structured
parameters required. The agent resolves vendor identity internally via LLM.

Example orchestrator queries this agent can handle:
    "Tell me about Cloud Data Dynamics"
    "Is TechServe a risky vendor?"
    "Give me a full profile on LegalEdge"
    "Which vendor should I be most worried about?"
    "Compare all vendors by risk"
    "Show me the vendor rankings"
─────────────────────────────────────────────────────────────

Input:
    query : str — natural language query referencing a vendor

Output:
    Single vendor:
    {
        "query_type":   "single_vendor",
        "vendor_id":    str,
        "vendor_name":  str,
        "profile":      dict,       # transaction history & financial stats
        "behaviors":    list[dict], # detected behavioral patterns with evidence
        "risk_score":   int,        # 0-100 (higher = riskier)
        "risk_rating":  str,        # "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
        "narrative":    str         # LLM factual vendor assessment
    }

    All-vendor ranking:
    {
        "query_type": "all_vendors",
        "rankings":   list[dict],   # all vendors sorted by risk_score desc
        "narrative":  str           # LLM factual ranking summary
    }

Module responsibilities:
    agents/vendorIntelligenceAgent.py  — resolve_vendor(), run_vendor_intelligence(),
                                         generate_vendor_narrative(),
                                         rank_all_vendors(), generate_ranking_narrative()
    engines/vendor_profiler.py         — build_vendor_profile()
    engines/vendor_behaviors.py        — detect_vendor_behaviors(), calculate_risk_score()
"""

import os 
from typing import Optional 

from dotenv import load_dotenv 
from langchain_core .prompts import ChatPromptTemplate 
from langchain_groq import ChatGroq 
from pydantic import BaseModel ,Field 

from dummy_data import VENDOR_MASTER 
from engines .vendor_profiler import build_vendor_profile 
from engines .vendor_behaviors import detect_vendor_behaviors ,calculate_risk_score 

load_dotenv ()
GROQ_API_KEY =os .getenv ("GROQ_API_KEY")

if not GROQ_API_KEY :
    raise ValueError ("GROQ_API_KEY not found. Please add it to your .env file.")

llm =ChatGroq (model ="llama-3.1-8b-instant",api_key =GROQ_API_KEY ,temperature =0 )

class VendorResolution (BaseModel ):
    vendor_id :Optional [str ]=Field (
    default =None ,
    description =(
    "The matched vendor ID from the master list (e.g. 'V001'). "
    "Return null if query asks for all vendors or no specific vendor is mentioned."
    )
    )
    query_type :str =Field (
    description =(
    "One of: 'single_vendor' if a specific vendor is mentioned, "
    "'all_vendors' if user wants a comparison or ranking of all vendors."
    )
    )
    confidence :float =Field (
    description ="Confidence in the vendor match, 0.0 to 1.0"
    )

def resolve_vendor (query :str )->VendorResolution :
    """
    Use LLM to identify which vendor the query refers to.
    Supports fuzzy matching — partial names, abbreviations, and descriptions all match.

    Args:
        query: Raw natural language query from user or orchestrator.

    Returns:
        VendorResolution with vendor_id, query_type, and confidence.
    """
    vendor_list ="\n".join ([
    f"{vid }: {vdata ['name']} ({vdata ['category']})"
    for vid ,vdata in VENDOR_MASTER .items ()
    ])

    prompt =ChatPromptTemplate .from_messages ([
    ("system",f"""You are a vendor name resolver for a finance system.
Match the user's query to the correct vendor from this master list.
Use fuzzy matching — partial names, abbreviations, and descriptions should all match.

VENDOR MASTER:
{vendor_list }

If the user asks about all vendors, rankings, or comparisons (e.g. "which vendor is riskiest",
"compare all vendors"), set query_type to 'all_vendors' and vendor_id to null.
"""),
    ("human","{query}")
    ])

    structured_llm =llm .with_structured_output (VendorResolution )
    return (prompt |structured_llm ).invoke ({"query":query })

def generate_vendor_narrative (
vendor_name :str ,
profile :dict ,
behaviors :list ,
risk_score :int ,
risk_rating :str ,
query :str 
)->str :
    """
    Generate a factual vendor intelligence report using the LLM.

    The LLM receives pre-computed profile stats and behavior summaries.
    Its only job is to restate them as structured prose — no interpretation.

    Args:
        vendor_name: Display name of the vendor.
        profile:     Output of build_vendor_profile().
        behaviors:   Output of detect_vendor_behaviors().
        risk_score:  Output of calculate_risk_score() — score component.
        risk_rating: Output of calculate_risk_score() — rating component.
        query:       Original query for context.

    Returns:
        Formatted narrative string for CFO consumption.
    """
    behavior_summary ="\n".join ([
    f"[{b ['severity']}] {b ['behavior']}: {b ['summary']}"
    for b in behaviors 
    ])or "No behavioral anomalies detected. Vendor appears compliant."

    evidence_details ="\n".join ([
    f"{b ['behavior']} Evidence:\n"+"\n".join (f"  - {e }"for e in b ["evidence"])
    for b in behaviors 
    ])or "None"

    prompt =ChatPromptTemplate .from_messages ([
    ("system","""You are a finance reporting assistant writing a vendor intelligence report for the CFO.
Your role is strictly to restate the pre-computed data provided to you. Do NOT infer intent, motivations, or conclusions beyond what the data states.

Rules:
- Do NOT use words like "deliberate", "intentional", "suspicious intent", "likely to", "probably", or any speculative language.
- Do NOT contradict or re-interpret the provided risk_score or risk_rating.
- Do NOT add recommendations. Recommendations are provided separately by the system.
- Do NOT assess financial health or business stability of the vendor.
- State only what the numbers and flags show. If a behavior is flagged, describe what was observed, not why it happened.

Structure your response as:
1. Vendor Overview (1-2 sentences — who they are, what they supply)
2. Relationship Summary (restate spend, invoice count, compliance rate exactly as given)
3. Behavioral Findings (one paragraph per finding — describe the observed data only, most critical first)
4. Risk Rating (restate the provided score and rating label exactly — do not justify or re-score)"""),
    ("human","""
Original Query: {query}
Vendor: {vendor_name}
Category: {category}
GST Type: {gst_type}
Risk Score: {risk_score}/100 — {risk_rating}

FINANCIAL PROFILE:
- Invoices: {invoice_count}
- Total Spend: ₹{total_spend:,.0f}
- Total Tax Paid: ₹{total_tax:,.0f}
- Missing GST: ₹{missing_gst:,.0f}
- GST Compliance Rate: {gst_compliance_rate}%
- Monthly Trend: {monthly_spend}

BEHAVIORAL FINDINGS ({behavior_count} detected):
{behavior_summary}

EVIDENCE:
{evidence_details}
""")
    ])

    response =(prompt |llm ).invoke ({
    "query":query ,
    "vendor_name":vendor_name ,
    "category":profile .get ("vendor_info",{}).get ("category","Unknown"),
    "gst_type":profile .get ("gst_type","Unknown"),
    "risk_score":risk_score ,
    "risk_rating":risk_rating ,
    "invoice_count":profile .get ("invoice_count",0 ),
    "total_spend":profile .get ("total_subtotal",0 ),
    "total_tax":profile .get ("total_tax_paid",0 ),
    "missing_gst":profile .get ("missing_gst_amount",0 ),
    "gst_compliance_rate":profile .get ("gst_compliance_rate",0 ),
    "monthly_spend":profile .get ("monthly_spend",{}),
    "behavior_count":len (behaviors ),
    "behavior_summary":behavior_summary ,
    "evidence_details":evidence_details ,
    })

    return response .content 

def rank_all_vendors ()->list :
    """
    Score and rank all vendors in VENDOR_MASTER by risk score.

    Builds profile and detects behaviors for every vendor,
    then sorts by risk_score descending.

    Returns:
        List of dicts sorted by risk_score desc. Each dict contains:
            vendor_id, vendor_name, category, risk_score, risk_rating,
            behavior_count, top_behaviors (up to 3), total_spend,
            gst_compliance_rate
    """
    rankings =[]

    for vendor_id in VENDOR_MASTER :
        profile =build_vendor_profile (vendor_id )
        behaviors =detect_vendor_behaviors (vendor_id ,profile )
        score ,rating =calculate_risk_score (profile ,behaviors )

        rankings .append ({
        "vendor_id":vendor_id ,
        "vendor_name":VENDOR_MASTER [vendor_id ]["name"],
        "category":VENDOR_MASTER [vendor_id ]["category"],
        "risk_score":score ,
        "risk_rating":rating ,
        "behavior_count":len (behaviors ),
        "top_behaviors":[b ["behavior"]for b in behaviors [:3 ]],
        "total_spend":profile .get ("total_subtotal",0 ),
        "gst_compliance_rate":profile .get ("gst_compliance_rate",100 ),
        })

    rankings .sort (key =lambda x :x ["risk_score"],reverse =True )
    return rankings 

def generate_ranking_narrative (rankings :list ,query :str )->str :
    """
    Generate a factual vendor risk ranking summary using the LLM.
    LLM restates pre-computed rankings only — no inferences or recommendations.

    Args:
        rankings: Output of rank_all_vendors().
        query:    Original query for context.

    Returns:
        Narrative string under 200 words.
    """
    ranking_text ="\n".join ([
    f"{i +1 }. {r ['vendor_name']} — Risk: {r ['risk_score']}/100 ({r ['risk_rating']}) "
    f"| Behaviors: {', '.join (r ['top_behaviors'])if r ['top_behaviors']else 'None'} "
    f"| Spend: ₹{r ['total_spend']:,.0f} | GST Compliance: {r ['gst_compliance_rate']}%"
    for i ,r in enumerate (rankings )
    ])

    prompt =ChatPromptTemplate .from_messages ([
    ("system","""You are a finance reporting assistant. Write a concise vendor risk ranking summary for the CFO.
Your role is strictly to restate the pre-computed rankings provided to you.

Rules:
- Do NOT infer intent, motivations, or conclusions beyond what the data states.
- Do NOT use words like "deliberate", "intentional", "suspicious", "likely", or any speculative language.
- Do NOT contradict or re-score any vendor's risk score or rating.
- Do NOT add recommendations.
- State only what the scores, ratings, and detected behaviors show.
- Note which vendors have no detected behaviors.
Keep it under 200 words. Be direct and factual."""),
    ("human","Query: {query}\n\nRANKINGS:\n{rankings}")
    ])

    response =(prompt |llm ).invoke ({"query":query ,"rankings":ranking_text })
    return response .content 

def run_vendor_intelligence (query :str )->dict :
    """
    Main entry point for the Vendor Intelligence Agent.
    Called by the orchestrator or directly.

    Pipeline:
        1. resolve_vendor()           — LLM identifies vendor from query
        2. build_vendor_profile()     — deterministic financial stats
        3. detect_vendor_behaviors()  — deterministic pattern detection
        4. calculate_risk_score()     — deterministic 0-100 score
        5. generate_vendor_narrative() — LLM restates findings as prose

    Args:
        query: Natural language query about a vendor or vendors.

    Returns:
        For single vendor — dict with keys:
            query_type, vendor_id, vendor_name, profile,
            behaviors, risk_score, risk_rating, narrative

        For all-vendor comparison — dict with keys:
            query_type, rankings, narrative
    """

    resolution =resolve_vendor (query )

    if resolution .query_type =="all_vendors"or resolution .vendor_id is None :
        rankings =rank_all_vendors ()
        narrative =generate_ranking_narrative (rankings ,query )
        return {
        "query_type":"all_vendors",
        "rankings":rankings ,
        "narrative":narrative 
        }

    vendor_id =resolution .vendor_id 
    vendor_name =VENDOR_MASTER .get (vendor_id ,{}).get ("name",vendor_id )

    profile =build_vendor_profile (vendor_id )
    if "error"in profile :
        return {"error":profile ["error"]}

    behaviors =detect_vendor_behaviors (vendor_id ,profile )
    risk_score ,risk_rating =calculate_risk_score (profile ,behaviors )
    narrative =generate_vendor_narrative (
    vendor_name ,profile ,behaviors ,risk_score ,risk_rating ,query 
    )

    return {
    "query_type":"single_vendor",
    "vendor_id":vendor_id ,
    "vendor_name":vendor_name ,
    "profile":profile ,
    "behaviors":behaviors ,
    "risk_score":risk_score ,
    "risk_rating":risk_rating ,
    "narrative":narrative 
    }

if __name__ =="__main__":

    test_queries =[
    "Tell me about Cloud Data Dynamics",
    "Is TechServe a risky vendor?",
    "Give me a full profile on LegalEdge",
    "Which vendor should I be most worried about?",
    ]

    for q in test_queries :
        print (f"\n{'='*60 }")
        print (f"QUERY: {q }")
        print ("="*60 )

        result =run_vendor_intelligence (q )

        if result .get ("query_type")=="all_vendors":
            print ("VENDOR RISK RANKINGS:")
            for r in result ["rankings"]:
                print (
                f"  {r ['risk_score']:>3}/100 [{r ['risk_rating']:<8}] "
                f"{r ['vendor_name']} — {', '.join (r ['top_behaviors'])or 'Clean'}"
                )
            print (f"\nNARRATIVE:\n{result ['narrative']}")
        else :
            print (f"Vendor     : {result ['vendor_name']} ({result ['vendor_id']})")
            print (f"Risk Score : {result ['risk_score']}/100 — {result ['risk_rating']}")
            print (f"Behaviors  : {len (result ['behaviors'])}")
            for b in result ["behaviors"]:
                print (f"  [{b ['severity']}] {b ['behavior']}")
                for e in b ["evidence"]:
                    print (f"    → {e }")
            print (f"\nNARRATIVE:\n{result ['narrative']}")