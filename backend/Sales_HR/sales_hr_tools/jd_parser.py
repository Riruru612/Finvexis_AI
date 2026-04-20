from langchain .tools import tool 
from langchain_groq import ChatGroq 
import os 
import json 
import re 
from dotenv import load_dotenv 

load_dotenv ()

llm =ChatGroq (
model ="llama-3.1-8b-instant",
groq_api_key =os .getenv ("GROQ_API")or os .getenv ("GROQ_API_KEY"),
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
    "required_skills":parsed .get ("required_skills",[]),
    "preferred_skills":parsed .get ("preferred_skills",[]),
    "tools_frameworks":parsed .get ("tools_frameworks",[]),
    "experience_level":parsed .get ("experience_level",""),
    "responsibilities":parsed .get ("responsibilities",[])
    }

@tool 
def parse_job_description (job_description :str ):
    """
    Extract structured requirements from job description.
    Returns clean structured dictionary.
    """

    try :
        prompt =f"""
You are an expert job description parser.

Extract structured information from the job description.

IMPORTANT:
- Return ONLY valid JSON
- No explanations
- No text outside JSON

Format:
{{
  "required_skills": [],
  "preferred_skills": [],
  "tools_frameworks": [],
  "experience_level": "",
  "responsibilities": []
}}

Rules:
- Required skills = must-have skills
- Preferred skills = nice-to-have skills
- tools_frameworks = technologies mentioned (TensorFlow, PyTorch, etc.)
- experience_level = years or level (fresher, junior, etc.)
Also ensure:
- include AI/ML terms like NLP, Deep Learning, Computer Vision
- normalize skill names (e.g., "TensorFlow" not "tensorflow framework")

Job Description:
{job_description }
"""

        response =llm .invoke (prompt )
        response =llm .invoke (prompt )

        print ("\n========== JD RAW OUTPUT ==========\n")
        print (response .content )
        print ("\n=================================\n")

        parsed =safe_json_parse (response .content )

        if not parsed :
            return {
            "required_skills":[],
            "preferred_skills":[],
            "tools_frameworks":[],
            "experience_level":"",
            "responsibilities":[]
            }

        return normalize_output (parsed )

    except Exception as e :
        return {
        "required_skills":[],
        "preferred_skills":[],
        "tools_frameworks":[],
        "experience_level":"",
        "responsibilities":[],
        "error":str (e )
        }