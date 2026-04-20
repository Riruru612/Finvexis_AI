from langchain .tools import tool 
import re 
from langchain_groq import ChatGroq 
from langchain_core .prompts import ChatPromptTemplate 
import os 
from dotenv import load_dotenv 
from utils .helpers import validate_email 

from sales_hr_tools .crm_tool import add_customer ,update_customer ,add_interaction 

load_dotenv ()

llm =ChatGroq (
model ="llama-3.1-8b-instant",
groq_api_key =os .getenv ("GROQ_API")
)

def compute_lead_score (budget ,company_size ,interest ):
    score =0 

    if budget >100000 :
        score +=30 
    elif budget >50000 :
        score +=20 
    else :
        score +=10 

    if company_size >500 :
        score +=30 
    elif company_size >100 :
        score +=20 
    else :
        score +=10 

    interest =interest .lower ()

    if "high"in interest :
        score +=30 
    elif "medium"in interest :
        score +=20 
    else :
        score +=10 

    return score 

prompt =ChatPromptTemplate .from_template (
"""
Explain why this lead got a score of {score}/100.

Return:
- Priority
- Key reasons (2–3 bullets only)
"""
)

@tool 
def lead_scoring_tool (
name :str ,
company :str ,
email :str ,
budget :str ,
company_size :str ,
interest :str 
):
    """
    Evaluate and score a lead, store in CRM, and log interactions.
    """

    try :

        email =validate_email (email )

        budget =int (float (str (budget ).replace (",","").strip ()))
        company_size =int (float (str (company_size ).replace (",","").strip ()))

        score =compute_lead_score (budget ,company_size ,interest )

        if score >70 :
            stage ="high_priority"
        elif score >50 :
            stage ="qualified"
        else :
            stage ="nurture"

        add_customer .invoke ({
        "name":name ,
        "email":email ,
        "company":company 
        })

        update_customer .invoke ({
        "email":email ,
        "field":"lead_score",
        "value":int (score )
        })

        update_customer .invoke ({
        "email":email ,
        "field":"deal_stage",
        "value":stage 
        })

        add_interaction .invoke ({
        "email":email ,
        "note":f"Lead created for {company }",
        "interaction_type":"creation"
        })

        add_interaction .invoke ({
        "email":email ,
        "note":f"Lead scored {score }/100",
        "interaction_type":"scoring"
        })

        if score >80 :
            next_action ="Schedule demo"
        elif score >60 :
            next_action ="Follow up"
        else :
            next_action ="Nurture lead"

        add_interaction .invoke ({
        "email":email ,
        "note":f"Next action: {next_action }",
        "interaction_type":"recommendation"
        })

        chain =prompt |llm 

        explanation =chain .invoke ({
        "score":score 
        })

        return f"""
Lead Evaluation Result:

Name: {name }
Company: {company }
Email: {email }

Lead Score: {score } ({stage .replace ('_',' ').title ()})

{explanation .content }

Recommended Action: {next_action }
"""

    except Exception as e :
        return f"Error in lead scoring: {str (e )}"