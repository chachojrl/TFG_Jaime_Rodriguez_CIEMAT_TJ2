from langchain_community.llms import Replicate
import json
import os
from dotenv import load_dotenv
from config_loader import load_signal_options

# Load environment variables
load_dotenv()
os.environ["REPLICATE_API_TOKEN"] = os.getenv("REPLICATE_API_TOKEN")

# Set up LLaMA-3
llm = Replicate(
    model="meta/meta-llama-3-8b-instruct",
    model_kwargs={"temperature": 0.1, "max_new_tokens": 100}
)

# Load valid signals from config_loader
valid_signals = set(load_signal_options())

def parse_user_input_with_ai(user_input):
    """Uses an AI model to extract structured data from user input."""
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

    response = llm.invoke(input=prompt).strip()

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return None

def determine_intent(user_input):
    """Uses LLM to determine if the request is about the CSV, plotting, or general inquiry."""
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
    
    response = llm.invoke(input=prompt).strip()
    print(response)
    return response.upper()
