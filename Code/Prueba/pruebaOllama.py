import ollama

prompt = "escribe un articulo sobre python" #input("Pregunta: ")

modelo = "llama3.2"

response = ollama.chat(model=modelo, messages = [{'role': 'user', 'content': prompt}])

print(response)
