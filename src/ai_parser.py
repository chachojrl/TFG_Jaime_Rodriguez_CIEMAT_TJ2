from langchain_community.llms import Replicate
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
os.environ["REPLICATE_API_TOKEN"] = os.getenv("REPLICATE_API_TOKEN")

# Set up LLaMA-3
llm = Replicate(
    model="meta/meta-llama-3-8b-instruct",
    model_kwargs={"temperature": 0.1, "max_new_tokens": 100}
)

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
