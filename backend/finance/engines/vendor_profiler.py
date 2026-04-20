"""
vendor_profiler.py
===================
Deterministic vendor profile builder for the Vendor Intelligence Agent.

Owns:
  - build_vendor_profile()  : builds complete transaction profile for a vendor

No LLM calls. Output is a plain Python dict consumed by:
  - vendor_behaviors.py (detect_vendor_behaviors, calculate_risk_score)
  - vendorIntelligenceAgent.py (narrative generation, entry point)
"""

from collections import defaultdict 
from dummy_data import INVOICE_LEDGER ,VENDOR_MASTER ,CLIENT 

def build_vendor_profile (vendor_id :str )->dict :
    """
    Build a complete transaction profile for a vendor from the invoice ledger.

    Computes core financials, GST compliance rate, payment status breakdown,
    monthly spend trend, and full invoice history. Determines intra/inter-state
    GST type by comparing vendor and client state codes.

    Args:
        vendor_id: Vendor ID string matching a key in VENDOR_MASTER (e.g. "V001").

    Returns:
        dict containing:
            vendor_id, vendor_info, gst_type, invoice_count,
            total_subtotal, total_tax_paid, total_amount_paid,
            expected_gst, missing_gst_amount, gst_compliance_rate,
            status_breakdown, monthly_spend, invoice_history

        Returns {"error": str} if vendor_id is not found in VENDOR_MASTER.
        Returns {"invoice_count": 0, ...} if vendor exists but has no invoices.
    """
    vendor_info =VENDOR_MASTER .get (vendor_id )
    if not vendor_info :
        return {"error":f"Vendor {vendor_id } not found in master."}

    invoices =[inv for inv in INVOICE_LEDGER if inv ["vendor_id"]==vendor_id ]

    if not invoices :
        return {
        "vendor_id":vendor_id ,
        "vendor_info":vendor_info ,
        "invoice_count":0 ,
        "message":"No invoices found for this vendor."
        }

    total_subtotal =sum (inv ["subtotal"]for inv in invoices )
    total_tax =sum (inv ["tax_amount"]for inv in invoices )
    total_amount =sum (inv ["total_amount"]for inv in invoices )
    expected_gst =round (total_subtotal *0.18 ,2 )

    invoices_with_gst =[inv for inv in invoices if inv ["tax_amount"]>0 ]
    gst_compliance_rate =round (len (invoices_with_gst )/len (invoices )*100 ,1 )
    missing_gst_amount =round (expected_gst -total_tax ,2 )

    status_breakdown =defaultdict (int )
    for inv in invoices :
        status_breakdown [inv ["status"]]+=1 

    monthly_spend =defaultdict (float )
    for inv in invoices :
        key =inv ["date_issued"].strftime ("%B %Y")
        monthly_spend [key ]+=inv ["subtotal"]

    invoice_history =sorted ([
    {
    "invoice_number":inv ["invoice_number"],
    "date":inv ["date_issued"].strftime ("%d %b %Y"),
    "subtotal":inv ["subtotal"],
    "tax_amount":inv ["tax_amount"],
    "total_amount":inv ["total_amount"],
    "status":inv ["status"],
    "department":inv ["department"],
    }
    for inv in invoices 
    ],key =lambda x :x ["date"])

    client_state =CLIENT ["state_code"]
    vendor_state =vendor_info ["state_code"]
    gst_type =(
    "Intra-State (CGST + SGST)"
    if vendor_state ==client_state 
    else "Inter-State (IGST)"
    )

    return {
    "vendor_id":vendor_id ,
    "vendor_info":vendor_info ,
    "gst_type":gst_type ,
    "invoice_count":len (invoices ),
    "total_subtotal":round (total_subtotal ,2 ),
    "total_tax_paid":round (total_tax ,2 ),
    "total_amount_paid":round (total_amount ,2 ),
    "expected_gst":expected_gst ,
    "missing_gst_amount":max (missing_gst_amount ,0.0 ),
    "gst_compliance_rate":gst_compliance_rate ,
    "status_breakdown":dict (status_breakdown ),
    "monthly_spend":dict (monthly_spend ),
    "invoice_history":invoice_history ,
    }