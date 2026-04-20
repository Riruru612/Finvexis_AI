from langchain .tools import tool 
from langchain_groq import ChatGroq 
from langchain_core .prompts import ChatPromptTemplate 
from dotenv import load_dotenv 
import os 

load_dotenv ()

llm =ChatGroq (
model ="llama-3.1-8b-instant",
groq_api_key =os .getenv ("GROQ_API")or os .getenv ("GROQ_API_KEY")
)

prompt =ChatPromptTemplate .from_template (
"""
You are an expert HR assistant at Finvexis.

Answer the user's question based ONLY on the provided HR policy context.
If the answer is not in the context, say "I couldn't find specific information about this in the uploaded policy."

Context:
{context}

Question:
{question}

Instructions:
1. Provide a direct, structured answer in clear paragraphs or bullet points.
2. Use professional, friendly tone.
3. Organize the information into logical sections using **bold headers**.
4. Aim for concise explanations (4-5 lines per paragraph or section).
5. Highlight key terms (like dates, durations, or specific names) using **bolding**.
6. Ensure the response is well-formatted and visually clean.
7. DO NOT include "Note:" or meta-commentary about what you couldn't find if you have already provided a partial answer.
8. DO NOT say "I couldn't find dates or percentages" unless the user specifically asked for them and they are missing.
9. Avoid long lists of single-sentence bullet points; instead, group related points into short paragraphs or cohesive bullet groups.
"""
)

retriever =None 

def set_hr_retriever (new_retriever ):
    global retriever 
    retriever =new_retriever 

@tool 
def hr_policy_tool (question :str =None ,input :str =None ,filename :str =None ):
    """Answer HR policy questions based on uploaded documents."""

    question =question or input 

    if not question :
        return "FINAL ANSWER: No question provided."

    if retriever is None :
        return "FINAL ANSWER: No HR document uploaded. Please upload a policy PDF first."

    print (f"HR tool called for question: {question }")

    docs =retriever .invoke (question )

    if not docs :
        return "FINAL ANSWER: I couldn't find any relevant sections in the policy that address your question."

    context ="\n".join ([doc .page_content for doc in docs ])

    chain =prompt |llm 

    response =chain .invoke ({
    "context":context ,
    "question":question 
    })

    result =response .content 
    if filename :
        result =f"> **Source Document:** {filename }\n\n{result }"

    return result 