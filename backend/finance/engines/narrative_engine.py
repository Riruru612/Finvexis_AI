"""
narrative_engine.py
====================
LLM narrative layer for the FP&A Agent.

Owns:
  - generate_fpa_narrative()  : converts pre-computed insights into CFO-ready prose
  - cached_narrative()        : lru_cache wrapper to avoid redundant LLM calls

The LLM's ONLY job here: convert pre-written insights into fluent prose.
It does NOT interpret data, make decisions, or write recommendations.
All numbers, verdicts, and action text come from alert_engine.build_insights().
"""

import os 
import json 
from functools import lru_cache 
from typing import Optional 

from dotenv import load_dotenv 
from langchain_core .prompts import ChatPromptTemplate 
from langchain_groq import ChatGroq 

from engines .alert_engine import build_insights 

load_dotenv ()
GROQ_API_KEY =os .getenv ("GROQ_API_KEY")

if not GROQ_API_KEY :
    raise ValueError ("GROQ_API_KEY not found. Please add it to your .env file.")

llm =ChatGroq (model ="llama-3.1-8b-instant",api_key =GROQ_API_KEY ,temperature =0 )

def generate_fpa_narrative (
query :str ,
query_type :str ,
budget_vs_actual :dict ,
monthly_burn :dict ,
forecasts :dict ,
alerts :list ,
what_if_result :Optional [dict ]=None 
)->str :
    """
    Generate a CFO-ready FP&A narrative using pre-computed insights.

    Args:
        query:            Original natural language query from the user/orchestrator.
        query_type:       One of full_report | single_dept | forecast | what_if
        budget_vs_actual: Output of build_budget_vs_actual()
        monthly_burn:     Output of build_monthly_burn()
        forecasts:        Output of forecast_quarter_end()
        alerts:           Output of detect_fpa_alerts()
        what_if_result:   Output of run_what_if() or None

    Returns:
        str — formatted narrative ready for CFO consumption.
    """
    insights =build_insights (query_type ,budget_vs_actual ,forecasts ,
    monthly_burn ,alerts ,what_if_result )
    dept_names =list (budget_vs_actual .keys ())

    bva_lines ="\n".join ([
    f"  {dept }: Budget ₹{d ['q1_budget']:,.0f} | Actual ₹{d ['actual_spend']:,.0f} | "
    f"Variance ₹{d ['variance']:+,.0f} | {d ['utilization_pct']}% utilized | {d ['status']}"
    for dept ,d in budget_vs_actual .items ()
    ])

    forecast_lines ="\n".join ([
    f"  {dept }: Projected ₹{f ['projected_quarter_total']:,.0f} | "
    f"Projected variance ₹{f ['projected_variance']:+,.0f} | {f ['forecast_status']}"
    for dept ,f in forecasts .items ()
    ])

    forecast_status_map ="\n".join ([
    f"  {dept }: {f ['forecast_status']}"
    for dept ,f in forecasts .items ()
    ])

    alert_lines ="\n".join ([
    f"  [{a ['severity']}] {a ['department']}: {a ['description']}"
    for a in alerts 
    ])or "  No alerts."

    action_lines ="\n".join ([
    f"  [{a ['severity']}] {a ['department']}: {a ['action']}"
    for a in insights ["all_actions"]
    ])or "  No actions required."

    what_if_block =""
    if insights ["what_if_verdict"]:
        v =insights ["what_if_verdict"]
        wi =what_if_result 
        what_if_block =(
        f"\nWHAT-IF RESULT (verdict already decided — just report it):\n"
        f"  Verdict: {v ['recommendation']}\n"
        f"  Reason: {v ['reason']}\n"
        f"  Utilization before: {v ['before_utilization']}% → after: {v ['after_utilization']}%\n"
        f"  Variance before: ₹{v ['before_variance']:+,.0f} → after: ₹{v ['after_variance']:+,.0f}\n"
        )

    scope_instructions ={
    "full_report":(
    "Write a full Q1 FP&A report covering all departments.\n"
    "Include: executive summary, department standings table, "
    "alerts (verbatim from ALERTS block), forecast outlook, "
    "and actions (verbatim from ACTIONS block — do not rewrite them).\n"
    "Clearly distinguish forecast categories:\n"
    "- WILL_OVERRUN\n"
    "- AT_RISK\n"
    "- WILL_STAY_WITHIN_BUDGET\n"
    "Do not group AT_RISK with safe departments."
    ),
    "single_dept":(
    f"Write a focused briefing for {dept_names [0 ]} only.\n"
    "Include: budget position (1-2 sentences), burn rate trend, "
    "forecast, and actions from the ACTIONS block only. "
    "Do not mention any other department. "
    "Do not mention any other department."
    ),
    "forecast":(
    "Write a forecast-only note.\n"
    "You MUST group departments into EXACTLY three sections:\n\n"
    "1. WILL_OVERRUN:\n"
    "- List only departments with forecast_status = WILL_OVERRUN\n\n"
    "2. AT_RISK:\n"
    "- List only departments with forecast_status = AT_RISK\n\n"
    "3. WILL_STAY_WITHIN_BUDGET:\n"
    "- List only departments with forecast_status = WILL_STAY_WITHIN_BUDGET\n\n"
    "Do NOT mix categories.\n"
    "Do NOT call AT_RISK departments safe.\n"
    "Use ONLY the FORECASTS block.\n"
    "Do not include a full budget table."
    ),
    "what_if":(
    f"Write a one-department what-if analysis for {dept_names [0 ]}.\n"
    "State: what was simulated, the verdict from the WHAT-IF RESULT block "
    "(APPROVE or REJECT), the exact reason, and nothing else. "
    "Do not include other departments. Do not rewrite the verdict."
    ),
    }

    scope_instruction =scope_instructions .get (query_type ,scope_instructions ["full_report"])

    table_lines ="\n".join ([
    f"| {dept } | ₹{d ['q1_budget']:,.0f} | ₹{d ['actual_spend']:,.0f} | "
    f"₹{d ['variance']:+,.0f} | {d ['utilization_pct']}% | "
    f"{d ['status']} | {forecasts [dept ]['forecast_status']} |"
    for dept ,d in budget_vs_actual .items ()
    ])

    prompt =ChatPromptTemplate .from_messages ([
    ("system",f"""You are an FP&A analyst converting pre-computed data into a professional report.

{scope_instruction }

STRICT RULES:
1. Valid departments: {', '.join (dept_names )}. Never mention any other department.
2. Never calculate, estimate, or infer any number — use only what is in the data blocks.
3. Never rewrite the ACTIONS — copy them exactly as given.
4. For what-if: the verdict (APPROVE/REJECT) is already decided — just report it clearly.
5. Do not use phrases like "monitor spend" or "track burn rate".
6. Departments with ON_TRACK or UNDER_UTILIZED status are performing within budget.
7. If projected total equals actual spend, treat it as final actual, not a forecast.
8. Clearly distinguish between:
   - WILL_STAY_WITHIN_BUDGET
   - AT_RISK (near budget limit)
   - WILL_OVERRUN
"""),
    ("human","""Query: {query}
Quarter: Q1 2026

DEPARTMENT TABLE (STRICT — DO NOT MODIFY):
| Department | Budget | Actual | Variance | Utilization | Status | Forecast |
| --- | --- | --- | --- | --- | --- | --- |
{table_lines}

BUDGET VS ACTUAL:
{bva_lines}

FORECASTS:
{forecast_lines}

FORECAST STATUS (STRICT — DO NOT CHANGE):
{forecast_status_map}

ALERTS:
{alert_lines}

ACTIONS (copy these verbatim into recommendations — do not rewrite):
{action_lines}
{what_if_block}
""")
    ])

    response =(prompt |llm ).invoke ({
    "query":query ,
    "bva_lines":bva_lines ,
    "forecast_lines":forecast_lines ,
    "forecast_status_map":forecast_status_map ,
    "table_lines":table_lines ,
    "alert_lines":alert_lines ,
    "action_lines":action_lines ,
    "what_if_block":what_if_block ,
    })

    return response .content 

@lru_cache (maxsize =100 )
def cached_narrative (
query :str ,
query_type :str ,
bva_str :str ,
burn_str :str ,
forecast_str :str ,
alerts_str :str ,
what_if_str :str 
)->str :
    """
    lru_cache wrapper around generate_fpa_narrative.
    All dict arguments are passed as JSON strings for hashability.

    Args:
        query, query_type: passed through directly
        bva_str, burn_str, forecast_str, alerts_str, what_if_str:
            JSON-serialized versions of the corresponding dicts/lists.
            Pass "null" for what_if_str when no what-if simulation was run.

    Returns:
        Narrative string (from cache or freshly generated).
    """
    return generate_fpa_narrative (
    query ,
    query_type ,
    json .loads (bva_str ),
    json .loads (burn_str ),
    json .loads (forecast_str ),
    json .loads (alerts_str ),
    json .loads (what_if_str )if what_if_str !="null"else None 
    )