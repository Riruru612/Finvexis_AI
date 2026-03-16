from langchain.agents import create_agent
from langchain_groq import ChatGroq

from sales_hr_tools.lead_scoring_tool import lead_scoring_tool
from sales_hr_tools.resume import resume_match_tool
from sales_hr_tools.crm_tool import add_customer, get_customer
from sales_hr_tools.hr_policy_tool import hr_policy_tool
import os
from dotenv import load_dotenv

load_dotenv()
groq_api_key = os.getenv("GROQ_API")

def create_sales_hr_agent():

    llm = ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=groq_api_key)

    tools = [
        lead_scoring_tool,
        resume_match_tool,
        add_customer,
        get_customer,
        hr_policy_tool
    ]

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt="""
You are the Sales & HR assistant for Finvexis AI.

Your responsibilities include:
- Evaluating sales leads
- Screening resumes for job roles
- Managing CRM customer data
- Answering HR policy questions

When responding:
1. Clearly explain what action you performed.
2. Mention which tool was used.
3. Provide the result in a structured way.
"""
    )

    return agent