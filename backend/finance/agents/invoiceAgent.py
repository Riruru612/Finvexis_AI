"""
invoiceAgent.py
================
Invoice Agent — Finvexis AI Finance Pipeline

Entry point for orchestrator:
    run_invoice_pipeline(file_bytes: bytes, filename: str) -> dict

Entry point for direct use:
    run_invoice_pipeline(file_bytes: bytes, filename: str) -> dict   (same function)

─────────────────────────────────────────────────────────────
ORCHESTRATOR INTEGRATION
─────────────────────────────────────────────────────────────
When the master orchestrator routes a file upload to this agent, it calls:

    from finance.agents.invoiceAgent import run_invoice_pipeline

    result = run_invoice_pipeline(
        file_bytes=request.file.read(),   # raw bytes from HTTP upload
        filename="invoice.pdf"            # original filename for logging
    )

No file path needed. No Streamlit session state. No temp file management.
The agent handles all of that internally.

Example orchestrator triggers for this agent:
    User uploads a PDF invoice → orchestrator routes to Invoice Agent
    "Process this invoice"     → orchestrator routes to Invoice Agent
    "Extract and analyse this invoice" → Invoice Agent
─────────────────────────────────────────────────────────────

Input:
    file_bytes : bytes — raw PDF bytes from the frontend/orchestrator
    filename   : str  — original filename (used for logging only)

Output:
    {
        "invoice":      dict,       # extracted invoice fields
        "tax":          dict,       # GST routing + TDS calculation
        "risks":        list[dict], # risk flags with severity
        "narrative":    str,        # LLM factual summary
        "ledger_write": dict        # result of writing to INVOICE_LEDGER
    }

Module responsibilities:
    agents/invoiceAgent.py          — run_invoice_pipeline(), generate_narrative(),
                                      session state (processed invoice numbers)
    engines/invoice_extractor.py    — PDF parsing + LLM structured extraction
    engines/invoice_tax_engine.py   — calculate_tax(), score_risks()
    engines/invoice_writer.py       — write_to_ledger()
"""

import os 
from typing import Optional 

from dotenv import load_dotenv 
from langchain_core .prompts import ChatPromptTemplate 
from langchain_groq import ChatGroq 

from engines .invoice_extractor import extract_invoice 
from engines .invoice_tax_engine import calculate_tax ,score_risks 
from engines .invoice_writer import write_to_ledger 

load_dotenv ()
GROQ_API_KEY =os .getenv ("GROQ_API_KEY")

if not GROQ_API_KEY :
    raise ValueError ("GROQ_API_KEY not found. Please add it to your .env file.")

llm =ChatGroq (model ="llama-3.1-8b-instant",api_key =GROQ_API_KEY ,temperature =0 )

_processed_invoice_numbers :set =set ()

def generate_narrative (invoice :dict ,tax :dict ,risks :list )->str :
    """
    Generate a factual invoice summary for the Finance Team.

    The LLM receives pre-computed extraction results, tax calculations,
    and risk flags. Its only job is to restate them as structured prose.

    Args:
        invoice: Output dict from extract_invoice().
        tax:     Output dict from calculate_tax().
        risks:   Output list from score_risks().

    Returns:
        Formatted narrative string.
    """
    risk_lines ="\n".join ([
    f"[{r ['severity']}] {r ['id']}: {r ['desc']}"
    for r in risks 
    ])or "No risks detected."

    prompt =ChatPromptTemplate .from_messages ([
    ("system","""You are a finance reporting assistant writing an invoice summary for the Finance Team.
Your role is strictly to restate the pre-computed data provided to you. Do NOT infer intent, motivations, or conclusions beyond what the data states.

Rules:
- Do NOT use words like "deliberate", "intentional", "suspicious", "likely", "probably", or any speculative language.
- Do NOT add recommendations. Risk flags are provided separately by the system.
- Do NOT calculate, estimate, or infer any number — use only what is in the data blocks.
- State only what the extraction and risk engine found.
- Never contradict or re-interpret a provided risk severity.

Structure your response as:
1. Invoice Overview (vendor, client, date, total — 1-2 sentences)
2. Tax Summary (restate GST type and TDS status exactly as provided)
3. Risk Flags (restate each flag exactly — do not soften or re-interpret severity)"""),
    ("human","""
EXTRACTED INVOICE:
- Invoice Number : {invoice_number}
- Vendor         : {vendor_name} (GSTIN: {vendor_gstin})
- Client         : {client_name} (GSTIN: {client_gstin})
- Date Issued    : {date_issued}
- Currency       : {currency}
- Subtotal       : ₹{subtotal:,.2f}
- Tax Applied    : ₹{tax_amount:,.2f}
- Total Amount   : ₹{total_amount:,.2f}
- Confidence     : {confidence_score:.0%}

TAX CALCULATION:
- Estimated GST  : ₹{estimated_gst:,.2f}
- GST Type       : {gst_type}
- TDS Applicable : {tds_applicable}
- TDS Amount     : ₹{tds_amount:,.2f}
- TDS Section    : {tds_section}

RISK FLAGS ({risk_count} detected):
{risk_lines}
""")
    ])

    response =(prompt |llm ).invoke ({
    "invoice_number":invoice .get ("invoice_number","UNKNOWN"),
    "vendor_name":invoice .get ("vendor_name","Unknown"),
    "vendor_gstin":invoice .get ("vendor_gstin")or "Not provided",
    "client_name":invoice .get ("client_name","Unknown"),
    "client_gstin":invoice .get ("client_gstin")or "Not provided",
    "date_issued":invoice .get ("date_issued","Unknown"),
    "currency":invoice .get ("currency","INR"),
    "subtotal":invoice .get ("subtotal",0.0 ),
    "tax_amount":invoice .get ("tax_amount",0.0 ),
    "total_amount":invoice .get ("total_amount",0.0 ),
    "confidence_score":invoice .get ("confidence_score",0.0 ),
    "estimated_gst":tax .get ("estimated_gst",0.0 ),
    "gst_type":tax .get ("gst_type","Unknown"),
    "tds_applicable":tax .get ("tds_applicable",False ),
    "tds_amount":tax .get ("tds_amount",0.0 ),
    "tds_section":tax .get ("tds_section")or "Not applicable",
    "risk_count":len (risks ),
    "risk_lines":risk_lines ,
    })

    return response .content 

