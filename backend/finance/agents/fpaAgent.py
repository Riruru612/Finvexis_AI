"""
fpaAgent.py
============
FP&A (Financial Planning & Analysis) Agent — Finvexis AI Finance Pipeline

Entry point for orchestrator:
    run_fpa(query: str) -> dict

Entry point for direct use:
    run_fpa(query: str) -> dict   (same function)

Input:
    query : str — natural language FP&A query
                  e.g. "How are we tracking against budget this quarter?"
                       "Which department is over budget?"
                       "Give me the burn rate for IT"
                       "Will we stay within budget by end of Q1?"
                       "What if IT spends another ₹50,000?"
                       "Full FP&A report"

Output:
    {
        "query_type":       str,            # "full_report" | "single_dept" | "forecast" | "what_if"
        "scope":            str,            # human-readable scope label
        "budget_vs_actual": dict,           # per-department variance breakdown
        "monthly_burn":     dict,           # month-over-month spend per department
        "forecasts":        dict,           # projected quarter-end spend per department
        "alerts":           list[dict],     # budget alerts with severity and pre-written actions
        "narrative":        str             # LLM CFO-ready executive summary
        "what_if_result":   dict            # only present for what_if queries
    }

Module responsibilities:
    fpaAgent.py          — query parsing + entry point (run_fpa) only
    engines/budget_engine.py   — build_budget_vs_actual, build_monthly_burn,
                                 forecast_quarter_end, run_what_if, extract_amount
    engines/alert_engine.py    — detect_fpa_alerts, build_insights
    engines/narrative_engine.py — generate_fpa_narrative, cached_narrative
"""

import os 
import json 
from typing import Optional 

from dotenv import load_dotenv 
from langchain_core .prompts import ChatPromptTemplate 
from langchain_groq import ChatGroq 
from pydantic import BaseModel ,Field 

from dummy_data import DEPARTMENT_BUDGETS 
from engines .budget_engine import (
build_budget_vs_actual ,
build_monthly_burn ,
forecast_quarter_end ,
run_what_if ,
extract_amount ,
)
from engines .alert_engine import detect_fpa_alerts 
from engines .narrative_engine import cached_narrative 

load_dotenv ()
GROQ_API_KEY =os .getenv ("GROQ_API_KEY")

if not GROQ_API_KEY :
    raise ValueError ("GROQ_API_KEY not found. Please add it to your .env file.")

llm =ChatGroq (model ="llama-3.1-8b-instant",api_key =GROQ_API_KEY ,temperature =0 )

QUARTER_LABEL ="Q1 2026"

DEPT_ALIASES ={
"IT":["it","tech","technology"],
"Marketing":["marketing","ads","advertising"],
"Operations":["operations","ops"],
"HR":["hr","human resources"],
"Legal":["legal"]
}

class FPAQuery (BaseModel ):
    query_type :str =Field (
    description =(
    "One of: "
    "'full_report' — overall Q1 budget vs actual for all departments; "
    "'single_dept' — analysis focused on one department; "
    "'forecast' — project end-of-quarter spend based on burn rate; "
    "'what_if' — simulate impact of additional spend on a department."
    )
    )
    department :Optional [str ]=Field (
    description =(
    "Department name if query_type is 'single_dept', 'forecast' for one dept, "
    "or 'what_if'. Must match one of: IT, Marketing, Operations, HR, Legal. "
    "Return null for full_report or cross-department queries."
    ),
    default =None 
    )
    what_if_amount :Optional [float ]=Field (
    description =(
    "Additional spend amount in INR for what_if queries. "
    "Extract the number from phrases like 'another ₹50,000' or 'spend 1 lakh more'. "
    "Return null if not a what_if query."
    ),
    default =None 
    )

def parse_fpa_query (query :str )->FPAQuery :
    """
    LLM fallback parser — called only when smart_parse_query() cannot match.
    Classifies query type and extracts department + amount if applicable.
    """
    dept_list =", ".join (DEPARTMENT_BUDGETS .keys ())

    prompt =ChatPromptTemplate .from_messages ([
    ("system",f"""You are an FP&A query classifier for a finance system.
Extract the query type and any relevant parameters.

Valid departments: {dept_list }
Use fuzzy matching for department names (e.g. "tech team" = IT, "ads" = Marketing).

For what_if queries, extract the rupee amount even if written as "1 lakh" (=100000),
"50k" (=50000), or "₹2,00,000" (=200000).
"""),
    ("human","{query}")
    ])

    structured_llm =llm .with_structured_output (FPAQuery )
    return (prompt |structured_llm ).invoke ({"query":query })

