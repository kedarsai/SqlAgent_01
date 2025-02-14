import os
import pyodbc
from openai import OpenAI
from dotenv import load_dotenv
from typing import Optional, Literal, Dict, Any
from pydantic import BaseModel, Field

load_dotenv()

# SQL Server connection
conn_str = (
    "Driver={SQL Server};"
    "Server=localhost;"
    "Database=YourDatabaseName;"
    "Trusted_Connection=yes;"
)

class SqlRequestType(BaseModel):
    """Router LLM call: Determine the type of Sql request"""

    request_type: Literal["new_record", "modify_record", "delete_record"] = Field(
        description="Type of sql request being made"
    )
    table_name: str = Field(description="Name of the table to be modified")
    # values: Dict[str, Any] = Field(description="Dictionary of column values")
    # where_condition: Dict[str, Any] = Field(description="Dictionary of conditions for updates/deletes")
    confidence_score: float = Field(description="Confidence score between 0 and 1")
    description: str = Field(description="Cleaned description of the request")

def route_sql_request(user_input: str) -> Dict:
    """Router LLM call to determine the type and extract values from user input"""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    system_prompt = """Determine the type of SQL request based on the user's input and table to be used,
    """
    
    completion = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ],
        response_format=SqlRequestType,
    )
    
    result = completion.choices[0].message.parsed
    
    return result
user_input = "Create a new employee record of john whose age is 30 and gender is male"
sql_request = route_sql_request(user_input)
print(sql_request)
