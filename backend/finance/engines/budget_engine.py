"""
budget_engine.py
=================
Deterministic budget calculation engine for the FP&A Agent.

Owns:
  - build_budget_vs_actual()   : variance table for all or one department
  - build_monthly_burn()       : month-over-month spend breakdown
  - forecast_quarter_end()     : projected quarter-end spend from burn rate
  - run_what_if()              : simulate impact of additional spend

No LLM calls. All outputs are plain Python dicts consumed by fpaAgent.py.
"""

import re 
from collections import defaultdict 
from typing import Optional 

from dummy_data import INVOICE_LEDGER ,DEPARTMENT_BUDGETS 

QUARTER_MONTHS =[1 ,2 ,3 ]
QUARTER_LABEL ="Q1 2026"
TOTAL_QUARTER_MONTHS =3 
MONTH_ORDER ={1 :"January 2026",2 :"February 2026",3 :"March 2026"}

def build_budget_vs_actual (department :Optional [str ]=None )->dict :
    """
    Core variance engine. Computes actual spend vs budget for all or one department.
    Excludes duplicate invoices from spend calculation.

    Args:
        department: If provided, returns data for that department only.
                    If None, returns data for all departments.

    Returns:
        dict keyed by department name. Each value contains:
            q1_budget, actual_spend, variance, utilization_pct,
            budget_remaining, invoice_count, amount_paid,
            amount_pending, status
    """
    seen_invoices =set ()
    dept_spend =defaultdict (float )
    dept_invoice_count =defaultdict (int )
    dept_pending =defaultdict (float )
    dept_paid =defaultdict (float )

    for inv in INVOICE_LEDGER :
        inv_num =inv ["invoice_number"]

        if inv_num in seen_invoices :
            continue 
        seen_invoices .add (inv_num )

        dept =inv ["department"]
        dept_spend [dept ]+=inv ["subtotal"]
        dept_invoice_count [dept ]+=1 

        if inv ["status"]=="PAID":
            dept_paid [dept ]+=inv ["total_amount"]
        else :
            dept_pending [dept ]+=inv ["total_amount"]

    results ={}
    departments =[department ]if department else list (DEPARTMENT_BUDGETS .keys ())

    for dept in departments :
        if dept not in DEPARTMENT_BUDGETS :
            continue 

        budget =DEPARTMENT_BUDGETS [dept ]["q1_budget"]
        actual =round (dept_spend .get (dept ,0.0 ),2 )
        variance =round (actual -budget ,2 )
        utilization_pct =round (actual /budget *100 ,1 )if budget >0 else 0 
        remaining =round (budget -actual ,2 )

        results [dept ]={
        "department":dept ,
        "department_head":DEPARTMENT_BUDGETS [dept ]["department_head"],
        "q1_budget":budget ,
        "actual_spend":actual ,
        "variance":variance ,
        "utilization_pct":utilization_pct ,
        "budget_remaining":remaining ,
        "invoice_count":dept_invoice_count .get (dept ,0 ),
        "amount_paid":round (dept_paid .get (dept ,0.0 ),2 ),
        "amount_pending":round (dept_pending .get (dept ,0.0 ),2 ),
        "status":(
        "OVER_BUDGET"if variance >0 
        else "AT_RISK"if utilization_pct >=85 
        else "ON_TRACK"if utilization_pct >=50 
        else "UNDER_UTILIZED"
        )
        }

    return results 

def build_monthly_burn (department :Optional [str ]=None )->dict :
    """
    Calculate month-over-month spend for each department.

    Args:
        department: If provided, returns burn data for that department only.

    Returns:
        dict keyed by department name. Each value contains:
            monthly_breakdown (list of {month, spend, mom_change, mom_pct}),
            avg_monthly_burn, peak_month
    """
    seen_invoices =set ()
    monthly =defaultdict (lambda :defaultdict (float ))

    for inv in INVOICE_LEDGER :
        inv_num =inv ["invoice_number"]
        if inv_num in seen_invoices :
            continue 
        seen_invoices .add (inv_num )

        dept =inv ["department"]
        if department and dept !=department :
            continue 

        month_label =MONTH_ORDER .get (inv ["date_issued"].month )
        if month_label :
            monthly [dept ][month_label ]+=inv ["subtotal"]

    result ={}
    departments =[department ]if department else list (DEPARTMENT_BUDGETS .keys ())

    for dept in departments :
        dept_monthly =monthly .get (dept ,{})
        months_in_order =[MONTH_ORDER [m ]for m in QUARTER_MONTHS ]

        burn_data =[]
        prev_spend =None 
        for month_label in months_in_order :
            spend =round (dept_monthly .get (month_label ,0.0 ),2 )
            mom_change =None 
            mom_pct =None 

            if prev_spend is not None and prev_spend >0 :
                mom_change =round (spend -prev_spend ,2 )
                mom_pct =round ((spend -prev_spend )/prev_spend *100 ,1 )

            burn_data .append ({
            "month":month_label ,
            "spend":spend ,
            "mom_change":mom_change ,
            "mom_pct":mom_pct 
            })
            prev_spend =spend 

        non_zero =[b ["spend"]for b in burn_data if b ["spend"]>0 ]
        avg_monthly_burn =round (sum (non_zero )/len (non_zero ),2 )if non_zero else 0.0 

        result [dept ]={
        "monthly_breakdown":burn_data ,
        "avg_monthly_burn":avg_monthly_burn ,
        "peak_month":max (burn_data ,key =lambda x :x ["spend"])["month"]if burn_data else None ,
        }

    return result 

