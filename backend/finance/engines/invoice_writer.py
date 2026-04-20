"""
invoice_writer.py
==================
Ledger writer for the Invoice Agent.

Owns:
  - write_to_ledger() : Appends a processed invoice to INVOICE_LEDGER in dummy_data.py

Current implementation writes to the in-memory INVOICE_LEDGER list.
Since dummy_data is a module-level list, entries persist for the lifetime
of the running process (i.e. the full demo session).

─────────────────────────────────────────────────────────────
UPGRADING TO A REAL DATABASE
─────────────────────────────────────────────────────────────
When the backend team is ready to connect a real database (SQLite, PostgreSQL, etc.),
only this file needs to change. Replace the body of write_to_ledger() with the
appropriate DB insert. The function signature stays the same so invoiceAgent.py
requires zero changes.

Example upgrade path:
    import sqlite3
    def write_to_ledger(invoice: dict, tax: dict) -> dict:
        conn = sqlite3.connect("finvexis.db")
        conn.execute("INSERT INTO invoices (...) VALUES (...)", {...})
        conn.commit()
        ...
─────────────────────────────────────────────────────────────
"""

from datetime import date ,datetime 
import dummy_data 

def write_to_ledger (invoice :dict ,tax :dict )->dict :
    """
    Append a processed invoice to the in-memory INVOICE_LEDGER.

    Skips writing if invoice_number is "UNKNOWN" to avoid polluting
    the ledger with unidentifiable entries.

    Builds a ledger-compatible record matching the schema used in
    dummy_data.INVOICE_LEDGER so all four agents can read it consistently.

    Args:
        invoice: Output dict from extract_invoice().
        tax:     Output dict from calculate_tax().

    Returns:
        dict with keys:
            written   : bool   — True if written, False if skipped
            reason    : str    — why it was skipped (only present if written=False)
            record    : dict   — the ledger record that was appended (if written=True)
    """
    inv_num =invoice .get ("invoice_number","UNKNOWN")

    if inv_num =="UNKNOWN":
        return {
        "written":False ,
        "reason":"Invoice number is UNKNOWN — skipped to avoid ledger pollution."
        }

    date_issued =invoice .get ("date_issued","")
    parsed_date =_parse_date (date_issued )

    line_items =[]
    for item in invoice .get ("line_items",[]):

        if hasattr (item ,"model_dump"):
            item =item .model_dump ()
        line_items .append ({
        "description":item .get ("description",""),
        "quantity":item .get ("quantity",1 ),
        "unit_price":item .get ("unit_price",0.0 ),
        "amount":item .get ("amount",0.0 ),
        })

    record ={
    "invoice_number":inv_num ,
    "vendor_id":"EXTRACTED",
    "vendor_name":invoice .get ("vendor_name","Unknown"),
    "vendor_gstin":invoice .get ("vendor_gstin"),
    "client_gstin":invoice .get ("client_gstin"),
    "date_issued":parsed_date ,
    "department":"UNASSIGNED",
    "currency":invoice .get ("currency","INR"),
    "line_items":line_items ,
    "subtotal":invoice .get ("subtotal",0.0 ),
    "tax_amount":invoice .get ("tax_amount",0.0 ),
    "total_amount":invoice .get ("total_amount",0.0 ),
    "status":"PENDING",
    "notes":f"Extracted via Invoice Agent. GST type: {tax .get ('gst_type','Unknown')}.",
    "source":"INVOICE_AGENT",
    }

    dummy_data .INVOICE_LEDGER .append (record )

    return {
    "written":True ,
    "record":record 
    }

def _parse_date (date_str :str )->date :
    """
    Parse a date string returned by the LLM into a datetime.date object.
    Tries common formats. Falls back to today's date if parsing fails.

    Args:
        date_str: Date string e.g. "2026-04-07", "April 7, 2026", "07/04/2026"

    Returns:
        datetime.date object
    """
    formats =[
    "%Y-%m-%d",
    "%d-%m-%Y",
    "%d/%m/%Y",
    "%B %d, %Y",
    "%b %d, %Y",
    "%d %B %Y",
    "%d %b %Y",
    ]
    for fmt in formats :
        try :
            return datetime .strptime (date_str .strip (),fmt ).date ()
        except (ValueError ,AttributeError ):
            continue 

    print (f"[invoice_writer] Warning: could not parse date '{date_str }' — defaulting to today.")
    return date .today ()