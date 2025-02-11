import os
import re
import pandas as pd
import nest_asyncio
import pandasql as ps
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.logger import logger
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from langchain_community.llms import Replicate

# 🔹 Aplicar compatibilidad para ejecución asincrónica
nest_asyncio.apply()

# 🔹 Cargar variables de entorno
load_dotenv()
os.environ["REPLICATE_API_TOKEN"] = os.getenv("REPLICATE_API_TOKEN")

# 🔹 Inicializar FastAPI
app = FastAPI()

# 🔹 Configurar LLaMA-3 con Replicate
llama3_chat = "meta/meta-llama-3-8b-instruct"
llm = Replicate(
    model=llama3_chat,
    model_kwargs={"temperature": 0.7, "max_new_tokens": 100}
)

# 🔹 Cargar y preprocesar el dataset
file_path = "Data\Datos_del_CSV.csv"  # Ruta del CSV
data = pd.read_csv(file_path, delimiter=";", encoding="ISO-8859-1", low_memory=False)

# Reemplazar valores nulos
for column in data.columns:
    if data[column].dtype == "float64":
        data[column] = data[column].fillna(-1)
        if column == "N_DESCARGA":
            data[column] = data[column].astype(int)
    else:
        data[column] = data[column].fillna("N/A")

# Convertir DataFrame a tipo string
data = data.astype(str)

# 🔹 Definir contexto de SQL para LLaMA-3
script_context = (
    "The table is named 'data' and contains the following columns:\n"
    "N_DESCARGA, fecha, hora, comentarioDesc, comentarioExp, configuracion, "
    "potencia_radiada, energia_diamagnetica.\n"
    "Use exact column names when writing SQL queries.\n"
    "Output only the SQL query, nothing else.\n"
)

# 🔹 Función para ejecutar consultas SQL en el DataFrame
def execute_sql_query(data, sql_query):
    try:
        result = ps.sqldf(sql_query, locals())
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"SQL Execution Error: {e}")

# 🔹 Modelo de predicción con Random Forest
features = ["itf", "vf", "icc", "hx"]
target_ECRH1 = "potencia_nominal_ECRH1"
target_ECRH2 = "potencia_nominal_ECRH2"

df_clean = data.astype(str).replace("N/A", "-1").astype(float).dropna(subset=features + [target_ECRH1, target_ECRH2])

X = df_clean[features]
y_ECRH1 = df_clean[target_ECRH1]
y_ECRH2 = df_clean[target_ECRH2]

X_train, X_test, y_train_ECRH1, y_test_ECRH1 = train_test_split(X, y_ECRH1, test_size=0.2, random_state=42)
X_train, X_test, y_train_ECRH2, y_test_ECRH2 = train_test_split(X, y_ECRH2, test_size=0.2, random_state=42)

rf_ECRH1 = RandomForestRegressor(n_estimators=100, random_state=42)
rf_ECRH1.fit(X_train, y_train_ECRH1)

rf_ECRH2 = RandomForestRegressor(n_estimators=100, random_state=42)
rf_ECRH2.fit(X_train, y_train_ECRH2)

# 🔹 Función para predecir potencia nominal
def predecir_potencia(itf, vf, icc, hx):
    entrada = [[itf, vf, icc, hx]]
    pred_ECRH1 = rf_ECRH1.predict(entrada)[0]
    pred_ECRH2 = rf_ECRH2.predict(entrada)[0]
    return {"potencia_nominal_ECRH1": pred_ECRH1, "potencia_nominal_ECRH2": pred_ECRH2}

# 🔹 Función para procesar preguntas sobre predicciones
def procesar_pregunta_y_predecir(pregunta):
    valores = re.findall(r"[-+]?\d*\.\d+|\d+", pregunta)
    if len(valores) >= 4:
        itf, vf, icc, hx = map(float, valores[:4])
        predicciones = predecir_potencia(itf, vf, icc, hx)
        return {
            "Pregunta": pregunta,
            "Potencia ECRH1": predicciones["potencia_nominal_ECRH1"],
            "Potencia ECRH2": predicciones["potencia_nominal_ECRH2"]
        }
    return {"error": "Faltan parámetros en la pregunta. Se necesitan itf, vf, icc y hx."}

# 🔹 Modelo de datos para preguntas en la API
class Question(BaseModel):
    question: str

# 🔹 Endpoint para consultas SQL con LLaMA-3
@app.post("/ask")
def ask_question(question: Question):
    try:
        print(f"🗣️ Pregunta recibida: {question.question}")

        llm_input = f"{script_context}\nConvert this question into an SQL query: {question.question}"
        response = llm.invoke(input=llm_input).strip()
        sql_query = next((line.strip() for line in response.splitlines() if line.strip().upper().startswith("SELECT")), None)

        if not sql_query:
            raise HTTPException(status_code=400, detail="Invalid SQL query generated.")

        print(f"🔹 SQL Generado: {sql_query}")

        result = execute_sql_query(data, sql_query)
        return result.to_dict(orient="records")

    except Exception as e:
        print(f"⚠️ Error: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {e}")

# 🔹 Endpoint para predicciones de potencia nominal
@app.post("/predict")
def predict_potencia(question: Question):
    return procesar_pregunta_y_predecir(question.question)

# 🔹 Simulación de uso
if __name__ == "__main__":
    print("🚀 Servidor FastAPI corriendo... Realiza preguntas de SQL en '/ask' o predicciones en '/predict'.")
