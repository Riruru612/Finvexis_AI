"""
alert_engine.py
================
Deterministic alert and insight engine for the FP&A Agent.

Owns:
  - detect_fpa_alerts()  : generates structured alerts with pre-written actions
  - build_insights()     : pre-computes all data interpretations before LLM narration

No LLM calls. All decisions, thresholds, and action text are written in Python.
The LLM in narrative_engine.py only converts these outputs into fluent prose.
"""

from typing import Optional 

def detect_fpa_alerts (
budget_vs_actual :dict ,
monthly_burn :dict ,
forecasts :dict 
)->list :
    """
    Fully deterministic alert engine.
    Every alert description and action is written in Python — no LLM involvement.

    Alert types (in severity order):
        BUDGET_OVERRUN      — department already over budget         [CRITICAL]
        FORECAST_OVERRUN    — department projected to exceed budget   [HIGH]
        BUDGET_AT_RISK      — department above 85% utilization       [HIGH]
        ACCELERATING_BURN   — month-over-month spend jumped >= 30%   [MEDIUM]
        BUDGET_UNDER_UTILIZED — department below 60% utilization     [LOW]

    Args:
        budget_vs_actual: Output of build_budget_vs_actual()
        monthly_burn:     Output of build_monthly_burn()
        forecasts:        Output of forecast_quarter_end()

    Returns:
        List of alert dicts sorted by severity (CRITICAL first).
        Each alert contains: id, severity, department, department_head,
                             description, actions (list of pre-written strings)
    """
    alerts =[]

    for dept ,bva in budget_vs_actual .items ():
        burn =monthly_burn .get (dept ,{})
        forecast =forecasts .get (dept ,{})
        head =bva ["department_head"]
        overrun =bva ["variance"]
        util =bva ["utilization_pct"]
        remaining =bva ["budget_remaining"]

        if bva ["status"]=="OVER_BUDGET":
            pct_over =round (util -100 ,1 )
            alerts .append ({
            "id":"BUDGET_OVERRUN",
            "severity":"CRITICAL",
            "department":dept ,
            "department_head":head ,
            "description":(
            f"{dept } has exceeded its Q1 budget by ₹{overrun :,.0f} ({pct_over }% over). "
            f"Budget: ₹{bva ['q1_budget']:,.0f} | Actual: ₹{bva ['actual_spend']:,.0f}."
            ),
            "actions":[
            f"Place all new {dept } purchase orders on hold immediately — "
            f"department is ₹{overrun :,.0f} over budget with no remaining headroom.",
            f"Request {head } to submit a line-by-line breakdown of the ₹{bva ['actual_spend']:,.0f} "
            f"spend within 48 hours to identify what drove the overrun.",
            f"Do NOT approve any additional {dept } invoices until the overrun is explained "
            f"and a revised budget is signed off by the CFO.",
            ]
            })

        elif bva ["status"]=="AT_RISK":
            alerts .append ({
            "id":"BUDGET_AT_RISK",
            "severity":"HIGH",
            "department":dept ,
            "department_head":head ,
            "description":(
            f"{dept } has used {util }% of its Q1 budget. "
            f"Only ₹{remaining :,.0f} remaining for the rest of the quarter."
            ),
            "actions":[
            f"Freeze all discretionary {dept } spend above ₹10,000 pending CFO approval.",
            f"Notify {head } that the department has ₹{remaining :,.0f} left — "
            f"all remaining invoices must be pre-approved.",
            f"Review pending {dept } invoices (₹{bva ['amount_pending']:,.0f}) — "
            f"approve only what is contractually committed.",
            ]
            })

        if (forecast .get ("forecast_status")=="WILL_OVERRUN"
        and bva ["status"]!="OVER_BUDGET"):
            proj_total =forecast ["projected_quarter_total"]
            proj_variance =forecast ["projected_variance"]
            avg_burn =forecast ["avg_monthly_burn"]
            alerts .append ({
            "id":"FORECAST_OVERRUN",
            "severity":"HIGH",
            "department":dept ,
            "department_head":head ,
            "description":(
            f"{dept } is on track to overrun its budget by ₹{proj_variance :,.0f} "
            f"by end of Q1. Projected total: ₹{proj_total :,.0f} vs "
            f"budget ₹{forecast ['q1_budget']:,.0f}. "
            f"Current avg monthly burn: ₹{avg_burn :,.0f}."
            ),
            "actions":[
            f"Reduce {dept } monthly spend from ₹{avg_burn :,.0f} to under "
            f"₹{round (remaining /max (forecast ['months_remaining'],1 )):,.0f} "
            f"for the remaining {forecast ['months_remaining']} month(s) to stay within budget.",
            f"Identify and defer any non-critical {dept } expenditure this month.",
            f"Alert {head } that current burn rate will breach the budget — "
            f"require a corrective spend plan by end of week.",
            ]
            })

        monthly_breakdown =burn .get ("monthly_breakdown",[])
        non_zero =[m for m in monthly_breakdown if m ["spend"]>0 ]
        if len (non_zero )>=2 :
            last_mom_pct =non_zero [-1 ].get ("mom_pct")
            if last_mom_pct and last_mom_pct >=30 :
                prev_spend =non_zero [-2 ]["spend"]
                last_spend =non_zero [-1 ]["spend"]
                increase =round (last_spend -prev_spend ,0 )
                alerts .append ({
                "id":"ACCELERATING_BURN",
                "severity":"MEDIUM",
                "department":dept ,
                "department_head":head ,
                "description":(
                f"{dept } monthly spend jumped {last_mom_pct }% last month — "
                f"from ₹{prev_spend :,.0f} to ₹{last_spend :,.0f} "
                f"(increase of ₹{increase :,.0f})."
                ),
                "actions":[
                f"Ask {head } to explain the ₹{increase :,.0f} increase in {dept } spend last month — "
                f"was this planned or unplanned?",
                f"Check if any large {dept } invoices are still pending that would "
                f"accelerate the overrun further.",
                ]
                })

        if bva ["status"]=="UNDER_UTILIZED"and util <60 :
            alerts .append ({
            "id":"BUDGET_UNDER_UTILIZED",
            "severity":"LOW",
            "department":dept ,
            "department_head":head ,
            "description":(
            f"{dept } has only spent {util }% of its Q1 budget. "
            f"₹{remaining :,.0f} is unspent with the quarter ending."
            ),
            "actions":[
            f"Confirm with {head } whether planned {dept } activities were deferred "
            f"or cancelled — if cancelled, reallocate ₹{remaining :,.0f} to over-budget departments.",
            f"If spend is genuinely deferred to Q2, update the Q2 forecast accordingly.",
            ]
            })

    severity_order ={"CRITICAL":0 ,"HIGH":1 ,"MEDIUM":2 ,"LOW":3 }
    alerts .sort (key =lambda x :severity_order .get (x ["severity"],99 ))
    return alerts 

