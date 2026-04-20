"""
vendor_behaviors.py
====================
Deterministic behavioral pattern detection and risk scoring for the Vendor Intelligence Agent.

Owns:
  - detect_vendor_behaviors()  : detects 6 behavioral patterns from invoice history
  - calculate_risk_score()     : converts detected behaviors into a 0-100 risk score

No LLM calls. All thresholds, severities, and evidence strings are written in Python.
The LLM in vendorIntelligenceAgent.py only restates these outputs as prose.

Behavior catalog:
  RATE_HIKE_TRAJECTORY        — unit price increased >= 10% across analysis period   [HIGH/MEDIUM]
  TDS_THRESHOLD_GAMING        — 2+ invoices within ₹1,500 of the ₹30,000 TDS limit  [HIGH]
  GST_NON_COMPLIANCE          — invoices with ₹0 tax on non-zero subtotal            [CRITICAL/HIGH]
  CHRONIC_LATE_INVOICING      — invoices submitted after the billing period          [MEDIUM/LOW]
  HIGH_SPEND_CONCENTRATION    — vendor accounts for >= 25% of total ledger spend     [MEDIUM]
  DUPLICATE_INVOICE_SUBMISSION — same invoice number submitted more than once         [CRITICAL]
"""

from dummy_data import INVOICE_LEDGER ,VENDOR_MASTER 

def detect_vendor_behaviors (vendor_id :str ,profile :dict )->list :
    """
    Deep behavioral analysis for a specific vendor.

    Runs 6 deterministic checks against the invoice ledger.
    Each detected behavior includes: behavior name, severity, evidence list,
    and a factual summary string (no inferred intent or speculative language).

    Args:
        vendor_id: Vendor ID string (e.g. "V001").
        profile:   Output of build_vendor_profile() for this vendor.
                   Used for pre-computed stats (gst_compliance_rate, total_subtotal).

    Returns:
        List of behavior dicts sorted by severity (CRITICAL first).
        Each dict contains: behavior, severity, evidence (list[str]), summary (str).
        Returns [] if vendor has no invoices.
    """
    behaviors =[]
    invoices =[inv for inv in INVOICE_LEDGER if inv ["vendor_id"]==vendor_id ]

    if not invoices :
        return behaviors 

    price_timeline =[]
    for inv in sorted (invoices ,key =lambda x :x ["date_issued"]):
        for item in inv ["line_items"]:
            price_timeline .append ({
            "date":inv ["date_issued"],
            "invoice":inv ["invoice_number"],
            "description":item ["description"],
            "unit_price":item ["unit_price"],
            "month":inv ["date_issued"].strftime ("%B %Y")
            })

    if len (price_timeline )>=2 :
        first =price_timeline [0 ]
        last =price_timeline [-1 ]
        if first ["unit_price"]>0 :
            total_hike_pct =(last ["unit_price"]-first ["unit_price"])/first ["unit_price"]*100 
            if total_hike_pct >=10 :

                mom_hikes =[]
                for i in range (1 ,len (price_timeline )):
                    prev =price_timeline [i -1 ]["unit_price"]
                    curr =price_timeline [i ]["unit_price"]
                    if prev >0 and curr !=prev :
                        pct =round ((curr -prev )/prev *100 ,1 )
                        mom_hikes .append (
                        f"{price_timeline [i ]['month']}: ₹{prev :,.0f} → ₹{curr :,.0f} "
                        f"({'+'if pct >0 else ''}{pct }%)"
                        )

                behaviors .append ({
                "behavior":"RATE_HIKE_TRAJECTORY",
                "severity":"HIGH"if total_hike_pct >=20 else "MEDIUM",
                "evidence":mom_hikes ,
                "summary":(
                f"Unit price increased {round (total_hike_pct )}% over the analysis period "
                f"(₹{first ['unit_price']:,.0f} → ₹{last ['unit_price']:,.0f}). "
                f"{'Unit price has increased each consecutive month.'if len (mom_hikes )>=2 else 'Single price change detected.'} "
                f"Review contract for agreed rate schedules."
                )
                })

    TDS_THRESHOLD =30000 
    TDS_MARGIN =1500 
    under_threshold_invoices =[
    inv for inv in invoices 
    if (TDS_THRESHOLD -TDS_MARGIN )<=inv ["subtotal"]<TDS_THRESHOLD 
    ]

    if len (under_threshold_invoices )>=2 :
        gap_from_threshold =[TDS_THRESHOLD -inv ["subtotal"]for inv in under_threshold_invoices ]
        behaviors .append ({
        "behavior":"TDS_THRESHOLD_GAMING",
        "severity":"HIGH",
        "evidence":[
        f"{inv ['invoice_number']} ({inv ['date_issued'].strftime ('%b %Y')}): "
        f"₹{inv ['subtotal']:,.0f} — ₹{TDS_THRESHOLD -inv ['subtotal']:,.0f} below threshold"
        for inv in under_threshold_invoices 
        ],
        "summary":(
        f"{len (under_threshold_invoices )} invoices with subtotals within "
        f"₹{TDS_MARGIN :,} of the ₹{TDS_THRESHOLD :,} TDS threshold (Section 194J). "
        f"Gaps from threshold: {[f'₹{g :,.0f}'for g in gap_from_threshold ]}. "
        f"All {len (under_threshold_invoices )} invoices fall within ₹{TDS_MARGIN :,} of the threshold. "
        f"Flag raised for Tax team review."
        )
        })

    missing_gst_invoices =[
    inv for inv in invoices 
    if inv ["tax_amount"]==0 and inv ["subtotal"]>0 
    ]
    if missing_gst_invoices :
        total_missing =sum (round (inv ["subtotal"]*0.18 ,2 )for inv in missing_gst_invoices )
        compliance_rate =profile .get ("gst_compliance_rate",0 )
        severity ="CRITICAL"if len (missing_gst_invoices )==len (invoices )else "HIGH"
        behaviors .append ({
        "behavior":"GST_NON_COMPLIANCE",
        "severity":severity ,
        "evidence":[
        f"{inv ['invoice_number']} ({inv ['date_issued'].strftime ('%b %Y')}): "
        f"₹0 GST on ₹{inv ['subtotal']:,.0f} subtotal "
        f"(expected ₹{inv ['subtotal']*0.18 :,.0f})"
        for inv in missing_gst_invoices 
        ],
        "summary":(
        f"GST compliance rate: {compliance_rate }%. "
        f"{len (missing_gst_invoices )} of {len (invoices )} invoices show ₹0 tax. "
        f"Total estimated unpaid GST: ₹{total_missing :,.0f}. "
        f"{'All invoices from this vendor are non-compliant.'if severity =='CRITICAL'else 'Partial compliance — follow up on flagged invoices.'}"
        )
        })

    late_invoices =[
    inv for inv in invoices 
    if "late invoice"in inv .get ("notes","").lower ()
    ]
    if late_invoices :
        behaviors .append ({
        "behavior":"CHRONIC_LATE_INVOICING",
        "severity":"MEDIUM"if len (late_invoices )>=2 else "LOW",
        "evidence":[
        f"{inv ['invoice_number']}: {inv ['notes']}"
        for inv in late_invoices 
        ],
        "summary":(
        f"{len (late_invoices )} invoice(s) submitted significantly after the work period. "
        f"This creates accrual mismatches and makes it difficult to close monthly books accurately. "
        f"{'Recurring pattern — contractual invoicing deadlines should be enforced.'if len (late_invoices )>=2 else 'Isolated instance — follow up with vendor.'}"
        )
        })

    total_ledger_spend =sum (inv ["subtotal"]for inv in INVOICE_LEDGER )
    vendor_spend =profile .get ("total_subtotal",0 )
    concentration_pct =(
    round (vendor_spend /total_ledger_spend *100 ,1 )
    if total_ledger_spend >0 else 0 
    )

    if concentration_pct >=25 :
        behaviors .append ({
        "behavior":"HIGH_SPEND_CONCENTRATION",
        "severity":"MEDIUM",
        "evidence":[
        f"Vendor accounts for {concentration_pct }% of total Q1 ledger spend",
        f"Vendor spend: ₹{vendor_spend :,.0f} vs Total ledger: ₹{total_ledger_spend :,.0f}"
        ],
        "summary":(
        f"This vendor represents {concentration_pct }% of total expenditure in the analysis period. "
        f"High dependency on a single vendor creates supply chain and negotiation risk."
        )
        })

    invoice_numbers =[inv ["invoice_number"]for inv in invoices ]
    duplicates =[num for num in invoice_numbers if invoice_numbers .count (num )>1 ]
    unique_duplicates =list (set (duplicates ))

    for dup_num in unique_duplicates :
        dup_invoices =[inv for inv in invoices if inv ["invoice_number"]==dup_num ]
        behaviors .append ({
        "behavior":"DUPLICATE_INVOICE_SUBMISSION",
        "severity":"CRITICAL",
        "evidence":[
        f"{inv ['invoice_number']} dated {inv ['date_issued'].strftime ('%d %b %Y')} "
        f"— ₹{inv ['total_amount']:,.0f}"
        for inv in dup_invoices 
        ],
        "summary":(
        f"Invoice {dup_num } was submitted {len (dup_invoices )} times. "
        f"Potential double payment of ₹{dup_invoices [0 ]['total_amount']:,.0f}. "
        f"Immediate action required — put on payment hold pending vendor confirmation."
        )
        })

    severity_order ={"CRITICAL":0 ,"HIGH":1 ,"MEDIUM":2 ,"LOW":3 }
    behaviors .sort (key =lambda x :severity_order .get (x ["severity"],99 ))

    return behaviors 

