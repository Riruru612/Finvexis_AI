def score_resume (skills ,jd_text ,projects ,experience ):
    score =0 

    matched =sum (1 for skill in skills if skill .lower ()in jd_text .lower ())
    score +=min (matched *5 ,40 )

    if "year"in experience .lower ():
        score +=20 
    else :
        score +=10 

    score +=min (len (projects )*5 ,20 )

    return score 