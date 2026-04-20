from langchain_community .vectorstores import FAISS 
from langchain_huggingface import HuggingFaceEmbeddings 
from langchain_text_splitters import RecursiveCharacterTextSplitter 
from pypdf import PdfReader 

def create_vector_db (uploaded_file ):

    text =""

    reader =PdfReader (uploaded_file )

    for page in reader .pages :
        content =page .extract_text ()
        if content :
            text +=content 

    splitter =RecursiveCharacterTextSplitter (
    chunk_size =500 ,
    chunk_overlap =50 
    )

    docs =splitter .create_documents ([text ])

    embeddings =HuggingFaceEmbeddings (
    model_name ="sentence-transformers/all-MiniLM-L6-v2"
    )

    db =FAISS .from_documents (docs ,embeddings )

    return db 