def calculate_risk_score (profile :dict ,behaviors :list )->tuple [int ,str ]:
    """
    Calculate a 0-100 risk score from profile stats and detected behaviors.

    Scoring:
        CRITICAL behavior : +35 points
        HIGH behavior     : +20 points
        MEDIUM behavior   : +10 points
        LOW behavior      : +5  points
        Zero GST compliance rate bonus penalty : +15
        More pending than paid invoices penalty : +5
        Score is capped at 100.

    Rating thresholds:
        >= 70 → CRITICAL
        >= 45 → HIGH
        >= 20 → MEDIUM
        <  20 → LOW

    Args:
        profile:   Output of build_vendor_profile().
        behaviors: Output of detect_vendor_behaviors().

    Returns:
        Tuple of (score: int, rating: str).
    """
    score =0 

    severity_weights ={"CRITICAL":35 ,"HIGH":20 ,"MEDIUM":10 ,"LOW":5 }
    for b in behaviors :
        score +=severity_weights .get (b ["severity"],0 )

    if profile .get ("gst_compliance_rate",100 )==0 :
        score +=15 

    status =profile .get ("status_breakdown",{})
    pending =status .get ("PENDING",0 )
    paid =status .get ("PAID",0 )
    if pending >paid :
        score +=5 

    score =min (score ,100 )

    if score >=70 :
        rating ="CRITICAL"
    elif score >=45 :
        rating ="HIGH"
    elif score >=20 :
        rating ="MEDIUM"
    else :
        rating ="LOW"

    return score ,rating 