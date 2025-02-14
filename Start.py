import os
import pyodbc
from openai import OpenAI
from dotenv import load_dotenv
from typing import Optional, Literal, Dict, Any
from pydantic import BaseModel, Field
from db_utils import format_schema_for_prompt

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

class SqlInteract(BaseModel):
    """SQL Insert Record"""
    table_name: str = Field(description="Name of the table to be modified")
    sql_query: str = Field(description="based on the table name and values, create a valid sql query")   
    confidence_score: float = Field(description="Confidence score between 0 and 1")
    description: str = Field(description="Cleaned description of the request")

def route_sql_request(user_input: str) -> Dict:
    """Router LLM call to determine the type and extract values from user input"""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    system_prompt = f"""Determine the type of SQL request based on the user's input and table to be used.
    {format_schema_for_prompt()}
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


def create_record(description: str):
    system_prompt = f"""Determine the SQL query to be used to insert a record into the table based on the description.
    {format_schema_for_prompt()}
    """
    
    completion = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": description},
        ],
        response_format=SqlInteract,
    )       

    result = completion.choices[0].message.parsed

    return result

user_input = "Give me the list of students whose age is greater than 30, I want their name and age, check if these students are available in employee table"
sql_request = route_sql_request(user_input)

print(sql_request.request_type)


sql_insert_record = create_record(user_input)
print(sql_insert_record)
