from fastapi import FastAPI 
from fastapi .middleware .cors import CORSMiddleware 
import uvicorn 
import os 
from dotenv import load_dotenv 

load_dotenv (os .path .join (os .path .dirname (os .path .dirname (os .path .abspath (__file__ ))),".env"))

import sys 
current_dir =os .path .dirname (os .path .abspath (__file__ ))
sys .path .append (os .path .join (current_dir ,"Business"))
sys .path .append (os .path .join (current_dir ,"finance"))
sys .path .append (os .path .join (current_dir ,"Sales_HR"))

from routes import business ,finance ,sales 

app =FastAPI (
title ="Finvexis AI Backend",
description ="Unified API for Business, Finance, and Sales/HR intelligence.",
version ="1.0.0"
)

app .add_middleware (
CORSMiddleware ,
allow_origins =["*"],
allow_credentials =True ,
allow_methods =["*"],
allow_headers =["*"],
)

app .include_router (business .router )
app .include_router (finance .router )
app .include_router (sales .router )

@app .get ("/")
async def root ():
    return {"message":"Welcome to Finvexis AI API"}

if __name__ =="__main__":
    uvicorn .run ("main:app",host ="0.0.0.0",port =8000 ,reload =True )
