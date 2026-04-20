"""
corporateAuditor.py
====================
Corporate Auditor Agent — Finvexis AI Finance Pipeline

Entry point for orchestrator:
    run_auditor(query: str) -> dict

Entry point for direct use:
    run_auditor(query: str) -> dict   (same function, works both ways)

─────────────────────────────────────────────────────────────
ORCHESTRATOR INTEGRATION
─────────────────────────────────────────────────────────────
When the master orchestrator routes a query to this agent, it calls:

    from finance.agents.auditorAgent import run_auditor

    result = run_auditor(query=user_query)

The orchestrator passes a plain string query. No file upload or structured
parameters required. The agent parses time scope internally via LLM.

Example orchestrator queries this agent can handle:
    "Give me a full audit report"
    "Audit Q1 2026"
    "Anything suspicious in March?"
    "What happened last quarter?"
    "Run an audit for January 2026"
    "Are there any anomalies in the ledger?"
─────────────────────────────────────────────────────────────

Input:
    query : str  — natural language query with optional time scope
                   e.g. "Full audit", "Audit Q1 2026", "Audit March", "Anything suspicious last quarter?"

Output:
    {
        "scope":         str,           # e.g. "Q1 2026", "March 2026", "Full Ledger"
        "period_report": dict,          # aggregated financials for the scope
        "anomalies":     list[dict],    # all detected anomalies with severity
        "narrative":     str            # LLM executive audit summary (facts only)
    }
"""

import os 
from datetime import date 
from collections import defaultdict 
from dotenv import load_dotenv 

from langchain_core .prompts import ChatPromptTemplate 
from langchain_groq import ChatGroq 
from pydantic import BaseModel ,Field 
from typing import Optional 

from dummy_data import (
INVOICE_LEDGER ,
DEPARTMENT_BUDGETS ,
VENDOR_MASTER ,
)

load_dotenv ()
GROQ_API_KEY =os .getenv ("GROQ_API_KEY")

if not GROQ_API_KEY :
    raise ValueError ("GROQ_API_KEY not found. Please add it to your .env file.")

llm =ChatGroq (model ="llama-3.1-8b-instant",api_key =GROQ_API_KEY ,temperature =0 )

class TimeScope (BaseModel ):
    scope_type :str =Field (
    description ="One of: 'full', 'quarter', 'month'"
    )
    year :Optional [int ]=Field (
    description ="4-digit year if mentioned, else null. Default to 2026 if quarter or month is mentioned without a year.",
    default =2026 
    )
    quarter :Optional [int ]=Field (
    description ="Quarter number 1-4 if scope_type is 'quarter', else null",
    default =None 
    )
    month :Optional [int ]=Field (
    description ="Month number 1-12 if scope_type is 'month', else null",
    default =None 
    )
    scope_label :str =Field (
    description ="Human-readable label like 'Q1 2026', 'March 2026', or 'Full Ledger'"
    )

def parse_time_scope (query :str )->TimeScope :
    """Use LLM to extract time scope from a natural language query."""
    today =date .today ()

    prompt =ChatPromptTemplate .from_messages ([
    ("system",f"""You are a time scope extractor for a finance auditor.
Today's date is {today .strftime ('%B %d, %Y')}.
Extract the time scope from the user's query.

Rules:
- If no time is mentioned, scope_type = 'full'
- 'this quarter' = current quarter based on today's date
- 'last quarter' = previous quarter
- 'this month' = current month
- 'last month' = previous month
- If a quarter is mentioned (e.g., Q1, Q2), set scope_type='quarter' and set the quarter field to the integer 1, 2, 3, or 4.
- Always default year to 2026 if not mentioned but a quarter or month is referenced
"""),
    ("human","{query}")
    ])

    structured_llm =llm .with_structured_output (TimeScope )
    result =(prompt |structured_llm ).invoke ({"query":query })
    return result 

def filter_ledger (scope :TimeScope )->list :
    """Filter INVOICE_LEDGER based on parsed time scope."""
    if scope .scope_type =="full":
        return INVOICE_LEDGER 

    filtered =[]
    for inv in INVOICE_LEDGER :
        inv_date =inv ["date_issued"]

        if scope .scope_type =="month":
            if inv_date .month ==scope .month and inv_date .year ==scope .year :
                filtered .append (inv )

        elif scope .scope_type =="quarter":
            quarter_months ={
            1 :[1 ,2 ,3 ],
            2 :[4 ,5 ,6 ],
            3 :[7 ,8 ,9 ],
            4 :[10 ,11 ,12 ],
            }
            q_val =scope .quarter 
            if not q_val :
                if "1"in scope .scope_label :q_val =1 
                elif "2"in scope .scope_label :q_val =2 
                elif "3"in scope .scope_label :q_val =3 
                elif "4"in scope .scope_label :q_val =4 
                else :q_val =1 
            if (
            inv_date .month in quarter_months .get (q_val ,[])
            and inv_date .year ==scope .year 
            ):
                filtered .append (inv )

    return filtered 

