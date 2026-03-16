from langchain.tools import tool
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    groq_api_key=os.getenv("GROQ_API")
)

prompt = ChatPromptTemplate.from_template(
"""
You are an expert sales analyst.

Evaluate the following lead and assign a lead score from 0–100.

Consider:
- Budget
- Company size
- Industry relevance
- Interest level

Lead Details:
Name: {name}
Company: {company}
Budget: {budget}
Company Size: {company_size}
Interest Level: {interest}
Return output in this format:

Lead Score: <number>/100
Priority: <High / Medium / Low>

Reason:
• Budget evaluation
• Company evaluation
• Interest level analysis
"""
)

@tool
def lead_scoring_tool(name:str, company:str, budget:int, company_size:int, interest:str):
    """Evaluate and score a potential sales lead."""

    chain = prompt | llm

    response = chain.invoke({
        "name": name,
        "company": company,
        "budget": budget,
        "company_size": company_size,
        "interest": interest
    })

    return response.content