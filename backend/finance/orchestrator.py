import os 
from typing import Optional 

from dotenv import load_dotenv 
from langchain_core .prompts import ChatPromptTemplate 
from langchain_groq import ChatGroq 
from pydantic import BaseModel ,Field 

from agents .invoiceAgent import run_invoice_pipeline 
from agents .auditorAgent import run_auditor 
from agents .vendorIntelligenceAgent import run_vendor_intelligence 
from agents .fpaAgent import run_fpa 

load_dotenv ()
GROQ_API_KEY =os .getenv ("GROQ_API_KEY")

if not GROQ_API_KEY :
    raise ValueError ("GROQ_API_KEY not found. Please add it to your .env file.")

llm =ChatGroq (model ="llama-3.1-8b-instant",api_key =GROQ_API_KEY ,temperature =0 )

AGENT_PRIORITY =["invoice_agent","auditor_agent","vendor_agent","fpa_agent"]

class RoutingDecision (BaseModel ):
    agents :list [str ]=Field (
    description =(
    "List of agents to call. Choose from: "
    "'invoice_agent' — process a PDF invoice, extract data, calculate GST/TDS; "
    "'auditor_agent' — audit the ledger for a time period, detect anomalies; "
    "'vendor_agent'  — analyse vendor risk, behavioral patterns, rankings; "
    "'fpa_agent'     — budget vs actual, burn rate, forecast, what-if analysis. "
    "Return multiple agents if the query spans more than one domain. "
    "Return an empty list if the query has no clear finance task."
    )
    )
    reasoning :str =Field (
    description ="One sentence explaining which agents were selected and why."
    )

def route_query (query :str ,has_file :bool )->RoutingDecision :
    """
    Use LLM to decide which agents to invoke for a given query.

    Args:
        query:    Natural language query from the user.
        has_file: True if the user uploaded a PDF file.

    Returns:
        RoutingDecision with agents list and reasoning string.
    """
    file_context =(
    "The user has uploaded a PDF file — invoice_agent should be included "
    "if the query involves processing or analysing the uploaded document."
    if has_file else 
    "No file was uploaded."
    )

    prompt =ChatPromptTemplate .from_messages ([
    ("system",f"""You are a finance query router for a multi-agent AI system.
Your job is to read the user's query and decide which finance agents to call.

Available agents and their domains:
- invoice_agent  : Processing PDF invoices, GST/TDS calculation, invoice risk flags
- auditor_agent  : Ledger audits, anomaly detection, period reports (Q1, March, etc.)
- vendor_agent   : Vendor risk profiles, behavioral patterns, vendor rankings
- fpa_agent      : Budget vs actual, department burn rates, forecasts, what-if simulations

File context: {file_context }

Rules:
- Select ALL agents whose domain is relevant to the query
- If query spans multiple domains, return multiple agents
- For broad queries (e.g., "full financial overview"), return auditor_agent, vendor_agent, and fpa_agent
- NEVER return invoice_agent unless a file is explicitly uploaded (file context says "The user has uploaded a PDF file")
- If no finance task is identifiable, return an empty list
"""),
    ("human","{query}")
    ])

    structured_llm =llm .with_structured_output (RoutingDecision )
    return (prompt |structured_llm ).invoke ({"query":query })

def dispatch_agents (
agents :list [str ],
query :str ,
file_bytes :Optional [bytes ],
filename :str 
)->dict :
    """
    Call each selected agent in AGENT_PRIORITY order.
    Collects results and errors per agent.

    Args:
        agents:     List of agent names from RoutingDecision.
        query:      Original user query — passed to all non-invoice agents.
        file_bytes: PDF bytes — only used by invoice_agent.
        filename:   Original filename for logging.

    Returns:
        dict keyed by agent name. Each value is either the agent's output dict
        or {"error": str} if the agent raised an exception.
    """

    ordered =[a for a in AGENT_PRIORITY if a in agents ]

    results ={}
    for agent in ordered :
        try :
            if agent =="invoice_agent":
                if file_bytes :
                    results [agent ]=run_invoice_pipeline (
                    file_bytes =file_bytes ,
                    filename =filename 
                    )
                else :
                    results [agent ]={
                    "error":"invoice_agent was selected but no PDF file was provided."
                    }

            elif agent =="auditor_agent":
                results [agent ]=run_auditor (query =query )

            elif agent =="vendor_agent":
                results [agent ]=run_vendor_intelligence (query =query )

            elif agent =="fpa_agent":
                results [agent ]=run_fpa (query =query )

        except Exception as e :
            results [agent ]={"error":f"{agent } failed: {str (e )}"}

    return results 

