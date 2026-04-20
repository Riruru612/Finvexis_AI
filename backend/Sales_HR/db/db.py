import sqlite3 
import os 

BASE_DIR =os .path .dirname (os .path .dirname (os .path .dirname (os .path .dirname (os .path .abspath (__file__ )))))
DB_NAME =os .path .join (BASE_DIR ,"finvexis.db")

def get_connection ():
    return sqlite3 .connect (DB_NAME ,check_same_thread =False )

def init_db ():
    conn =get_connection ()
    cursor =conn .cursor ()

    cursor .execute ("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        company TEXT,
        status TEXT,
        deal_stage TEXT,
        lead_score INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor .execute ("""
    CREATE TABLE IF NOT EXISTS interactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        note TEXT,
        type TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(customer_id) REFERENCES customers(id)
    )
    """)

    cursor .execute ("""
    CREATE TABLE IF NOT EXISTS candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        skills TEXT,
        experience TEXT,
        projects TEXT,
        achievements TEXT,
        score INTEGER,
        decision TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn .commit ()
    conn .close ()

    print (" Database initialized successfully!")

if __name__ =="__main__":
    init_db ()