def forecast_quarter_end (
budget_vs_actual :dict ,
monthly_burn :dict ,
department :Optional [str ]=None 
)->dict :
    """
    Project end-of-quarter spend based on average monthly burn rate.

    Assumption: positioned at end of Q1 (all 3 months elapsed).
    Months remaining = 0, so projected_total = spend_to_date.

    Args:
        budget_vs_actual: Output of build_budget_vs_actual()
        monthly_burn:     Output of build_monthly_burn()
        department:       Scope filter — None for all departments.

    Returns:
        dict keyed by department. Each value contains:
            spend_to_date, avg_monthly_burn, months_remaining,
            projected_quarter_total, projected_variance,
            projected_utilization_pct, forecast_status
    """
    months_elapsed =3 
    months_remaining =TOTAL_QUARTER_MONTHS -months_elapsed 

    forecasts ={}
    departments =[department ]if department else list (DEPARTMENT_BUDGETS .keys ())

    for dept in departments :
        if dept not in budget_vs_actual :
            continue 

        bva =budget_vs_actual [dept ]
        burn =monthly_burn .get (dept ,{})
        avg_burn =burn .get ("avg_monthly_burn",0.0 )

        dept_invoices =[
        inv for inv in INVOICE_LEDGER 
        if inv ["department"]==dept and inv ["date_issued"].month <=months_elapsed 
        ]
        seen =set ()
        spend_to_date =0.0 
        for inv in dept_invoices :
            if inv ["invoice_number"]not in seen :
                seen .add (inv ["invoice_number"])
                spend_to_date +=inv ["subtotal"]

        projected_total =round (spend_to_date +(avg_burn *months_remaining ),2 )
        budget =bva ["q1_budget"]
        projected_variance =round (projected_total -budget ,2 )
        projected_utilization =round (projected_total /budget *100 ,1 )if budget >0 else 0 

        forecasts [dept ]={
        "department":dept ,
        "spend_to_date":round (spend_to_date ,2 ),
        "avg_monthly_burn":avg_burn ,
        "months_remaining":months_remaining ,
        "projected_additional_spend":round (avg_burn *months_remaining ,2 ),
        "projected_quarter_total":projected_total ,
        "q1_budget":budget ,
        "projected_variance":projected_variance ,
        "projected_utilization_pct":projected_utilization ,
        "forecast_status":(
        "WILL_OVERRUN"if projected_variance >0 
        else "AT_RISK"if projected_utilization >=90 
        else "WILL_STAY_WITHIN_BUDGET"
        )
        }

    return forecasts 

def run_what_if (department :str ,additional_spend :float ,budget_vs_actual :dict )->dict :
    """
    Simulate the impact of an additional spend amount on a department's budget position.

    Args:
        department:       Target department name.
        additional_spend: Hypothetical additional spend in INR.
        budget_vs_actual: Output of build_budget_vs_actual().

    Returns:
        dict containing before/after financials and a budget_impact verdict:
            ALREADY_OVER_BUDGET | CROSSES_BUDGET | WITHIN_BUDGET
    """
    if department not in budget_vs_actual :
        return {"error":f"Department '{department }' not found."}

    bva =budget_vs_actual [department ]
    current_actual =bva ["actual_spend"]
    budget =bva ["q1_budget"]

    new_actual =round (current_actual +additional_spend ,2 )
    new_variance =round (new_actual -budget ,2 )
    new_utilization =round (new_actual /budget *100 ,1 )if budget >0 else 0 
    new_remaining =round (budget -new_actual ,2 )

    return {
    "department":department ,
    "additional_spend":additional_spend ,
    "current_actual":current_actual ,
    "new_actual":new_actual ,
    "q1_budget":budget ,
    "current_variance":bva ["variance"],
    "new_variance":new_variance ,
    "current_utilization_pct":bva ["utilization_pct"],
    "new_utilization_pct":new_utilization ,
    "budget_remaining_before":bva ["budget_remaining"],
    "budget_remaining_after":new_remaining ,
    "budget_impact":(
    "ALREADY_OVER_BUDGET"if bva ["variance"]>0 
    else "CROSSES_BUDGET"if new_variance >0 
    else "WITHIN_BUDGET"
    ),
    "already_over_budget":bva ["variance"]>0 ,
    "new_status":(
    "OVER_BUDGET"if new_variance >0 
    else "AT_RISK"if new_utilization >=85 
    else "ON_TRACK"
    )
    }

def extract_amount (text :str )->Optional [float ]:
    """
    Extract a rupee amount from natural language.
    Handles: "1 lakh", "50k", "₹2,00,000", plain integers.
    """
    text =text .lower ()

    lakh_match =re .search (r'(\d+(?:\.\d+)?)\s*lakh',text )
    if lakh_match :
        return float (lakh_match .group (1 ))*100000 

    k_match =re .search (r'(\d+(?:\.\d+)?)\s*k',text )
    if k_match :
        return float (k_match .group (1 ))*1000 

    match =re .search (r'(\d+[,\d]*)',text )
    if match :
        return float (match .group (1 ).replace (",",""))

    return None 