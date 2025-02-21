import pandas as pd
import ollama
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

# Define the global LLM model
LLM_MODEL = "llama3"

# Load the CSV file into memory
CSV_FILE = "../data/processed/cleaned_csv_data.csv"

def load_csv():
    """Loads the CSV into a Pandas DataFrame and cleans column names."""
    try:
        df = pd.read_csv(CSV_FILE)
        df.columns = df.columns.str.strip().str.lower()
        return df.astype(str)
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return None

data = load_csv()

def query_llm(prompt):
    """Queries the Ollama LLM and returns the response."""
    response = ollama.chat(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )["message"]["content"].strip()
    return response

def execute_sql_query(sql_query):
    """Executes an SQL query on the loaded DataFrame."""
    if data is None:
        return {"error": "CSV data not loaded."}

    try:
        result = ps.sqldf(sql_query, {"data": data})

        # Convert result to JSON
        result_json = result.to_dict(orient="records")
        
        print(result_json)

        # Generate a natural language response
        prompt = f"""
        You are an AI that translates JSON to natural language.
        
        Convert the following JSON into a precise natural language description:
        "{result_json}"

        Return ONLY the natural language response.
        """

        response = query_llm(prompt)
        return response
    except Exception as e:
        return {"error": f"SQL Execution Error: {e}"}

def query_csv(question: str):
    """Processes a natural language question and converts it into an SQL query."""
    if data is None:
        return {"error": "CSV data not loaded."}

    prompt = f"""
        You are an AI that translates user queries into precise SQL queries.
        The table name is 'data' and contains the following columns:

        {', '.join(data.columns)}

        Follow these strict rules:
        - Always generate a valid SQL query.
        - Always include `FROM data` in the query.
        - Never use `AS` to rename columns.
        - Never add comments or explanations.
        - Always use exact column names as they appear in the table.
        - The column 'fecha' is formatted as `YYYY/MM/DD`, where YYYY = Year, MM = Month, and DD = Day.
        - Always use lowercase column names.
        - If the user asks for a specific discharge number (N_DESCARGA), use `WHERE n_descarga = ...`
        - If the user asks about a year, extract the year from 'fecha' using `substr(fecha, 1, 4)`.
        - If the user asks about a month, extract the year and month from 'fecha' using `substr(fecha, 1, 7)`.
        - If the user asks about a specific day, use `fecha` directly.
        - If the user asks for a count, use `COUNT(*)` without aliases.
        - If the user requests specific columns, include them explicitly in the SELECT statement.
        - If the user asks for all available data, use `SELECT *`.
        - Ensure that all filters (WHERE conditions) use exact column names and values.
        - If the user asks for the last shot, use the highest `n_descarga` value.
        - If the user query references a configuration, use `WHERE configuracion = ...`.
        - The SQL query must be valid even if the user input is unstructured.

        Examples of user questions and expected SQL output:
        - User Question: "Which year had the most shots?"
            SQL Query:
            SELECT substr(fecha, 1, 4), COUNT(*)
            FROM data
            GROUP BY strftime('%Y', fecha)
            ORDER BY COUNT(*) DESC
            LIMIT 1;

        - User Question: "Which month had the most shots?"
            SQL Query:
            SELECT substr(fecha, 1, 7), COUNT(*)
            FROM data
            GROUP BY substr(fecha, 1, 7)
            ORDER BY COUNT(*) DESC
            LIMIT 1;

        - User Question: "Which day had the most shots?"
            SQL Query:
            SELECT fecha, COUNT(*)
            FROM data
            GROUP BY fecha
            ORDER BY COUNT(*) DESC
            LIMIT 1;

        Convert the following user request into a precise SQL query:
        "{question}"

        Return ONLY the SQL query with no extra text.
    """

    sql_query = query_llm(prompt)
    print(sql_query)

    if not sql_query:
        return {"error": "Invalid SQL query generated."}

    return execute_sql_query(sql_query)

# FastAPI Endpoint
description = "API to process queries related to TJ-II experiment data."
app = FastAPI(title="TJ-II CSV Query API", description=description)

class Question(BaseModel):
    question: str

@app.post("/ask")
def ask_question(question: Question):
    return query_csv(question.question)