def build_period_report (invoices :list )->dict :
    """Aggregate key financial metrics for the filtered invoice set."""
    if not invoices :
        return {"error":"No invoices found for this time period."}

    total_subtotal =0.0 
    total_tax =0.0 
    total_amount =0.0 
    by_department =defaultdict (lambda :{"subtotal":0.0 ,"tax":0.0 ,"total":0.0 ,"count":0 })
    by_vendor =defaultdict (lambda :{"subtotal":0.0 ,"tax":0.0 ,"total":0.0 ,"count":0 })
    by_month =defaultdict (lambda :{"subtotal":0.0 ,"total":0.0 ,"count":0 })
    by_status =defaultdict (int )

    for inv in invoices :
        total_subtotal +=inv ["subtotal"]
        total_tax +=inv ["tax_amount"]
        total_amount +=inv ["total_amount"]

        dept =inv ["department"]
        by_department [dept ]["subtotal"]+=inv ["subtotal"]
        by_department [dept ]["tax"]+=inv ["tax_amount"]
        by_department [dept ]["total"]+=inv ["total_amount"]
        by_department [dept ]["count"]+=1 

        vendor =inv ["vendor_name"]
        by_vendor [vendor ]["subtotal"]+=inv ["subtotal"]
        by_vendor [vendor ]["tax"]+=inv ["tax_amount"]
        by_vendor [vendor ]["total"]+=inv ["total_amount"]
        by_vendor [vendor ]["count"]+=1 

        month_key =inv ["date_issued"].strftime ("%B %Y")
        by_month [month_key ]["subtotal"]+=inv ["subtotal"]
        by_month [month_key ]["total"]+=inv ["total_amount"]
        by_month [month_key ]["count"]+=1 

        by_status [inv ["status"]]+=1 

    expected_gst =round (total_subtotal *0.18 ,2 )
    missing_gst =round (expected_gst -total_tax ,2 )

    return {
    "invoice_count":len (invoices ),
    "total_subtotal":round (total_subtotal ,2 ),
    "total_tax_collected":round (total_tax ,2 ),
    "total_amount_payable":round (total_amount ,2 ),
    "expected_gst":expected_gst ,
    "estimated_missing_gst":max (missing_gst ,0.0 ),
    "by_department":dict (by_department ),
    "by_vendor":dict (by_vendor ),
    "by_month":dict (by_month ),
    "by_status":dict (by_status ),
    }

