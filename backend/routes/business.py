from fastapi import APIRouter ,UploadFile ,File ,Form ,HTTPException 
import pandas as pd 
import io 
import sys 
import os 
import json 
from typing import Optional ,List ,Dict ,Any 
from pydantic import BaseModel 

from Business .src_ai .graph .orchestrator import FinvexisOrchestrator 
from langchain_groq import ChatGroq 
from langchain_core .messages import HumanMessage ,SystemMessage 

router =APIRouter (prefix ="/business",tags =["business"])

class ChatRequest (BaseModel ):
    prompt :str 
    analysis_results :Optional [Dict [str ,Any ]]=None 
    context_summary :Optional [str ]=None 

def get_chatbot_response (prompt :str ,context_summary :Optional [str ]=None ,analysis_results :Optional [Dict [str ,Any ]]=None ):
    raw_api_key =os .getenv ("GROQ_API_KEY")
    if not raw_api_key :
        raise HTTPException (status_code =500 ,detail ="GROQ_API_KEY is missing")

    api_key =raw_api_key .strip ()
    try :

        llm =ChatGroq (model ="llama-3.3-70b-versatile",groq_api_key =api_key ,temperature =0 )

        system_msg ="""You are Finvexis AI, a world-class Decision Intelligence Consultant. 
        Your goal is to help a CEO/Founder make better decisions using data.
        
        STRICT REQUIREMENT: 
        - Always respond in professional, clear, and concise English.
        - Do not use Hindi, Hinglish, or any other language.
        - **IMPORTANT: Keep your answers PRECISE, SHORT, and SIMPLE.** Avoid long paragraphs. Focus on the most impactful facts.
        """

        context =""
        if analysis_results :

            readable_analysis =json .dumps (analysis_results ,separators =(',',':'))
            context +=f"\n\n--- AGENT ANALYSIS (DEEP CONTEXT) ---\n{readable_analysis }"

        if context_summary :
            context +=f"\n\n--- RAW DATA SUMMARY ---\n{context_summary }"

        messages =[
        SystemMessage (content =system_msg +"\n\nCONTEXT:\n"+context ),
        HumanMessage (content =prompt )
        ]

        response =llm .invoke (messages )
        return response .content 
    except Exception as e :
        raise HTTPException (status_code =500 ,detail =str (e ))

@router .post ("/analyze")
async def analyze_business (
file :UploadFile =File (...),
use_llm :bool =Form (True )
):
    try :
        contents =await file .read ()
        df =pd .read_csv (io .BytesIO (contents ))

        orchestrator =FinvexisOrchestrator (use_llm =use_llm ,llm_provider ="groq")

        m_context ={
        "competitors":[{"name":"A","price":200 ,"features":["F1"]},{"name":"B","price":180 ,"features":["F1","F2"]}],
        "our_features":["F1"],
        "industry_trend":"growing",
        "sentiment_score":75 
        }

        res =orchestrator .run_full_analysis (df ,m_context )
        return {
        "analysis_results":res ,
        "data_summary":df .describe ().to_string ()
        }
    except Exception as e :
        raise HTTPException (status_code =500 ,detail =str (e ))

@router .post ("/chat")
async def business_chat (request :ChatRequest ):
    response =get_chatbot_response (
    prompt =request .prompt ,
    context_summary =request .context_summary ,
    analysis_results =request .analysis_results 
    )
    return {"response":response }