def run_invoice_pipeline (file_bytes :bytes ,filename :str ="invoice.pdf")->dict :
    """
    Main entry point for the Invoice Agent.
    Called by the orchestrator or directly.

    Pipeline:
        1. extract_invoice()   — PDF parsing + LLM structured extraction
        2. calculate_tax()     — deterministic GST routing + TDS check
        3. score_risks()       — 4 deterministic risk rules
        4. write_to_ledger()   — append to INVOICE_LEDGER in dummy_data
        5. generate_narrative() — LLM restates findings as prose

    Args:
        file_bytes: Raw PDF bytes. Orchestrator passes these directly
                    from the HTTP upload — no temp file management needed
                    on the orchestrator side.
        filename:   Original filename for logging. Does not affect processing.

    Returns:
        dict with keys:
            invoice      — extracted invoice fields
            tax          — GST routing + TDS calculation
            risks        — list of risk flags with severity
            narrative    — LLM factual summary
            ledger_write — result of writing to INVOICE_LEDGER
                           {written: bool, record: dict} or {written: False, reason: str}
    """
    print (f"[invoiceAgent] Processing: {filename }")

    invoice_data =extract_invoice (file_bytes )

    tax_data =calculate_tax (invoice_data )

    risk_data =score_risks (invoice_data ,tax_data ,_processed_invoice_numbers )

    ledger_result =write_to_ledger (invoice_data ,tax_data )

    inv_num =invoice_data .get ("invoice_number","UNKNOWN")
    if ledger_result ["written"]and inv_num !="UNKNOWN":
        _processed_invoice_numbers .add (inv_num )

    narrative =generate_narrative (invoice_data ,tax_data ,risk_data )

    return {
    "invoice":invoice_data ,
    "tax":tax_data ,
    "risks":risk_data ,
    "narrative":narrative ,
    "ledger_write":ledger_result ,
    }

if __name__ =="__main__":
    import sys 

    if len (sys .argv )<2 :
        print ("Usage: python invoiceAgent.py <path_to_invoice.pdf>")
        print ("Example: python invoiceAgent.py ../indian_invoice.pdf")
        sys .exit (1 )

    pdf_path =sys .argv [1 ]

    print (f"\n{'='*60 }")
    print (f"INVOICE AGENT — CLI TEST")
    print (f"File: {pdf_path }")
    print ("="*60 )

    with open (pdf_path ,"rb")as f :
        raw_bytes =f .read ()

    result =run_invoice_pipeline (
    file_bytes =raw_bytes ,
    filename =pdf_path 
    )

    inv =result ["invoice"]
    print (f"\nExtracted Invoice  : {inv .get ('invoice_number')}")
    print (f"Vendor             : {inv .get ('vendor_name')} ({inv .get ('vendor_gstin')or 'No GSTIN'})")
    print (f"Total Amount       : ₹{inv .get ('total_amount',0 ):,.2f}")
    print (f"Confidence         : {inv .get ('confidence_score',0 ):.0%}")

    print (f"\nGST Type           : {result ['tax']['gst_type']}")
    print (f"TDS Applicable     : {result ['tax']['tds_applicable']}")
    if result ["tax"]["tds_applicable"]:
        print (f"TDS Amount         : ₹{result ['tax']['tds_amount']:,.2f}")

    print (f"\nRisks ({len (result ['risks'])}):")
    for r in result ["risks"]:
        print (f"  [{r ['severity']}] {r ['id']} — {r ['desc']}")

    print (f"\nLedger Write       : {' Written'if result ['ledger_write']['written']else ' Skipped — '+result ['ledger_write'].get ('reason','')}")

    print (f"\nNARRATIVE:\n{result ['narrative']}")