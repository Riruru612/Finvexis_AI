from fastapi import APIRouter ,UploadFile ,File ,Form ,HTTPException 
import sys 
import os 
from typing import Optional 

from finance .orchestrator import run_orchestrator 

router =APIRouter (prefix ="/finance",tags =["finance"])

@router .post ("/process")
async def process_finance (
query :str =Form (...),
file :Optional [UploadFile ]=File (None )
):
    try :
        file_bytes =None 
        filename =None 

        if file :
            file_bytes =await file .read ()
            filename =file .filename 

        result =run_orchestrator (
        query =query ,
        file_bytes =file_bytes ,
        filename =filename 
        )

        if result .get ("error"):
            raise HTTPException (status_code =500 ,detail =result ["error"])

        return result 
    except Exception as e :
        raise HTTPException (status_code =500 ,detail =str (e ))
