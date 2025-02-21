import ollama
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

def query_llm(prompt):
    """Realiza una consulta al modelo Ollama y devuelve la respuesta."""
    response = ollama.chat(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )["message"]["content"].strip()
    return response

def parse_user_input_with_ai(user_input):
    """Usa el modelo de IA para extraer datos estructurados de la entrada del usuario."""
    prompt = f"""
    You are an AI that extracts structured data from user requests for plasma diagnostics.
    The user will provide a request in natural language, and you must extract the following fields:

    - "shot": integer (discharge number)
    - "tstart": float (start time in seconds, if provided, otherwise 0.00)
    - "tstop": float (stop time in seconds, if provided, otherwise 2000.00)
    - "signals": list of signal names (always as an array, even if only one signal is given)

    Extract structured data from the following input:
    "{user_input}"

    Provide ONLY the response in a valid JSON format.
    """

    response = query_llm(prompt)

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return None

def determine_intent(user_input):
    """Usa el modelo de IA para determinar si la solicitud es sobre CSV, gráficos o una consulta general."""
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

    Classify the following user request:
    "{user_input}"

    Examples:
    - "Me puedes dar el diagrama de TFI del numero de descarga 54573" → PLOT
    - "Cuál es la fecha del número de descarga 4" → CSV
    - "¿Qué tipo de experimento se hizo el 12 de enero?" → CSV
    - "Explícame qué significa el parámetro ICX" → GENERAL

    Provide ONLY the category name (PLOT, CSV, or GENERAL) as output.
    """

    response = query_llm(prompt)
    print(response)
    return response.upper()

def ask_general_ai(user_input):
    """Consulta al modelo de IA para responder preguntas generales."""
    prompt = f"""
    You are an advanced AI that provides helpful, clear, and concise answers.
    Answer the following question accurately:

    "{user_input}"
    """

    return query_llm(prompt)
