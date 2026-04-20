"""
invoice_tax_engine.py
======================
Deterministic Indian tax engine and risk scorer for the Invoice Agent.

Owns:
  - calculate_tax()  : GST routing (Intra/Inter-state) + TDS 194J detection
  - score_risks()    : 4 deterministic risk rules against extracted invoice data

No LLM calls. All thresholds and rules are written in Python.
Output is consumed by invoiceAgent.py for narrative generation and ledger writing.

Tax rules applied:
  GST  — 18% flat rate (SaaS/Services standard)
         Intra-state → 9% CGST + 9% SGST (same first-2 digits in GSTIN)
         Inter-state → 18% IGST
  TDS  — Section 194J: 10% on technical/professional services > ₹30,000

Risk rules:
  DUPLICATE_INVOICE — invoice number already exists in the processed set  [CRITICAL]
  TAX_MISSING       — invoice shows ₹0 tax but GST is applicable          [HIGH]
  INVALID_GSTIN     — vendor GSTIN length != 15 characters                [MEDIUM]
  TDS_REQUIRED      — TDS deduction required before payment               [MEDIUM]
"""

TDS_SERVICE_KEYWORDS =[
"consulting","software","saas","professional",
"architecture","hosting","technical","advisory"
]

TDS_THRESHOLD =30000 
TDS_RATE =0.10 
GST_RATE =0.18 

def calculate_tax (invoice :dict )->dict :
    """
    Calculate applicable Indian taxes for an extracted invoice.

    Determines GST type (Intra/Inter-state) by comparing the first two
    characters of vendor and client GSTINs (state codes).
    Applies TDS Section 194J if subtotal > ₹30,000 and invoice contains
    technical/professional service keywords.

    Args:
        invoice: Output dict from extract_invoice().

    Returns:
        dict containing:
            estimated_gst  : float — 18% of subtotal
            gst_type       : str   — routing description with amounts
            tds_applicable : bool
            tds_amount     : float — 10% of subtotal if applicable, else 0.0
            tds_section    : str | None — "Section 194J (10%)" or None
    """
    subtotal =invoice .get ("subtotal",0.0 )

    tax_info ={
    "estimated_gst":round (subtotal *GST_RATE ,2 ),
    "gst_type":"Unknown",
    "tds_applicable":False ,
    "tds_amount":0.0 ,
    "tds_section":None 
    }

    v_gstin =invoice .get ("vendor_gstin")
    c_gstin =invoice .get ("client_gstin")

    if v_gstin and c_gstin and len (v_gstin )>=2 and len (c_gstin )>=2 :
        if v_gstin [:2 ]==c_gstin [:2 ]:
            cgst =round (subtotal *0.09 ,2 )
            sgst =round (subtotal *0.09 ,2 )
            tax_info ["gst_type"]=(
            f"Intra-State: 9% CGST (₹{cgst :,.2f}) + 9% SGST (₹{sgst :,.2f})"
            )
        else :
            igst =round (subtotal *GST_RATE ,2 )
            tax_info ["gst_type"]=f"Inter-State: 18% IGST (₹{igst :,.2f})"
    else :
        tax_info ["gst_type"]="18% GST (Missing GSTINs — state routing cannot be determined)"

    if subtotal >TDS_THRESHOLD :
        line_items =invoice .get ("line_items",[])
        is_service =any (
        any (kw in item .get ("description","").lower ()for kw in TDS_SERVICE_KEYWORDS )
        for item in line_items 
        )
        if is_service :
            tax_info ["tds_applicable"]=True 
            tax_info ["tds_section"]="Section 194J (10%)"
            tax_info ["tds_amount"]=round (subtotal *TDS_RATE ,2 )

    return tax_info 

def score_risks (invoice :dict ,tax :dict ,processed_invoice_numbers :set )->list :
    """
    Run 4 deterministic risk rules against an extracted invoice.

    Args:
        invoice:                   Output dict from extract_invoice().
        tax:                       Output dict from calculate_tax().
        processed_invoice_numbers: Set of invoice numbers already written
                                   to the ledger in this session. Used to
                                   detect duplicate submissions.

    Returns:
        List of risk dicts sorted by severity (CRITICAL first).
        Each dict contains: id, severity, desc
        Returns [] if no risks detected.
    """
    risks =[]

    inv_num =invoice .get ("invoice_number","")
    if inv_num and inv_num !="UNKNOWN"and inv_num in processed_invoice_numbers :
        risks .append ({
        "id":"DUPLICATE_INVOICE",
        "severity":"CRITICAL",
        "desc":f"Invoice {inv_num } has already been processed. "
        f"Potential double payment of ₹{invoice .get ('total_amount',0 ):,.2f}."
        })

    if invoice .get ("tax_amount",0 )==0 and tax ["estimated_gst"]>0 :
        risks .append ({
        "id":"TAX_MISSING",
        "severity":"HIGH",
        "desc":f"Invoice shows ₹0 tax. "
        f"Applicable GST: ₹{tax ['estimated_gst']:,.2f} ({tax ['gst_type']})."
        })

    v_gstin =invoice .get ("vendor_gstin")
    if v_gstin and len (str (v_gstin ))!=15 :
        risks .append ({
        "id":"INVALID_GSTIN",
        "severity":"MEDIUM",
        "desc":f"Vendor GSTIN '{v_gstin }' is invalid — must be exactly 15 characters."
        })

    if tax ["tds_applicable"]:
        risks .append ({
        "id":"TDS_REQUIRED",
        "severity":"MEDIUM",
        "desc":f"Deduct ₹{tax ['tds_amount']:,.2f} TDS under "
        f"{tax ['tds_section']} before releasing payment."
        })

    severity_order ={"CRITICAL":0 ,"HIGH":1 ,"MEDIUM":2 ,"LOW":3 }
    risks .sort (key =lambda x :severity_order .get (x ["severity"],99 ))

    return risks 