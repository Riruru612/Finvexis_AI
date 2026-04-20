"""
invoice_extractor.py
=====================
PDF extraction engine for the Invoice Agent.

Owns:
  - LineItem         : Pydantic model for a single line item
  - InvoiceData      : Pydantic model for the full extracted invoice
  - extract_invoice() : Reads PDF bytes, extracts text + tables, returns structured dict

No deterministic logic or LLM narrative here.
Output is consumed by invoice_tax_engine.py and invoiceAgent.py.
"""

import json 
import os 
import tempfile 
from typing import List ,Optional 

import pdfplumber 
from dotenv import load_dotenv 
from langchain_core .prompts import ChatPromptTemplate 
from langchain_groq import ChatGroq 
from pydantic import BaseModel ,Field ,model_validator 

load_dotenv ()
GROQ_API_KEY =os .getenv ("GROQ_API_KEY")

if not GROQ_API_KEY :
    raise ValueError ("GROQ_API_KEY not found. Please add it to your .env file.")

llm =ChatGroq (model ="llama-3.1-8b-instant",api_key =GROQ_API_KEY ,temperature =0 )

class LineItem (BaseModel ):
    description :str 
    quantity :float 
    unit_price :float 
    amount :float 

class InvoiceData (BaseModel ):
    invoice_number :str =Field (description ="Unique invoice ID. Return 'UNKNOWN' if missing.")
    vendor_name :str 
    vendor_gstin :Optional [str ]=Field (description ="15-character GSTIN of the vendor if present, else None")
    client_name :str 
    client_gstin :Optional [str ]=Field (description ="15-character GSTIN of the client if present, else None")
    date_issued :str 
    currency :str 
    subtotal :float 
    tax_amount :float 
    total_amount :float 
    line_items :List [LineItem ]
    confidence_score :float =Field (description ="Estimated extraction confidence (0.0 to 1.0)")

    @model_validator (mode ='after')
    def validate_math (self )->'InvoiceData':
        """
        Penalise confidence if subtotal + tax does not match total_amount.
        Tolerance: ₹0.50 to account for rounding.
        """
        calculated_total =self .subtotal +self .tax_amount 
        if abs (calculated_total -self .total_amount )>0.5 :
            self .confidence_score =max (0.0 ,self .confidence_score -0.2 )
        return self 

def extract_invoice (file_bytes :bytes )->dict :
    """
    Extract structured invoice data from PDF bytes.

    Writes bytes to a temp file, reads text and tables via pdfplumber,
    then uses LLM structured output to populate InvoiceData.
    Temp file is deleted after extraction regardless of success or failure.

    Args:
        file_bytes: Raw PDF bytes from the orchestrator or frontend upload.

    Returns:
        dict matching InvoiceData schema:
            invoice_number, vendor_name, vendor_gstin, client_name,
            client_gstin, date_issued, currency, subtotal, tax_amount,
            total_amount, line_items (list of dicts), confidence_score

    Raises:
        Exception: If pdfplumber cannot open the file or LLM extraction fails.
    """

    tmp_path =None 
    try :
        with tempfile .NamedTemporaryFile (delete =False ,suffix =".pdf")as tmp :
            tmp .write (file_bytes )
            tmp_path =tmp .name 

        raw_text =""
        table_data =""
        with pdfplumber .open (tmp_path )as pdf :
            for page in pdf .pages :
                raw_text +=(page .extract_text ()or "")+"\n"
                for table in page .extract_tables ():
                    table_data +=str (table )+"\n"

    finally :
        if tmp_path and os .path .exists (tmp_path ):
            os .unlink (tmp_path )

    structured_extractor =llm .with_structured_output (InvoiceData )

    prompt =ChatPromptTemplate .from_messages ([
    ("system",(
    "You are a precise Indian accounting AI. "
    "Extract invoice data into the required JSON structure. "
    "Return line_items as a proper JSON array, NOT a string. "
    "Look for 15-character GSTINs for both vendor and client."
    )),
    ("human","RAW TEXT:\n{text}\n\nTABLE DATA:\n{tables}")
    ])

    result =(prompt |structured_extractor ).invoke ({
    "text":raw_text ,
    "tables":table_data 
    })

    if isinstance (result ,dict ):

        if isinstance (result .get ("line_items"),str ):
            try :
                result ["line_items"]=json .loads (result ["line_items"])
            except Exception :
                result ["line_items"]=[]
        return result 

    return result .model_dump ()if hasattr (result ,"model_dump")else result .dict ()