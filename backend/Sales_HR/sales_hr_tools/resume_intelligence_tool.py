from langchain .tools import tool 
from langchain_groq import ChatGroq 
from langchain_core .prompts import ChatPromptTemplate 
import os 
import re 

from streamlit import text 

from sales_hr_tools .resume_parser import parse_resume 
from sales_hr_tools .jd_parser import parse_job_description 

llm =ChatGroq (
model ="llama-3.3-70b-versatile",
groq_api_key =os .getenv ("GROQ_API_KEY")
)

def parse_llm_output (text ):
    try :

        score_match =re .search (r"Score:\s*(\d+)",text )
        score =int (score_match .group (1 ))if score_match else 50 

        matched_match =re .search (r"Matched Required Skills:\s*(.*?)(?:\n|$)",text ,re .IGNORECASE )
        matched_str =matched_match .group (1 ).strip ()if matched_match else ""

        if matched_str .startswith ("[")and matched_str .endswith ("]"):
            try :

                matched_items =re .findall (r"['\"]([^'\"]+)['\"]",matched_str )
                if not matched_items :
                    matched_items =[s .strip ()for s in matched_str [1 :-1 ].split (",")if s .strip ()]
            except :
                matched_items =[s .strip ()for s in matched_str [1 :-1 ].split (",")if s .strip ()]
        else :
            matched_items =[s .strip ()for s in matched_str .split (",")if s .strip ()]

        missing_match =re .search (r"Missing Required Skills:\s*(.*?)(?:\n|$)",text ,re .IGNORECASE )
        missing_str =missing_match .group (1 ).strip ()if missing_match else ""

        if missing_str .startswith ("[")and missing_str .endswith ("]"):
            try :
                missing_items =re .findall (r"['\"]([^'\"]+)['\"]",missing_str )
                if not missing_items :
                    missing_items =[s .strip ()for s in missing_str [1 :-1 ].split (",")if s .strip ()]
            except :
                missing_items =[s .strip ()for s in missing_str [1 :-1 ].split (",")if s .strip ()]
        else :
            missing_items =[s .strip ()for s in missing_str .split (",")if s .strip ()]

        return {
        "score":score ,
        "matched_required":[m .strip ("[]'\" ")for m in matched_items if m .strip ("[]'\" ")],
        "missing_required":[m .strip ("[]'\" ")for m in missing_items if m .strip ("[]'\" ")],
        "raw":text 
        }

    except Exception as e :
        print (f"Error parsing LLM output: {e }")
        return {
        "score":50 ,
        "matched_required":[],
        "missing_required":[],
        "raw":text 
        }

@tool 
def resume_intelligence_tool (resume_text :str ,job_description :str ):
    """
    Hybrid Resume Intelligence:
    - LLM for understanding
    - Controlled scoring for stability
    """

    try :

        resume_data =parse_resume .invoke ({"resume_text":resume_text })
        jd_data =parse_job_description .invoke ({"job_description":job_description })

        resume_skills =resume_data .get ("skills",[])
        projects =resume_data .get ("projects",[])
        experience =resume_data .get ("experience_summary","")

        jd_required =jd_data .get ("required_skills",[])
        jd_preferred =jd_data .get ("preferred_skills",[])

        if not resume_skills or not jd_required :
            return "Parsing failed. Please check input."

        prompt =ChatPromptTemplate .from_template ("""
You are an expert technical recruiter.

Your task is to evaluate how well a candidate’s resume matches a job description.

-----------------------------------
INPUT
-----------------------------------

Resume Skills:
{resume_skills}

Projects:
{projects}

Experience:
{experience}

Job Required Skills:
{jd_required}

Preferred Skills:
{jd_preferred}

-----------------------------------
EVALUATION RULES (VERY IMPORTANT)
-----------------------------------

1. Use semantic understanding, NOT exact keyword matching.

2. Treat tools, frameworks, and technologies as evidence of broader skills.

3. If a skill is supported indirectly (via tools, projects, or experience),
   it MUST be included in "Matched Required Skills".

4. If you mention any indirect evidence in the reasoning,
   that skill MUST NOT appear in "Missing Required Skills".

5. Only include a skill in "Missing Required Skills" if there is ZERO evidence.

6. STRICT CONSISTENCY:
   - No contradictions allowed
   - If reasoning supports a skill → it is MATCHED

7. Only mark a skill as "missing" if there is NO evidence at all.

. Avoid contradictions:
   - If reasoning says the candidate has a skill → it MUST be in matched
   - Do NOT say something is missing and then justify it as present

-----------------------------------
OUTPUT FORMAT (STRICT)
-----------------------------------

Score: <0-100>

Matched Required Skills: skill1, skill2
Missing Required Skills: skill3, skill4

Strengths:
- Brief explanation of strengths

Gaps:
- Brief explanation of gaps

Decision: Shortlist / Consider / Reject

-----------------------------------
IMPORTANT: 
- Do NOT use brackets [] or quotes "" for skills.
- Do NOT use symbols like ** for labels.
- Provide a clean, text-only response.
-----------------------------------
""")

        chain =prompt |llm 

        llm_response =chain .invoke ({
        "resume_skills":resume_skills ,
        "projects":projects ,
        "experience":experience ,
        "jd_required":jd_required ,
        "jd_preferred":jd_preferred 
        })

        parsed =parse_llm_output (llm_response .content )

        llm_score =parsed ["score"]
        matched_required =parsed ["matched_required"]
        missing_required =parsed ["missing_required"]

        required_total =len (jd_required )
        preferred_total =len (jd_preferred )

        required_score =(len (matched_required )/required_total )*70 if required_total else 0 

        matched_preferred =[
        s for s in jd_preferred if s .lower ()in [r .lower ()for r in resume_skills ]
        ]
        preferred_score =(len (matched_preferred )/preferred_total )*20 if preferred_total else 0 

        project_score =min (len (projects )*2 ,10 )
        experience_score =5 if experience else 0 

        rule_score =required_score +preferred_score +project_score +experience_score 

        final_score =(0.6 *rule_score )+(0.4 *llm_score )

        if missing_required :
            final_score =min (final_score ,90 )

        final_score =round (min (final_score ,100 ),2 )

        if final_score >75 :
            decision ="Shortlist"
        elif final_score >50 :
            decision ="Consider"
        else :
            decision ="Reject"

        strengths_match =re .search (r"Strengths:\s*(.*?)(?=\s*Gaps:|\s*Decision:|$)",llm_response .content ,re .DOTALL |re .IGNORECASE )
        gaps_match =re .search (r"Gaps:\s*(.*?)(?=\s*Decision:|$)",llm_response .content ,re .DOTALL |re .IGNORECASE )

        strengths_text =strengths_match .group (1 ).strip ()if strengths_match else "No specific strengths identified."
        gaps_text =gaps_match .group (1 ).strip ()if gaps_match else "No major gaps identified."

        return f"""
Resume Evaluation:

Score: {final_score }/100
Decision: {decision }

Matched Required Skills:
{', '.join (matched_required )if matched_required else 'None'}

Missing Required Skills:
{', '.join (missing_required )if missing_required else 'None'}

Strengths:
{strengths_text }

Gaps:
{gaps_text }
"""

    except Exception as e :
        return f"Error evaluating resume: {str (e )}"
