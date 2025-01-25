import pandas as pd
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from rasa.core.agent import Agent
from rasa.core.interpreter import RasaNLUInterpreter

# Cargar el CSV
df = pd.read_csv('C:/Users/jaimerodriguezlara/OneDrive - IBM/Escritorio/TFG/Data/PARAMETROS_TJ2.csv')

# Crear un modelo de lenguaje
tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
model = AutoModelForSequenceClassification.from_pretrained('bert-base-uncased')

# Crear un chatbot básico
agent = Agent('chatbot', interpreter=RasaNLUInterpreter())

# Integrar el modelo de lenguaje en el chatbot
agent.model = model

# Crear una API para acceder a los datos del CSV
from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/datos', methods=['GET'])
def get_datos():
    query = request.args.get('query')
    resultados = df[df['columna'] == query]
    return jsonify(resultados.to_dict(orient='records'))

# Conectar el chatbot con la API
agent.api = app

# Iniciar el chatbot
agent.start()

## -------------------------------------------------------------------------------


import llama
from watson_developer_cloud import AssistantV2

# Cargar el modelo de Llama 3
model = llama.load_model("llama-3")

# Crear un cliente de API para interactuar con el chatbot de Watson
assistant = AssistantV2(
    version='2021-11-27',
    iam_api_key='YOUR_API_KEY',
    url='https://api.us-south.assistant.watson.cloud.ibm.com'
)

# Crear un flujo de trabajo para interactuar con el chatbot de Watson
def llama_response(message):
    response = model.predict(message)
    return response

def watson_response(message):
    response = assistant.message(
        workspace_id='YOUR_WORKSPACE_ID',
        input={'message_type': 'text', 'text': message}
    ).get_result()
    return response['output']['text']

# Integrar el chatbot con Llama 3 con el chatbot de Watson
def chatbot_response(message):
    llama_resp = llama_response(message)
    watson_resp = watson_response(llama_resp)
    return watson_resp

# Iniciar el chatbot
chatbot_response("Hola, ¿cómo estás?")