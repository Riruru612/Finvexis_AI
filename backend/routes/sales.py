from fastapi import APIRouter ,UploadFile ,File ,Form ,HTTPException 
import sys 
import os 
import io 
from typing import Optional ,Any 
from pypdf import PdfReader 
from pydantic import BaseModel 

from Sales_HR .agent import create_sales_hr_agent 
from Sales_HR .utils .pdf_rag import create_vector_db 
from Sales_HR .sales_hr_tools .hr_policy_tool import set_hr_retriever ,hr_policy_tool 
from Sales_HR .sales_hr_tools .sales_advisor_tool import sales_advisor_tool 
from Sales_HR .sales_hr_tools .sales_insights_tool import sales_insights_tool 
from Sales_HR .sales_hr_tools .resume_intelligence_tool import resume_intelligence_tool 
from Sales_HR .utils .doc_classifier import classify_document 
from Sales_HR .db .db import init_db 
from langchain_groq import ChatGroq 
from langchain_core .prompts import ChatPromptTemplate 

init_db ()

sales_hr_agent =create_sales_hr_agent ()

router =APIRouter (prefix ="/sales",tags =["sales"])

router_llm =ChatGroq (
model ="llama-3.1-8b-instant",
groq_api_key =os .getenv ("GROQ_API"),
temperature =0 
)

router_prompt =ChatPromptTemplate .from_template ("""
You are an intent classifier for a business AI system.
Your job is to classify the user's query into EXACTLY ONE of the following labels:
resume, hr, sales_advisor, sales_insights, crm
Return ONLY ONE word. Do NOT explain.
USER QUERY: {query}
""")

def classify_intent (query :str ):
    try :
        chain =router_prompt |router_llm 
        result =chain .invoke ({"query":query })
        return result .content .strip ().lower ()
    except :
        return "crm"

@router .post ("/process")
async def process_sales_hr (
query :str =Form (...),
file :Optional [UploadFile ]=File (None )
):
    try :
        q_lower =query .lower ()

        if file :
            file_bytes =await file .read ()
            reader =PdfReader (io .BytesIO (file_bytes ))
            text =""
            for page in reader .pages :
                content =page .extract_text ()
                if content :
                    text +=content 

            doc_type =classify_document (text )

            if doc_type =="resume"or "resume"in file .filename .lower ():
                response =resume_intelligence_tool .invoke ({
                "resume_text":text ,
                "job_description":query 
                })
                return {"type":"resume_evaluation","response":response }

            else :

                file_stream =io .BytesIO (file_bytes )
                db =create_vector_db (file_stream )
                retriever =db .as_retriever (search_kwargs ={"k":3 })
                set_hr_retriever (retriever )

                response =hr_policy_tool .invoke ({
                "question":query ,
                "filename":file .filename 
                })

                return {
                "type":"hr_policy_response",
                "response":response 
                }

        if any (k in q_lower for k in ["add customer","create customer","new customer","update customer","delete customer","log interaction","show interactions","get customer","customer details"]):
            response =sales_hr_agent .invoke ({"messages":[{"role":"user","content":query }]})
            answer =response ["messages"][-1 ].content if isinstance (response ,dict )else str (response )
            return {"type":"crm_response","response":answer }

        elif any (k in q_lower for k in ["why","how","performance","analysis","insights","pipeline","conversion"]):
            response =sales_insights_tool .invoke ({"query":query })
            return {"type":"sales_insights","response":response }

        elif any (k in q_lower for k in ["write","draft","generate","email","pitch","follow up","reply"]):
            response =sales_advisor_tool .invoke ({"query":query })
            return {"type":"sales_advisor","response":response }

        intent =classify_intent (query )
        if intent =="sales_insights":
            response =sales_insights_tool .invoke ({"query":query })
            return {"type":"sales_insights","response":response }
        elif intent =="sales_advisor":
            response =sales_advisor_tool .invoke ({"query":query })
            return {"type":"sales_advisor","response":response }
        else :
            response =sales_hr_agent .invoke ({"messages":[{"role":"user","content":query }]})
            answer =response ["messages"][-1 ].content if isinstance (response ,dict )else str (response )
            return {"type":"agent_response","response":answer }

    except Exception as e :
        raise HTTPException (status_code =500 ,detail =str (e ))
