import pandas as pd
from langchain_community.llms import Replicate
from dotenv import load_dotenv
import os
import nest_asyncio
import pandasql as ps
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Apply async compatibility
nest_asyncio.apply()

# Load environment variables
load_dotenv()
os.environ["REPLICATE_API_TOKEN"] = os.getenv("REPLICATE_API_TOKEN")

# Initialize LLaMA 3 Model
llm = Replicate(
    model="meta/meta-llama-3-8b-instruct",
    model_kwargs={"temperature": 0.7, "max_new_tokens": 100}
)

# Load the CSV file in memory
CSV_FILE = "../data/processed/cleaned_csv_data.csv"
def load_csv():
    try:
        df = pd.read_csv(CSV_FILE)
        df.columns = df.columns.str.strip().str.lower()
        return df.astype(str)
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return None

data = load_csv()

def execute_sql_query(sql_query):
    """Executes an SQL query on the loaded DataFrame."""

    try:
        result = ps.sqldf(sql_query, {"data": data})
        result.to_dict(orient="records")

        prompt = f"""
        You are an AI that translates JSON to natural language 
        
        Convert the following JSON into a precise Natural language:
        "{result}"

        Return ONLY the Natural Language response """
        
        response = llm.invoke(input=prompt).strip()
        return response
    except Exception as e:
        return {"error": f"SQL Execution Error: {e}"}

def query_csv(question: str):
    """Processes a natural language question into an SQL query and executes it."""
    if data is None:
        return {"error": "CSV data not loaded."}
    
    #prompt = f"{script_context}\nConvert the following question into an SQL query: {question}"
    prompt = f"""
    You are an AI that translates user queries into precise SQL queries.
    The table name is 'data' and contains the following columns:

    {', '.join(data.columns)}

    Follow these strict rules:
    - Always generate a SQL SELECT query.
    - Never add comments or explanations.
    - Use exact column names from the table.
    - The column fecha is like `YYYY/MM/DD`
    - Always use lowercase column names.
    - If the user asks for a number of discharge (N_DESCARGA), filter using `WHERE n_descarga = ...`
    - If the user asks for how many of something, use `COUNT(*) AS total_count`
    - If the user requests specific columns, include them explicitly in the SELECT statement.
    - If the user asks for all available data, use `SELECT *`
    - Ensure that all filters (WHERE conditions) use exact column names and values.
    - If the user query references a configuration, use `WHERE configuracion = ...`
    - The query must be a valid SQL statement, even if the user input is unstructured.

    Convert the following user request into a precise SQL query:
    "{question}"

    Return ONLY the SQL query with no extra text.
    """



    response = llm.invoke(input=prompt).strip()
    print(response)
    
    if not response:
        return {"error": "Invalid SQL query generated."}
    
    return execute_sql_query(response)

# FastAPI Endpoint
description = "API to process queries related to TJ-II experiment data."
app = FastAPI(title="TJ-II CSV Query API", description=description)

class Question(BaseModel):
    question: str

@app.post("/ask")
def ask_question(question: Question):
    return query_csv(question.question)
