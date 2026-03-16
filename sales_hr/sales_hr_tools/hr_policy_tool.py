from langchain.tools import tool
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

groq_api_key = os.getenv("GROQ_API")

loader = TextLoader("data/hr_policy.txt")
documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

docs = text_splitter.split_documents(documents)


embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

db = FAISS.from_documents(docs, embeddings)

retriever = db.as_retriever()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    groq_api_key=groq_api_key
)

prompt = ChatPromptTemplate.from_template(
"""
You are an HR assistant.

Use the HR policy context below to answer the question.

Context:
{context}

Question:
{question}
"""
)

@tool
def hr_policy_tool(question: str):
    """
    Answers employee questions related to HR policies like leave policy, work hours, remote work, etc.
    """

    docs = retriever.invoke(question)

    context = "\n".join([doc.page_content for doc in docs])

    chain = prompt | llm

    response = chain.invoke(
        {
            "context": context,
            "question": question
        }
    )

    return response.content