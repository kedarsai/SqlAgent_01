import pyodbc
from typing import Dict, List, Tuple

def get_connection():
    """Create and return a database connection"""
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=LAPTOP-N4MDHON5;"
        "DATABASE=MyPractice;"
        "Trusted_Connection=yes;"
    )

def get_schema_info() -> Dict[str, List[Tuple[str, str]]]:
    """
    Get database schema information including tables and their columns
    Returns: Dict[table_name, List[Tuple[column_name, data_type]]]
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Dictionary to store table schema information
        schema_info = {}
        
        # Query to get all user tables
        tables_query = """
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
        """
        
        # For each table, get its columns
        for table in cursor.execute(tables_query).fetchall():
            table_name = table[0]
            columns_query = f"""
                SELECT COLUMN_NAME, DATA_TYPE 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = '{table_name}'
                ORDER BY ORDINAL_POSITION
            """
            
            columns = cursor.execute(columns_query).fetchall()
            schema_info[table_name] = [(col[0], col[1]) for col in columns]
        
        cursor.close()
        conn.close()
        return schema_info
        
    except Exception as e:
        print(f"Error reading schema: {e}")
        return {}

def format_schema_for_prompt() -> str:
    """Format schema information for use in prompts"""
    schema = get_schema_info()
    prompt = "Table Schema:\n"
    
    for table, columns in schema.items():
        prompt += f"- {table} ("
        prompt += ", ".join([f"{col[0]} {col[1]}" for col in columns])
        prompt += ")\n"
    
    return prompt

def test_sql_connection():
    try:
        conn = get_connection()
        print("Yes")  # Connection successful
        conn.close()
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

if __name__ == "__main__":
    # Test connection
    if test_sql_connection():
        # Print schema if connection successful
        print("\nDatabase Schema:")
        print(format_schema_for_prompt())
