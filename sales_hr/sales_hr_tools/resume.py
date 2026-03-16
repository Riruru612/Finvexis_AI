from langchain.tools import tool
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer('all-MiniLM-L6-v2')

@tool
def resume_match_tool(resume_text:str, job_description:str):
    """
    Compares resume with job description and gives match score.
    """

    resume_embedding = model.encode([resume_text])
    jd_embedding = model.encode([job_description])

    score = cosine_similarity(resume_embedding, jd_embedding)[0][0]

    percentage = round(score * 100, 2)

    if percentage > 75:
        decision = "Shortlist"
    elif percentage > 50:
        decision = "Consider"
    else:
        decision = "Reject"

    return f"Match Score: {percentage}%, Recommendation: {decision}"