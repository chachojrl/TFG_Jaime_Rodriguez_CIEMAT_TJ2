import gradio as gr
import urllib3
import pandas as pd
#import requests
import subprocess
import sys
import os
import certifi
#import io
from ai_parser import parse_user_input_with_ai, determine_intent, ask_general_ai, clean_answer, parse_user_input_for_shot_number, query_csv
from data_fetcher import generate_url, fetch_data, extract_data_points
from plotter import plot_data_per_signal
from config_loader import load_keywords, load_signal_options

# ---------------------- CONFIGURATION ---------------------- #
os.environ["SSL_CERT_FILE"] = certifi.where()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://info.fusion.ciemat.es/cgi-bin/TJII_data.cgi"
CSV_FILE = "../data/processed/cleaned_csv_data.csv"

def load_csv():
    try:
        return pd.read_csv(CSV_FILE)
    except Exception as e:
        return f"Error loading CSV: {e}"

df = load_csv()
keywords = load_keywords()
valid_signals = load_signal_options()

# ------------------ END CONFIGURATION ---------------------- #


def run_prediction(shot_number, generate_if_missing="No"):
    """Ejecuta `predict_spectogram.py`, captura su salida y devuelve mensaje e imágenes."""
    try:
        
        result = subprocess.run(
            [sys.executable, "predict_spectogram.py", str(shot_number), generate_if_missing],
            capture_output=True, text=True
        )

        output_lines = result.stdout.strip().split("\n")
        if not output_lines:
            return "Error: No output from prediction script.", None
        
        message = output_lines[0] 

        if "ERROR" in message or "WARNING" in message:
            return message, None

        if "SUCCESS" in message:
            primary_folder = "./spectograms/spectograms_for_try"
            secondary_folder = "./spectograms/spectograms_for_ai_learning"

            image_path = f"{primary_folder}/{shot_number}.png"

            if not os.path.exists(image_path):
                image_path = f"{secondary_folder}/{shot_number}.png"

                if not os.path.exists(image_path):
                    return f"Error: Image for shot {shot_number} not found in both directories.", None

            message = clean_answer(message)
            return message, image_path

    except Exception as e:
        return f"Error running prediction script: {e}", None

# ---------------------- MAIN RESPONSE ---------------------- #
def chatbot_response(user_input):
    """Determina la intención del usuario y ejecuta la acción correspondiente."""
    intent = determine_intent(user_input)

    if intent == "PLOT":
        parsed_data = parse_user_input_with_ai(user_input)
        if parsed_data and "shot" in parsed_data:
            shot = parsed_data["shot"]
            tstart = parsed_data.get("tstart", 0)
            tstop = parsed_data.get("tstop", 2000)
            signals = [sig for sig in parsed_data.get("signals", []) if sig in valid_signals]

            if signals:
                url = generate_url(BASE_URL, shot, len(signals), signals, ["1.00"] * len(signals), tstart, tstop)
                html_content = fetch_data(url)

                if html_content:
                    data_points_dict = extract_data_points(html_content, signals)
                    img_list = []

                    for img_pil in plot_data_per_signal(data_points_dict): 
                        img_list.append(img_pil)

                    if img_list:
                        return f"Plot generated for shot {shot}.", img_list
                    else:
                        return f"Error: No plots could be generated for {shot}.", []
                else:
                    return "No data retrieved.", []
            else:
                return "No valid signals found.", []
        else:
            return "Failed to interpret request.", []
    elif intent == "CSV":
        if isinstance(df, pd.DataFrame):
            csv_response = query_csv(user_input)

            if csv_response:
                return csv_response, []
            else:
                return "No relevant data found in CSV.", []
        else:
            return "CSV data is not available.", []

    elif intent == "PREDICT":
        shot_number = parse_user_input_for_shot_number(user_input)
        generate_if_missing = "Yes"

        result_text, img_path = run_prediction(shot_number, generate_if_missing)

        if img_path:
            return result_text, [img_path]
        else:
            return result_text, []

    else:
        response = ask_general_ai(user_input)
        return response if response else "No response.", None
    
# ------------------ END MAIN RESPONSE ---------------------- #

# ---------------------- GRADIO INTERFACE ---------------------- #
interface = gr.Interface(
    fn=chatbot_response,
    inputs=gr.Textbox(label="Ask a question or request a plot:"),
    outputs=[
        gr.Textbox(label="Response / Prediction Result"),
        gr.Gallery(label="Generated Images"),
    ],
    title="TJ-II Chatbot",
    description="Chatbot para análisis de espectrogramas del TJ-II."
)

if __name__ == "__main__":
    interface.launch()