def synthesise_narrative (
query :str ,
agent_results :dict ,
routing_reasoning :str 
)->str :
    """
    Combine all agent narratives into a single unified response.

    Each agent's narrative is already factual and pre-computed.
    The synthesis LLM only organises and connects them — no new reasoning.

    Args:
        query:             Original user query.
        agent_results:     Output dict from dispatch_agents().
        routing_reasoning: One-sentence explanation from the router.

    Returns:
        Unified narrative string.
    """

    narrative_blocks =[]
    for agent ,result in agent_results .items ():
        if "error"in result :
            narrative_blocks .append (
            f"[{agent .upper ()}]\nError: {result ['error']}"
            )
        else :
            narrative =result .get ("narrative","No narrative generated.")
            narrative_blocks .append (f"[{agent .upper ()}]\n{narrative }")

    combined ="\n\n".join (narrative_blocks )
    agent_count =len (agent_results )

    prompt =ChatPromptTemplate .from_messages ([
    ("system","""You are a finance reporting assistant combining multiple agent reports into one unified response.

Rules:
- Do NOT add any new analysis, calculations, or conclusions not present in the agent reports.
- Do NOT use speculative language like "likely", "probably", "may indicate".
- Do NOT contradict any severity rating or verdict from the agent reports.
- Preserve all specific rupee amounts, percentages, and risk flags exactly as stated.
- Connect the reports naturally — use section headers for each agent's findings.
- If only one agent was called, present its report cleanly without unnecessary framing.
- End with a brief one-line status summary of the overall financial position.
- Do NOT invent, assume, or hallucinate time periods, dates, or quarters (e.g., "Q4") based on the user's conversational query. Use ONLY the scope explicitly provided in the AGENT REPORTS.
"""),
    ("human","""User Query: {query}

Agents invoked: {agent_count} ({agent_names})
Router reasoning: {reasoning}

AGENT REPORTS:
{combined}
""")
    ])

    response =(prompt |llm ).invoke ({
    "query":query ,
    "agent_count":agent_count ,
    "agent_names":", ".join (agent_results .keys ()),
    "reasoning":routing_reasoning ,
    "combined":combined ,
    })

    return response .content 

def run_orchestrator (
query :str ,
file_bytes :Optional [bytes ]=None ,
filename :str ="uploaded_file.pdf"
)->dict :
    """
    Main entry point for the Finvexis AI Finance Orchestrator.
    Called by the Streamlit interface or any external caller.

    Pipeline:
        1. route_query()        — LLM decides which agents to call
        2. dispatch_agents()    — calls agents in priority order
        3. synthesise_narrative() — LLM unifies all outputs

    Args:
        query:      Natural language query from the user.
        file_bytes: Raw PDF bytes if user uploaded a file, else None.
        filename:   Original filename for logging (default: "uploaded_file.pdf").

    Returns:
        dict with keys:
            query          — original query
            agents_called  — list of agent names that were invoked
            results        — per-agent raw output dicts
            narrative      — unified synthesis narrative
            has_file       — whether a PDF was processed
            error          — None if successful, error string if routing failed
    """
    has_file =file_bytes is not None 

    try :
        routing =route_query (query ,has_file )
    except Exception as e :
        return {
        "query":query ,
        "agents_called":[],
        "results":{},
        "narrative":"Routing failed — could not determine which agents to call.",
        "has_file":has_file ,
        "error":str (e )
        }

    if not routing .agents :
        return {
        "query":query ,
        "agents_called":[],
        "results":{},
        "narrative":(
        "I couldn't identify a finance task in your query. "
        "Try asking about invoices, budgets, vendors, or audits. "
        "You can also upload a PDF invoice for processing."
        ),
        "has_file":has_file ,
        "error":None 
        }

    agent_results =dispatch_agents (
    agents =routing .agents ,
    query =query ,
    file_bytes =file_bytes ,
    filename =filename 
    )

    narrative =synthesise_narrative (query ,agent_results ,routing .reasoning )

    return {
    "query":query ,
    "agents_called":list (agent_results .keys ()),
    "results":agent_results ,
    "narrative":narrative ,
    "has_file":has_file ,
    "error":None 
    }

if __name__ =="__main__":
    import sys 
    import time 
    print ("Finvexis AI — Orchestrator CLI Test")
    print ("="*60 )

    test_queries =[
    ("Audit Q1 2026 and tell me about Cloud Data Dynamics risk",None ),
    ("Which department is over budget and which vendor is riskiest?",None ),
    ("Full financial overview for Q1",None ),
    ("Are we tracking well against budget?",None ),
    ]

    for query ,file_bytes in test_queries :
        print (f"\nQUERY: {query }")
        print ("-"*60 )

        result =run_orchestrator (query =query ,file_bytes =file_bytes )

        print (f"Agents called : {', '.join (result ['agents_called'])or 'None'}")
        print (f"Error         : {result ['error']or 'None'}")
        print (f"\nNARRATIVE:\n{result ['narrative']}")
        print ("="*60 )

        time .sleep (10 )