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
        return df.astype(str)  # Ensure all data is treated as string for querying
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return None

data = load_csv()

# Define context for SQL generation
script_context = (
    "The table is named 'data' and contains the following columns:\n"
    "N_DESCARGA, fecha, hora, comentarioDesc, comentarioExp, configuracion, puffing_final, limitador_z1, limitador_z2, presion_base, tipo_impurezas, tiempo_sonda, tiempo_impurezas, ne_corte, pared, validada, itf, icc, hx, vf, valvula_li1, valvula_li2, valvula_he, valvula_cx1, valvula_cx2, valvula_nb, valvula_cnb1, valvula_cnb2, presion_cx1, presion_cx2, posicion_sonda_d4top, posicion_electrodo_a7top, posicion_sonda_b2bot, polaridad_limitador_a3bot, polaridad_limitador_c3bot, polaridad_electrodo_a7top, presion_nb, presion_cnb1, presion_cnb2, angulo_DR, potencia_nominal_ECRH1, potencia_depositada_ECRH1, inyeccion_OnOff_axis_ECRH1, modulacion_ECRH1, angulo_polarizacion_lineal_ECRH1, angulo_polarizacion_eliptica_ECRH1, angulo_toroidal_deposicion_ECRH1, angulo_1_ECRH1, angulo_2_ECRH1, n_paralelo_ECRH1, fmod_ECRH1, rho_ECRH1, tini_ECRH1, longitud_pulso_nominal_ECRH1, longitud_pulso_real_ECRH1, potencia_nominal_ECRH2, inyeccion_OnOff_axis_ECRH2, modulacion_ECRH2, angulo_polarizacion_lineal_ECRH2, angulo_toroidal_deposicion_ECRH2, angulo_1_ECRH2, angulo_2_ECRH2, n_paralelo_ECRH2, tini_ECRH2, longitud_pulso_nominal_ECRH2, fmod_ECRH2, rho_ECRH2, longitud_pulso_real_ECRH2, VAccel_nominal_NBI1, IAccel_nominal_NBI1, tini_NBI1, longitud_pulso_nominal_NBI1, potencia_nominal_NBI1, VAccel_real_NBI1, IAccel_real_NBI1, longitud_pulso_real_NBI1, updated_NBI1, potencia_through_port_NBI1, factor_transm_NBI1, VAccel_nominal_NBI2, IAccel_nominal_NBI2, tini_NBI2, longitud_pulso_nominal_NBI2, potencia_nominal_NBI2, potencia_through_port_NBI2, VAccel_real_NBI2, IAccel_real_NBI2, longitud_pulso_real_NBI2, factor_transm_NBI2.\n"
    "Use these exact column names when writing SQL queries.\n"
    "Output ONLY the SQL query, no explanations."
)

def execute_sql_query(sql_query):
    """Executes an SQL query on the loaded DataFrame."""
    try:
        result = ps.sqldf(sql_query, locals())
        return result.to_dict(orient="records")
    except Exception as e:
        return {"error": f"SQL Execution Error: {e}"}

def query_csv(question: str):
    """Processes a natural language question into an SQL query and executes it."""
    if data is None:
        return {"error": "CSV data not loaded."}
    
    prompt = f"{script_context}\nConvert the following question into an SQL query: {question}"
    response = llm.invoke(input=prompt).strip()
    
    sql_query = next((line.strip() for line in response.splitlines() if line.strip().upper().startswith("SELECT")), None)
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