def detect_anomalies (invoices :list ,scope :TimeScope )->list :
    """
    Run all anomaly detection rules on the filtered invoice set.
    Returns a list of anomaly dicts with severity and description.
    """
    anomalies =[]

    seen_invoice_numbers ={}
    for inv in invoices :
        num =inv ["invoice_number"]
        if num in seen_invoice_numbers :
            anomalies .append ({
            "id":"DUPLICATE_INVOICE",
            "severity":"CRITICAL",
            "vendor":inv ["vendor_name"],
            "invoice_numbers":[num ],
            "amount":inv ["total_amount"],
            "description":(
            f"Invoice {num } appears more than once. "
            f"First seen on {seen_invoice_numbers [num ].strftime ('%d %b %Y')}, "
            f"duplicate dated {inv ['date_issued'].strftime ('%d %b %Y')}. "
            f"Potential double payment of ₹{inv ['total_amount']:,.0f}."
            )
            })
        else :
            seen_invoice_numbers [num ]=inv ["date_issued"]

    missing_gst_by_vendor =defaultdict (list )
    for inv in invoices :
        if inv ["tax_amount"]==0 and inv ["subtotal"]>0 :
            expected =round (inv ["subtotal"]*0.18 ,2 )
            missing_gst_by_vendor [inv ["vendor_name"]].append ({
            "invoice_number":inv ["invoice_number"],
            "subtotal":inv ["subtotal"],
            "expected_gst":expected ,
            "date":inv ["date_issued"].strftime ("%d %b %Y")
            })

    for vendor ,flagged in missing_gst_by_vendor .items ():
        total_missing =sum (f ["expected_gst"]for f in flagged )
        severity ="CRITICAL"if len (flagged )>=3 else "HIGH"if len (flagged )==2 else "MEDIUM"
        anomalies .append ({
        "id":"MISSING_GST",
        "severity":severity ,
        "vendor":vendor ,
        "invoice_numbers":[f ["invoice_number"]for f in flagged ],
        "amount":total_missing ,
        "description":(
        f"{vendor } has {len (flagged )} invoice(s) with ₹0 GST. "
        f"Estimated unpaid tax: ₹{total_missing :,.0f}. "
        f"{'Systemic pattern — all invoices from this vendor are missing GST.'if len (flagged )>=2 else 'Verify with vendor.'}"
        )
        })

    by_month =defaultdict (float )
    for inv in invoices :
        key =inv ["date_issued"].strftime ("%B %Y")
        by_month [key ]+=inv ["subtotal"]

    if len (by_month )>=2 :
        month_totals =list (by_month .values ())
        avg =sum (month_totals )/len (month_totals )
        for month_name ,total in by_month .items ():
            if total >avg *1.4 :
                anomalies .append ({
                "id":"SPENDING_SPIKE",
                "severity":"HIGH",
                "vendor":"Multiple Vendors",
                "invoice_numbers":[],
                "amount":round (total ,2 ),
                "description":(
                f"Spending in {month_name } (₹{total :,.0f}) is "
                f"{round ((total -avg )/avg *100 )}% above the period average "
                f"(₹{avg :,.0f}). Recommend reviewing all invoices for this month."
                )
                })

    tds_threshold =30000 
    tds_margin =1500 
    by_vendor_subtotals =defaultdict (list )

    for inv in invoices :
        by_vendor_subtotals [inv ["vendor_name"]].append ({
        "invoice_number":inv ["invoice_number"],
        "subtotal":inv ["subtotal"],
        "date":inv ["date_issued"].strftime ("%d %b %Y")
        })

    for vendor ,inv_list in by_vendor_subtotals .items ():
        under_threshold =[
        i for i in inv_list 
        if (tds_threshold -tds_margin )<=i ["subtotal"]<tds_threshold 
        ]
        if len (under_threshold )>=2 :
            subtotals_list =[f"₹{i ['subtotal']:,.0f}"for i in under_threshold ]

            anomalies .append ({
            "id":"TDS_THRESHOLD_GAMING",
            "severity":"HIGH",
            "vendor":vendor ,
            "invoice_numbers":[i ["invoice_number"]for i in under_threshold ],
            "amount":sum (i ["subtotal"]for i in under_threshold ),

            "description":(
            f"{vendor } has {len (under_threshold )} invoice(s) with subtotals "
            f"within ₹{tds_margin :,} of the ₹{tds_threshold :,} TDS threshold (Section 194J). "
            f"Subtotals: {subtotals_list }. "
            f"All {len (under_threshold )} invoices fall within ₹{tds_margin :,} of the threshold. "
            f"Flag raised for Tax team review."
            )
            })

    vendor_prices =defaultdict (list )
    for inv in invoices :
        for item in inv ["line_items"]:
            vendor_prices [inv ["vendor_name"]].append ({
            "date":inv ["date_issued"],
            "unit_price":item ["unit_price"],
            "description":item ["description"]
            })

    for vendor ,price_records in vendor_prices .items ():

        price_records .sort (key =lambda x :x ["date"])
        if len (price_records )>=2 :
            first_price =price_records [0 ]["unit_price"]
            last_price =price_records [-1 ]["unit_price"]
            if first_price >0 :
                hike_pct =(last_price -first_price )/first_price *100 
                if hike_pct >=10 :
                    anomalies .append ({
                    "id":"VENDOR_RATE_HIKE",
                    "severity":"MEDIUM",
                    "vendor":vendor ,
                    "invoice_numbers":[],
                    "amount":round (last_price -first_price ,2 ),
                    "description":(
                    f"{vendor } unit price increased {round (hike_pct )}% "
                    f"from ₹{first_price :,.0f} to ₹{last_price :,.0f} "
                    f"between {price_records [0 ]['date'].strftime ('%b %Y')} "
                    f"and {price_records [-1 ]['date'].strftime ('%b %Y')}. "
                    f"Verify contract terms."
                    )
                    })

    for inv in invoices :
        if "late invoice"in inv .get ("notes","").lower ():
            anomalies .append ({
            "id":"LATE_INVOICING",
            "severity":"LOW",
            "vendor":inv ["vendor_name"],
            "invoice_numbers":[inv ["invoice_number"]],
            "amount":inv ["total_amount"],
            "description":(
            f"{inv ['vendor_name']} submitted {inv ['invoice_number']} late. "
            f"Work completed in a prior period but invoiced on "
            f"{inv ['date_issued'].strftime ('%d %b %Y')}. "
            f"May cause cash flow and accrual mismatches."
            )
            })

    severity_order ={"CRITICAL":0 ,"HIGH":1 ,"MEDIUM":2 ,"LOW":3 }
    anomalies .sort (key =lambda x :severity_order .get (x ["severity"],99 ))

    return anomalies 

