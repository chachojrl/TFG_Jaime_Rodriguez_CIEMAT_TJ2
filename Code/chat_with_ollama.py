import ollama
import subprocess
import re

def chat_with_ollama():
    print("Bienvenido al chat con Ollama. Escriba 'Salir' para finalizar la conversación")
    
    while True:
        user_input = input("Tu: ")
        
        if user_input.lower() == 'salir':
            print("Adios!!")
            break
        
        # Verificar si el texto incluye "número de descarga" y señales específicas
        if re.search(r'numero de descarga', user_input, re.IGNORECASE) and \
           re.search(r'TFI|Densidad2_', user_input, re.IGNORECASE):
            print("Ejecutando el script 'diagramasWeb.py'...")
            
            try:
                # Ejecutar el fichero diagramasWeb.py (Cambiar python runable)
                subprocess.run(["C:/Users/rodla/miniconda3/envs/tfg/python.exe", "./Code/diagramasWeb.py"], check=True)

            except subprocess.CalledProcessError as e:
                print("Hubo un error al ejecutar 'diagramasWeb.py':", e)
            continue
        
        # Enviar el texto al modelo de Ollama
        response = ollama.generate(model='llama3', prompt=user_input)
        print("Bot: ", response['response'])

# Iniciar el chat
chat_with_ollama()

# Me puedes dar la tabla del numero de descarga 57547 con TFI y Densidad2_
