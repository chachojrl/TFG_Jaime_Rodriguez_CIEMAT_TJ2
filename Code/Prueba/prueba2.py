import pandas as pd
from transformers import AutoTokenizer, AutoModelForCausalLM

# Paso 1: Cargar y procesar el CSV
def load_csv(file_path):
    try:
        data = pd.read_csv(file_path)
        print(f"Datos cargados exitosamente con {len(data)} filas y {len(data.columns)} columnas.")
        return data
    except Exception as e:
        print(f"Error al cargar el archivo CSV: {e}")
        return None

# Paso 2: Buscar datos relevantes en el CSV
def query_csv(data, query):
    """
    Procesa la consulta para encontrar información relevante en el CSV.
    """
    try:
        # Por simplicidad, busca la consulta en todas las columnas como texto.
        results = data.apply(lambda row: row.astype(str).str.contains(query, case=False).any(), axis=1)
        matching_rows = data[results]
        return matching_rows
    except Exception as e:
        print(f"Error en la consulta: {e}")
        return None

# Paso 3: Generar respuesta con un modelo LLM
def generate_response(llm_pipeline, query, results):
    if results.empty:
        return f"No se encontraron datos para la consulta: {query}."
    
    # Formatear los resultados encontrados
    response_context = results.to_string(index=False)
    prompt = (
        f"Usuario: {query}\n"
        f"Datos relevantes del CSV:\n{response_context}\n"
        "Genera una respuesta basada en estos datos:"
    )
    return llm_pipeline(prompt)[0]["generated_text"]

# Main: Integrar todo
if __name__ == "_main_":
    # Configuración inicial
    ##csv_file = "C:/Users/jaimerodriguezlara/OneDrive - IBM/Escritorio/TFG/Data/PARAMETROS_TJ2.csv"  # Cambia esto por el camino a tu CSV
    csv_file = "./PARAMETROS_TJ2.csv"
    data = load_csv(csv_file)
    
    print(data)
    
    if data is not None:
        # Configura un modelo generativo (aquí un ejemplo con Hugging Face Transformers)
        pipe = pipeline("text-generation", model="meta-llama/Llama-3.1-8B")
        
        tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B")
        model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.1-8B")

        print("¡Listo para recibir consultas!")
        while True:
            user_query = input("Ingresa tu pregunta (o 'salir' para terminar): ")
            if user_query.lower() == "salir":
                print("Saliendo del chatbot. ¡Hasta luego!")
                break
            
            # Procesar consulta
            results = query_csv(data, user_query)
            response = generate_response(llm_pipeline, user_query, results)
            print(f"Chatbot: {response}")