def generate_audit_narrative (
scope_label :str ,
period_report :dict ,
anomalies :list ,
query :str 
)->str :
    """Generate a professional executive audit summary using the LLM."""

    severity_counts =defaultdict (int )
    for a in anomalies :
        severity_counts [a ["severity"]]+=1 

    anomaly_summary ="\n".join ([
    f"[{a ['severity']}] {a ['id']} — {a ['description']}"
    for a in anomalies 
    ])or "No anomalies detected."

    prompt =ChatPromptTemplate .from_messages ([
    ("system","""You are a finance reporting assistant writing an audit summary for the Finance Director.
Your role is strictly to restate the pre-computed data provided to you. Do NOT infer intent, motivations, or conclusions beyond what the data states.

Rules:
- Do NOT use words like "deliberate", "intentional", "suspicious intent", "likely to", "probably", or any speculative language.
- Do NOT add recommendations. These are provided separately by the system.
- Do NOT calculate, estimate, or infer any number — use only what is in the data blocks.
- State only what the numbers and anomaly flags show. Describe what was observed, not why it happened.
- Never contradict or re-interpret a provided severity rating.

Structure your response as:
1. Audit Scope & Overview (1-2 sentences — scope and invoice count only)
2. Financial Summary (restate the provided numbers exactly)
3. Findings (one paragraph per anomaly, most critical first — describe observed data only)"""),
    ("human","""
Audit Scope: {scope}
Original Query: {query}

PERIOD REPORT:
- Invoices Analysed: {invoice_count}
- Total Payable: ₹{total_amount:,.0f}
- Tax Collected: ₹{total_tax:,.0f}
- Estimated Missing GST: ₹{missing_gst:,.0f}
- Status Breakdown: {status}

ANOMALIES DETECTED ({total_anomalies} total — {critical} CRITICAL, {high} HIGH, {medium} MEDIUM, {low} LOW):
{anomaly_summary}
""")
    ])

    response =(prompt |llm ).invoke ({
    "scope":scope_label ,
    "query":query ,
    "invoice_count":period_report .get ("invoice_count",0 ),
    "total_amount":period_report .get ("total_amount_payable",0 ),
    "total_tax":period_report .get ("total_tax_collected",0 ),
    "missing_gst":period_report .get ("estimated_missing_gst",0 ),
    "status":period_report .get ("by_status",{}),
    "total_anomalies":len (anomalies ),
    "critical":severity_counts ["CRITICAL"],
    "high":severity_counts ["HIGH"],
    "medium":severity_counts ["MEDIUM"],
    "low":severity_counts ["LOW"],
    "anomaly_summary":anomaly_summary ,
    })

    return response .content 

def run_auditor (query :str )->dict :
    """
    Main entry point for the Corporate Auditor agent.

    Args:
        query: Natural language audit request with optional time scope.
               Examples:
                 "Give me a full audit report"
                 "Audit Q1 2026"
                 "Anything suspicious in March?"
                 "What happened last quarter?"

    Returns:
        dict with keys: scope, period_report, anomalies, narrative
    """

    scope =parse_time_scope (query )

    invoices =filter_ledger (scope )

    if not invoices :
        return {
        "scope":scope .scope_label ,
        "period_report":{},
        "anomalies":[],
        "narrative":f"No invoices found for the requested period: {scope .scope_label }."
        }

    period_report =build_period_report (invoices )

    anomalies =detect_anomalies (invoices ,scope )

    narrative =generate_audit_narrative (scope .scope_label ,period_report ,anomalies ,query )

    return {
    "scope":scope .scope_label ,
    "period_report":period_report ,
    "anomalies":anomalies ,
    "narrative":narrative 
    }

if __name__ =="__main__":
    import json 

    test_queries =[
    "Give me a full audit report",
    "Audit Q1 2026",
    "Anything suspicious in March?",
    ]

    for q in test_queries :
        print (f"\n{'='*60 }")
        print (f"QUERY: {q }")
        print ('='*60 )

        result =run_auditor (q )

        print (f"Scope       : {result ['scope']}")
        print (f"Invoices    : {result ['period_report'].get ('invoice_count',0 )}")
        print (f"Total Payable: ₹{result ['period_report'].get ('total_amount_payable',0 ):,.0f}")
        print (f"Missing GST : ₹{result ['period_report'].get ('estimated_missing_gst',0 ):,.0f}")
        print (f"Anomalies   : {len (result ['anomalies'])}")
        for a in result ["anomalies"]:
            print (f"  [{a ['severity']}] {a ['id']} — {a ['vendor']}")
        print (f"\nNARRATIVE:\n{result ['narrative']}")