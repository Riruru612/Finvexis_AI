import re 

def validate_email (email :str ):
    if not email :
        raise ValueError ("Email is required.")

    email =email .strip ().lower ()

    if not email .endswith ("@gmail.com"):
        raise ValueError ("Only Gmail addresses are allowed.")

    pattern =r"^[a-zA-Z0-9._%+-]+@gmail\.com$"
    if not re .match (pattern ,email ):
        raise ValueError ("Invalid email format.")

    return email 