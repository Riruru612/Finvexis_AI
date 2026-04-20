from langchain .tools import tool 
from langchain_groq import ChatGroq 
import os 
import json 
import re 
from dotenv import load_dotenv 

load_dotenv ()

llm =ChatGroq (
model ="llama-3.3-70b-versatile",
groq_api_key =os .getenv ("GROQ_API_KEY"),
temperature =0 
)

def safe_json_parse (text ):
    try :

        match =re .search (r"\{.*\}",text ,re .DOTALL )
        if match :
            json_str =match .group ()
            return json .loads (json_str )
    except Exception :
        pass 
    return {}

def normalize_output (parsed ):
    return {
    "skills":parsed .get ("skills",[]),
    "projects":parsed .get ("projects",[]),
    "experience_summary":parsed .get ("experience_summary",""),
    "education":parsed .get ("education",""),
    "achievements":parsed .get ("achievements",[])
    }

@tool 
def parse_resume (resume_text :str ):
    """
    Extract structured information from resume using LLM.
    Returns clean JSON-like dictionary.
    """

    try :
        prompt =f"""
You are an expert resume parser.

Extract structured information from the resume.
Also ensure:
- skills include programming languages, tools, frameworks
- projects include project titles or descriptions

IMPORTANT:
- Return ONLY valid JSON
- Do NOT add explanations
- Do NOT add text before/after JSON

Format:
{{
  "skills": [],
  "projects": [],
  "experience_summary": "",
  "education": "",
  "achievements": []
}}

Resume:
{resume_text }
"""

        response =llm .invoke (prompt )
        print ("\n========== RESUME RAW OUTPUT ==========\n")
        print (response .content )
        print ("\n=====================================\n")

        parsed =safe_json_parse (response .content )

        if not parsed :
            return {
            "skills":[],
            "projects":[],
            "experience_summary":"",
            "education":"",
            "achievements":[]
            }

        return normalize_output (parsed )

    except Exception as e :
        return {
        "skills":[],
        "projects":[],
        "experience_summary":"",
        "education":"",
        "achievements":[],
        "error":str (e )
        }