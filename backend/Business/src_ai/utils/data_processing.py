import pandas as pd 
from typing import Dict ,Any ,List 

def clean_business_data (df :pd .DataFrame )->pd .DataFrame :

    if 'date'in df .columns :
        df ['date']=pd .to_datetime (df ['date'])
        df =df .sort_values ('date')

    numeric_cols =df .select_dtypes (include =['number']).columns 
    df [numeric_cols ]=df [numeric_cols ].interpolate (method ='linear').fillna (0 )

    df =df .drop_duplicates ()

    return df 

def validate_columns (df :pd .DataFrame ,required :List [str ])->List [str ]:
    missing =[col for col in required if col not in df .columns ]
    return missing 
