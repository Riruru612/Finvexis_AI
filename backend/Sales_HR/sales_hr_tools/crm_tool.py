from langchain .tools import tool 
from db .db import get_connection 
from utils .helpers import validate_email 
from pydantic import BaseModel ,Field 
from typing import Optional 

ALLOWED_FIELDS =["name","company","status","deal_stage","lead_score"]

class AddCustomerInput (BaseModel ):
    name :str =Field (...,description ="Full name of the customer")
    email :str =Field (...,description ="Valid email address of the customer")
    company :Optional [str ]=Field ("Unknown",description ="Company name")

class GetCustomerInput (BaseModel ):
    email :str 

class UpdateCustomerInput (BaseModel ):
    email :str 
    field :str 
    value :str 

class DeleteCustomerInput (BaseModel ):
    email :str 

class AddInteractionInput (BaseModel ):
    email :str 
    note :str 
    interaction_type :str =Field (...,description ="call / email / meeting")

class GetInteractionsInput (BaseModel ):
    email :str 

@tool (args_schema =AddCustomerInput )
def add_customer (name :str ,email :str ,company :str ="Unknown"):
    """Add a new customer to CRM."""

    try :
        email =validate_email (email )
    except ValueError as e :
        return str (e )

    try :
        conn =get_connection ()
        cursor =conn .cursor ()

        cursor .execute ("""
        INSERT OR IGNORE INTO customers (name, email, company, status, deal_stage)
        VALUES (?, ?, ?, ?, ?)
        """,(name ,email ,company ,"lead","new"))

        conn .commit ()

        if cursor .rowcount ==0 :
            conn .close ()
            return f"{name } already exists in CRM ({email })."

        conn .close ()
        return f"{name } ({email }) added to CRM as a lead."

    except Exception as e :
        return f"Error adding customer: {str (e )}"

@tool (args_schema =GetCustomerInput )
def get_customer (email :str ):
    """Fetch customer details using email."""

    try :
        conn =get_connection ()
        cursor =conn .cursor ()

        cursor .execute ("SELECT * FROM customers WHERE email=?",(email ,))
        result =cursor .fetchone ()

        conn .close ()

        if result :
            keys =["id","name","email","company","status","deal_stage","lead_score","created_at"]
            data =dict (zip (keys ,result ))

            return f"""
Customer Details:
Name: {data ['name']}
Email: {data ['email']}
Company: {data ['company']}
Status: {data ['status']}
Stage: {data ['deal_stage']}
Lead Score: {data ['lead_score']}
""".strip ()

        return f"No customer found with email {email }."

    except Exception as e :
        return f"Error fetching customer: {str (e )}"

@tool (args_schema =UpdateCustomerInput )
def update_customer (email :str ,field :str ,value :str ):
    """Update a specific field for a customer."""

    if field not in ALLOWED_FIELDS :
        return f"Invalid field. Allowed fields: {', '.join (ALLOWED_FIELDS )}"

    try :
        conn =get_connection ()
        cursor =conn .cursor ()

        cursor .execute (f"""
        UPDATE customers SET {field }=? WHERE email=?
        """,(value ,email ))

        conn .commit ()
        conn .close ()

        return f"{field } updated successfully for {email }."

    except Exception as e :
        return f"Error updating customer: {str (e )}"

@tool 
def search_customer (query :str ):
    """
    Search customer by name, email, or company.
    """

    try :
        conn =get_connection ()
        cursor =conn .cursor ()

        cursor .execute ("""
        SELECT id, name, email, company 
        FROM customers 
        WHERE name LIKE ? OR email LIKE ? OR company LIKE ?
        """,(f"%{query }%",f"%{query }%",f"%{query }%"))

        results =cursor .fetchall ()
        conn .close ()

        if not results :
            return "No matching customers found."

        if len (results )==1 :
            r =results [0 ]
            return f"Single match: {r [1 ]} ({r [2 ]}) - {r [3 ]}"

        formatted ="\n".join (
        [f"{i +1 }. {r [1 ]} – {r [2 ]} ({r [3 ]})"
        for i ,r in enumerate (results )]
        )

        return f"Multiple customers found:\n\n{formatted }\n\nAsk user to select one."

    except Exception as e :
        return f"Error searching customer: {str (e )}"

@tool (args_schema =DeleteCustomerInput )
def delete_customer (email :str ):
    """Delete a customer from CRM."""

    try :
        conn =get_connection ()
        cursor =conn .cursor ()

        cursor .execute ("DELETE FROM customers WHERE email=?",(email ,))
        conn .commit ()
        conn .close ()

        return f"Customer {email } deleted successfully."

    except Exception as e :
        return f"Error deleting customer: {str (e )}"

@tool (args_schema =AddInteractionInput )
def add_interaction (email :str ,note :str ,interaction_type :str ):
    """Log interaction for a customer (call, email, meeting)."""

    try :
        conn =get_connection ()
        cursor =conn .cursor ()

        cursor .execute ("SELECT id FROM customers WHERE email=?",(email ,))
        customer =cursor .fetchone ()

        if not customer :
            conn .close ()
            return f"Customer {email } not found."

        customer_id =customer [0 ]

        cursor .execute ("""
        INSERT INTO interactions (customer_id, note, type)
        VALUES (?, ?, ?)
        """,(customer_id ,note ,interaction_type ))

        conn .commit ()
        conn .close ()

        return f"{interaction_type } interaction logged for {email }."

    except Exception as e :
        return f"Error logging interaction: {str (e )}"

@tool (args_schema =GetInteractionsInput )
def get_interactions (email :str ):
    """Fetch all interactions for a customer."""

    try :
        conn =get_connection ()
        cursor =conn .cursor ()

        cursor .execute ("SELECT id FROM customers WHERE email=?",(email ,))
        customer =cursor .fetchone ()

        if not customer :
            conn .close ()
            return f"Customer {email } not found."

        customer_id =customer [0 ]

        cursor .execute ("""
        SELECT note, type, created_at
        FROM interactions
        WHERE customer_id=?
        ORDER BY created_at DESC
        """,(customer_id ,))

        results =cursor .fetchall ()
        conn .close ()

        if not results :
            return f"No interactions found for {email }."

        formatted ="\n".join (
        [f"{r [2 ]} | {r [1 ]} → {r [0 ]}"for r in results ]
        )

        return f"Interaction History:\n{formatted }"

    except Exception as e :
        return f"Error fetching interactions: {str (e )}"