def smart_parse_query (query :str )->FPAQuery :
    """
    Deterministic query classifier. Handles common patterns with regex/string
    matching to avoid unnecessary LLM calls. Falls back to parse_fpa_query()
    only when no pattern matches.
    """
    q =query .lower ()

    if "what if"in q :
        amount =extract_amount (q )
        for dept ,aliases in DEPT_ALIASES .items ():
            if any (alias in q for alias in aliases ):
                return FPAQuery (
                query_type ="what_if",
                department =dept ,
                what_if_amount =amount 
                )

    for dept in DEPARTMENT_BUDGETS :
        if dept .lower ()in q :
            return FPAQuery (query_type ="single_dept",department =dept )

    if any (kw in q for kw in ["over budget","exceeded","forecast","overspend"]):
        return FPAQuery (query_type ="forecast")

    if any (kw in q for kw in ["full","report","budget"]):
        return FPAQuery (query_type ="full_report")

    return parse_fpa_query (query )

def run_fpa (query :str )->dict :
    """
    Main entry point for the FP&A Agent.
    Called by the orchestrator (via agent_name + query) or directly.

    Pipeline:
        1. Parse query intent (deterministic first, LLM fallback)
        2. Run all calculations — pure Python, no LLM
        3. Run what-if simulation if applicable — pure Python
        4. Generate narrative — LLM converts pre-written insights to prose only

    Args:
        query: Natural language FP&A query.
               Examples:
                 "How are we tracking against budget this quarter?"
                 "Which department is over budget?"
                 "Give me the burn rate for IT"
                 "Will Marketing stay within budget?"
                 "What if IT spends another ₹50,000?"
                 "Full FP&A report for Q1"

    Returns:
        dict with keys: query_type, scope, budget_vs_actual, monthly_burn,
                        forecasts, alerts, narrative
                        + what_if_result (only for what_if queries)
    """

    parsed =smart_parse_query (query )
    query_type =parsed .query_type 
    department =parsed .department 
    what_if_amount =parsed .what_if_amount 

    scope =(
    f"{department } Department — {QUARTER_LABEL }"
    if department else 
    f"All Departments — {QUARTER_LABEL }"
    )

    budget_vs_actual =build_budget_vs_actual (department )
    monthly_burn =build_monthly_burn (department )
    forecasts =forecast_quarter_end (budget_vs_actual ,monthly_burn ,department )
    alerts =detect_fpa_alerts (budget_vs_actual ,monthly_burn ,forecasts )

    what_if_result =None 
    if query_type =="what_if"and department and what_if_amount :
        what_if_result =run_what_if (department ,what_if_amount ,budget_vs_actual )

    narrative =cached_narrative (
    query ,
    query_type ,
    json .dumps (budget_vs_actual ,sort_keys =True ),
    json .dumps (monthly_burn ,sort_keys =True ),
    json .dumps (forecasts ,sort_keys =True ),
    json .dumps (alerts ,sort_keys =True ),
    json .dumps (what_if_result ,sort_keys =True )if what_if_result else "null",
    )

    result ={
    "query_type":query_type ,
    "scope":scope ,
    "budget_vs_actual":budget_vs_actual ,
    "monthly_burn":monthly_burn ,
    "forecasts":forecasts ,
    "alerts":alerts ,
    "narrative":narrative ,
    }

    if what_if_result :
        result ["what_if_result"]=what_if_result 

    return result 

if __name__ =="__main__":

    test_queries =[
    "Full FP&A report for Q1",
    "Which department is over budget?",
    "Give me the IT department burn rate",
    "What if IT spends another ₹1,00,000 next month?",
    ]

    for q in test_queries :
        print (f"\n{'='*60 }")
        print (f"QUERY: {q }")
        print ("="*60 )

        result =run_fpa (q )

        print (f"Scope      : {result ['scope']}")
        print (f"Query Type : {result ['query_type']}")
        print ()

        print ("BUDGET VS ACTUAL:")
        for dept ,d in result ["budget_vs_actual"].items ():
            bar_filled =int (min (d ["utilization_pct"],100 )/5 )
            bar ="█"*bar_filled +"░"*(20 -bar_filled )
            print (
            f"  {dept :<12} [{bar }] {d ['utilization_pct']:>6.1f}%  "
            f"₹{d ['actual_spend']:>10,.0f} / ₹{d ['q1_budget']:>10,.0f}  "
            f"[{d ['status']}]"
            )

        print ()
        print (f"ALERTS ({len (result ['alerts'])}):")
        for a in result ["alerts"]:
            print (f"  [{a ['severity']}] {a ['id']} — {a ['department']}")

        if result .get ("what_if_result"):
            wi =result ["what_if_result"]
            print ()
            print ("WHAT-IF RESULT:")
            print (f"  {wi ['department']}: ₹{wi ['current_actual']:,.0f} → ₹{wi ['new_actual']:,.0f}")
            impact_map ={
            "ALREADY_OVER_BUDGET":"Already over budget ⚠️",
            "CROSSES_BUDGET":"Will cross budget ⚠️",
            "WITHIN_BUDGET":"Within budget "
            }
            print (f"  Budget impact: {impact_map .get (wi ['budget_impact'],wi ['budget_impact'])}")
            print (f"  New status: {wi ['new_status']}")

        print (f"\nNARRATIVE:\n{result ['narrative']}")