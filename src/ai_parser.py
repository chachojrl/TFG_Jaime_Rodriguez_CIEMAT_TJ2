import os
import json
from dotenv import load_dotenv
from ibm_watson_machine_learning.foundation_models import Model
from config_loader import load_signal_options
import pandas as pd
import pandasql as ps
import re


# Load environment variables
load_dotenv()

# Load valid signals from config_loader
valid_signals = set(load_signal_options())

# Define IBM Watsonx.ai model details
MODEL_ID = "meta-llama/llama-3-3-70b-instruct"

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

# Define generation parameters
GEN_PARMS = {
    "DECODING_METHOD": "greedy",
    "MIN_NEW_TOKENS": 1,
    "MAX_NEW_TOKENS": 100
}

# Load project credentials
PROJECT_ID = os.environ["PROJECT_ID"]
CREDENTIALS = {
    "apikey": os.environ["IBM_API_KEY"],  
    "url": os.environ["IBM_WATSON_URL"]
}

# Initialize the IBM Watsonx.ai model
model = Model(MODEL_ID, CREDENTIALS, GEN_PARMS, PROJECT_ID)

def query_llm(prompt):
    """Queries IBM Watsonx.ai LLM and returns the response."""
    response = model.generate(prompt)
    return response['results'][0]['generated_text'].strip()

def parse_user_input_with_ai(user_input):
    """Extracts structured data from user input."""
    prompt = f"""
    You are an AI that extracts structured data from user requests for plasma diagnostics.
    The user will provide a request in natural language, and you must extract the following fields:

    - "shot": integer (discharge number)
    - "tstart": float (start time in seconds, if provided, otherwise 0.00)
    - "tstop": float (stop time in seconds, if provided, otherwise 2000.00)
    - "signals": list of signal names (always as an array, even if only one signal is given)

    Extract structured data from the following input:
    "{user_input}"

    Return ONLY the response in valid JSON format.
    Example Output:
    {{ "shot": 54573, "tstart": 0.0, "tstop": 2000.0, "signals": ["TFI", "ICX"] }}
    """

    response = query_llm(prompt)

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        print("Error parsing JSON:", response)
        return None


import re

def determine_intent(user_input):
    """Uses the LLM to determine if the request is about CSV, plotting, or general inquiry."""
    user_input_lower = user_input.lower()
    contains_signal = any(signal in user_input_lower for signal in valid_signals)

    if contains_signal:
        return "PLOT"

    prompt = f"""
    You are an AI that classifies user requests related to plasma diagnostics.
    The possible categories are:
    - "PLOT": If the user is requesting a diagram, graph, or visualization of any signal.
    - "CSV": If the user is requesting specific numerical or textual data from the dataset.
    - "GENERAL": If the question does not fall into the above categories.

    STRICT CLASSIFICATION RULES:
    - If the user asks **"how many"**, **"cuántos"**, or any question about the **count of records**, classify it as `"CSV"`.
    - If the user asks for **specific data** (dates, shot numbers, parameters), classify it as `"CSV"`.
    - If the user asks for a **graph, visualization, or plot**, classify it as `"PLOT"`.
    - If the question is a general explanation request (e.g., "what is X?"), classify it as `"GENERAL"`.
    
    Classify the following user request:
    "{user_input}"

    Return ONLY one word: "PLOT", "CSV", or "GENERAL".
    No extra words, no explanations, no formatting, and no alternative choices.

    Examples:
    - "Cuántos shots se hicieron en 2024?" → CSV
    - "Dame la tabla con los datos de 2023" → CSV
    - "¿Puedes mostrarme un gráfico de TFI?" → PLOT
    - "Explica qué significa ICX" → GENERAL
    """

    response = query_llm(prompt).strip()

    # DEBUG: Print raw response before processing
    print("LLM raw response:", response)

    # Extract first valid category using regex
    match = re.search(r'\b(PLOT|CSV|GENERAL)\b', response, re.IGNORECASE)
    
    if match:
        return match.group(0).upper()  # Return the matched category in uppercase

    # If extraction fails, default to "GENERAL"
    return "GENERAL"





def ask_general_ai(user_input):
    """Queries the AI model to answer general questions."""
    prompt = f"""
    You are an advanced AI that provides helpful, clear, and concise answers.
    Answer the following question accurately:

    "{user_input}"
    """

    return query_llm(prompt)

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

        - If the Natural Language has a number writen, put it as a numeric number

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
    
    print("LLEGO AQUI")  # Debugging statement

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
        - If the user asks about a year, extract the year from 'fecha' using `substr(fecha, 1, 4)`."
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
            GROUP BY substr(fecha, 1, 4)
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

    sql_query = query_llm(prompt).strip()
    print("Generated SQL Query:", sql_query)  # Debugging output

    if not sql_query or not sql_query.lower().startswith("select"):
        return {"error": "Invalid SQL query generated."}

    return execute_sql_query(sql_query)
