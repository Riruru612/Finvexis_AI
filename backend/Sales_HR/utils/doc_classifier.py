def classify_document (text :str ):
    text =text .lower ()

    resume_keywords =[
    "skills","projects","experience","education",
    "resume","developer","engineer","intern",
    "work history","contact","email","phone",
    "summary","objective","certifications","languages"
    ]

    hr_keywords =[
    "policy","leave","employee","benefits",
    "company","rules","guidelines","attendance",
    "role","responsibilities","requirement","qualification",
    "description","jd","job"
    ]

    resume_score =sum (1 for k in resume_keywords if k in text )
    hr_score =sum (1 for k in hr_keywords if k in text )

    if resume_score >hr_score :
        return "resume"
    else :
        return "hr"