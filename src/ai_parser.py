import json
import os
from dotenv import load_dotenv
from config_loader import load_signal_options



# Cargar variables de entorno
load_dotenv()

# Cargar señales válidas desde config_loader
valid_signals = set(load_signal_options())

# Definir el modelo global
LLM_MODEL = "llama3"

CSV_FILE = "../data/processed/cleaned_csv_data.csv"

def clean_answer(user_input):
    """Limpia la respuesta usando el modelo LLM."""
    prompt = f"""
    You are an AI that cleans user input and returns a clear and concise version.
    
    Clean the following input:
    "{user_input}"

    Return ONLY the cleaned response as a string.
    """
    return query_llm(prompt)
    

def load_csv():
    """Loads the CSV into a Pandas DataFrame and cleans column names."""
    try:
        df = pd.read_csv(CSV_FILE, dtype={
            "fecha": "string",
            "hora": "string",
            "validada": "string"
        }, low_memory=False)
        df.columns = df.columns.str.strip().str.lower()
        return df.astype(str)
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return None

data = load_csv()

def query_llm(prompt):
    """Realiza una consulta al modelo Ollama y devuelve la respuesta."""
    response = ollama.chat(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )["message"]["content"].strip()
    return response

def parse_user_input_for_shot_number(user_input):
    """Extracts shot number from user input."""
    prompt = f"""
    You are an AI that extracts the first full number from the user request:
    - "shot": integer (discharge number)

    Extract the number from the following input:
    "{user_input}"

    Return ONLY the response as an integer.
    Example Output:
    57546
    """
    response = query_llm(prompt)
    
    try:
        return int(response)  # Convertir a entero para asegurar que es válido
    except ValueError:
        print("Error parsing shot number:", response)
        return None

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

    return response

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        print("Error parsing JSON:", response)
        return None

def determine_intent(user_input):
    """Usa el modelo de IA para determinar si la solicitud es sobre CSV, gráficos, prediccion o una consulta general."""
    user_input_lower = user_input.lower()
    contains_signal = any(signal in user_input_lower for signal in valid_signals)

    if contains_signal:
        return "PLOT"

    prompt = f"""
    You are an AI that classifies user requests related to plasma diagnostics.
    The possible categories are:
    - "PLOT": If the user is requesting a diagram, graph, or visualization of any signal.
    - "CSV": If the user is requesting specific numerical or textual data from the dataset.
    - "PREDICT": If the user is requesting information about a spectogram or MHD. 
    - "GENERAL": If the question does not fall into the above categories.

    STRICT CLASSIFICATION RULES:
    - If the user asks **"how many"**, **"cuántos"**, or any question about the **count of records**, classify it as `"CSV"`.
    - If the user asks for **specific data** (dates, shot numbers, parameters), classify it as `"CSV"`.
    - If the user asks for a **graph, visualization, or plot**, classify it as `"PLOT"`.
    - If the user ask for a **spectogram or mhd**, classify it as `"PREDICT"`.
    - If the question is a general explanation request (e.g., "what is X?"), classify it as `"GENERAL"`.
    
    Classify the following user request:
    "{user_input}"

    Return ONLY one word: "PLOT", "CSV", "PREDICT" or "GENERAL".
    No extra words, no explanations, no formatting, and no alternative choices.

    Examples:
    - "Cuántos shots se hicieron en 2024?" → CSV
    - "Dame la tabla con los datos de 2023" → CSV
    - "¿Puedes mostrarme un gráfico de TFI?" → PLOT
    - "¿La descarga 57547 tiene mhd?" → PREDICT
    - "Explica qué significa ICX" → GENERAL
    """

    response = query_llm(prompt)
    print(response)
    return response.upper()

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

    prompt = f"""
        You are an AI that translates user queries into precise SQL queries.
        The table name is 'data' and contains the following columns:

        {', '.join(data.columns)}

        Follow these strict rules:
        - Always generate a valid SQL query.
        - Always include `FROM data` in the query.
        - Only return one single SQL statement.
        - Never use `AS` to rename columns.
        - Never add comments, explanations, extra formatting, or multiple SQL queries.
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
        - If the user asks for the highest or lowest value of a numerical column, ensure to use: SELECT MAX(CAST(column_name AS INTEGER)) FROM data; or SELECT MIN(CAST(column_name AS INTEGER)) FROM data; replacing `column_name` with the appropriate column requested.
        - If the user query references a configuration, use `WHERE configuracion = ...`.
        - The SQL query must be valid even if the user input is unstructured.

        Convert the following user request into a precise SQL query:
        "{question}"

        Return ONLY the SQL query, with no extra text, no comments, no explanations, and no Markdown formatting.
    """

    sql_query = query_llm(prompt).strip()
    print("Generated SQL Query:", sql_query)  # Debugging output

    # Ensure only a single valid SQL statement is returned
    sql_query = sql_query.split(";")[0].strip()  # Keep only the first SQL statement before any semicolon

    if not sql_query.lower().startswith("select"):
        return {"error": "Invalid SQL query generated."}

    return execute_sql_query(sql_query)
