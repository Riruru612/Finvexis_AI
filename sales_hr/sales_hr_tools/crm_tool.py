from langchain.tools import tool

crm_db = {}

@tool
def add_customer(name:str, email:str, company:str):
    """
    Adds a new customer to CRM.
    """

    crm_db[email] = {
        "name": name,
        "company": company,
        "status": "lead"
    }

    return f"Customer {name} added to CRM."

@tool
def get_customer(email:str):
    """
    Fetch customer information.
    """

    return crm_db.get(email, "Customer not found")