def build_insights (
query_type :str ,
budget_vs_actual :dict ,
forecasts :dict ,
monthly_burn :dict ,
alerts :list ,
what_if_result :Optional [dict ]=None 
)->dict :
    """
    Pre-computes all data interpretations before LLM narration.

    All financial interpretation happens here in Python.
    Returns a structured dict of pre-decided insights that the LLM
    only needs to convert to readable prose — no reasoning required.

    Args:
        query_type:       One of full_report | single_dept | forecast | what_if
        budget_vs_actual: Output of build_budget_vs_actual()
        forecasts:        Output of forecast_quarter_end()
        monthly_burn:     Output of build_monthly_burn()
        alerts:           Output of detect_fpa_alerts()
        what_if_result:   Output of run_what_if() or None

    Returns:
        dict containing pre-written verdicts, categorized department lists,
        totals, and the what_if_verdict (APPROVE/REJECT with reason).
    """

    over_budget_depts =[d for d ,v in budget_vs_actual .items ()if v ["status"]=="OVER_BUDGET"]
    at_risk_depts =[d for d ,v in budget_vs_actual .items ()if v ["status"]=="AT_RISK"]
    on_track_depts =[d for d ,v in budget_vs_actual .items ()if v ["status"]=="ON_TRACK"]
    underutil_depts =[d for d ,v in budget_vs_actual .items ()if v ["status"]=="UNDER_UTILIZED"]

    total_budget =sum (v ["q1_budget"]for v in budget_vs_actual .values ())
    total_actual =sum (v ["actual_spend"]for v in budget_vs_actual .values ())
    total_pending =sum (v ["amount_pending"]for v in budget_vs_actual .values ())
    total_variance =round (total_actual -total_budget ,2 )

    worst_dept =max (budget_vs_actual ,key =lambda d :budget_vs_actual [d ]["variance"])
    worst =budget_vs_actual [worst_dept ]

    best_dept =min (budget_vs_actual ,key =lambda d :budget_vs_actual [d ]["utilization_pct"])
    best =budget_vs_actual [best_dept ]

    will_overrun =[d for d ,f in forecasts .items ()if f ["forecast_status"]=="WILL_OVERRUN"]
    will_stay =[d for d ,f in forecasts .items ()if f ["forecast_status"]=="WILL_STAY_WITHIN_BUDGET"]

    what_if_verdict =None 
    if what_if_result and "error"not in what_if_result :
        wi =what_if_result 
        dept =wi ["department"]
        bva =budget_vs_actual .get (dept ,{})
        add_spend =wi ["additional_spend"]
        new_var =wi ["new_variance"]

        if wi ["already_over_budget"]:

            what_if_verdict ={
            "recommendation":"REJECT",
            "reason":(
            f"{dept } is already ₹{bva .get ('variance',0 ):,.0f} over budget. "
            f"Adding ₹{add_spend :,.0f} would increase the overrun to ₹{new_var :,.0f}. "
            f"This spend must not be approved until a budget revision is signed off."
            ),
            "before_utilization":wi ["current_utilization_pct"],
            "after_utilization":wi ["new_utilization_pct"],
            "before_variance":wi ["current_variance"],
            "after_variance":new_var ,
            }
        elif wi ["budget_impact"]=="CROSSES_BUDGET":

            what_if_verdict ={
            "recommendation":"REJECT",
            "reason":(
            f"Approving ₹{add_spend :,.0f} would push {dept } over its Q1 budget. "
            f"Current spend: ₹{wi ['current_actual']:,.0f} | "
            f"Budget: ₹{wi ['q1_budget']:,.0f} | "
            f"New total would be ₹{wi ['new_actual']:,.0f} "
            f"(₹{abs (new_var ):,.0f} over budget). "
            f"Do not approve without a formal budget amendment."
            ),
            "before_utilization":wi ["current_utilization_pct"],
            "after_utilization":wi ["new_utilization_pct"],
            "before_variance":wi ["current_variance"],
            "after_variance":new_var ,
            }
        else :

            headroom_after =wi ["budget_remaining_after"]
            what_if_verdict ={
            "recommendation":"APPROVE",
            "reason":(
            f"Approving ₹{add_spend :,.0f} keeps {dept } within its Q1 budget. "
            f"New total: ₹{wi ['new_actual']:,.0f} vs budget ₹{wi ['q1_budget']:,.0f}. "
            f"Remaining headroom after approval: ₹{headroom_after :,.0f}."
            ),
            "before_utilization":wi ["current_utilization_pct"],
            "after_utilization":wi ["new_utilization_pct"],
            "before_variance":wi ["current_variance"],
            "after_variance":new_var ,
            }

    all_actions =[]
    for alert in alerts :
        for action in alert .get ("actions",[]):
            all_actions .append ({
            "severity":alert ["severity"],
            "department":alert ["department"],
            "action":action 
            })

    return {
    "over_budget_depts":over_budget_depts ,
    "at_risk_depts":at_risk_depts ,
    "on_track_depts":on_track_depts ,
    "underutil_depts":underutil_depts ,
    "total_budget":total_budget ,
    "total_actual":total_actual ,
    "total_pending":total_pending ,
    "total_variance":total_variance ,
    "worst_dept":worst_dept ,
    "worst_dept_data":worst ,
    "best_dept":best_dept ,
    "best_dept_data":best ,
    "will_overrun_depts":will_overrun ,
    "will_stay_depts":will_stay ,
    "what_if_verdict":what_if_verdict ,
    "all_actions":all_actions ,
    }