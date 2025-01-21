'''import csv

# Nombres de los archivos
input_file = 'C:/Users/jaimerodriguezlara/OneDrive - IBM/Escritorio/TFG/Data/PARAMETROS_TJ2.csv'  # Cambia esto al nombre de tu archivo CSV
output_file = 'C:/Users/jaimerodriguezlara/OneDrive - IBM/Escritorio/TFG/Data/PARAMETROS_TJ2_WithOut_Endings.csv'  # Nombre del archivo con las líneas procesadas

# Leer y procesar el archivo
with open(input_file, 'r', encoding='latin-1') as infile, open(output_file, 'w', encoding='latin-1', newline='') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)
    
    for row in reader:
        # Convertir la fila en cadena y verificar si no termina en ',' o ';'
        if not any(cell.strip().endswith((',', ';', '.')) for cell in row):
            writer.writerow(row)'''

import pandas as pd
import re

# Ruta del archivo CSV
file_path = 'C:/Users/jaimerodriguezlara/OneDrive - IBM/Escritorio/TFG/Data/PARAMETROS_TJ2.csv'
output_path = 'C:/Users/jaimerodriguezlara/OneDrive - IBM/Escritorio/TFG/Data/PARAMETROS_TJ2_Converted.csv'

# Leer el archivo CSV
df = pd.read_csv(file_path, encoding='latin-1')

# Función para limpiar caracteres específicos al final de una celda
def limpiar_final(celda):
    if isinstance(celda, str):  # Verificar que es texto
        return re.sub(r'[.,;]+$', '', celda.strip())  # Eliminar caracteres del final
    return celda

# Procesar las columnas específicas
if 'comentarioDesc' in df.columns:
    df['comentarioDesc'] = df['comentarioDesc'].fillna('').apply(limpiar_final)

if 'ComentarioExp' in df.columns:
    df['ComentarioExp'] = df['ComentarioExp'].fillna('').apply(limpiar_final)

# Guardar el archivo actualizado
df.to_csv(output_path, index=False, encoding='latin-1')

print("Las columnas 'comentarioDesc' y 'ComentarioExp' fueron limpiadas y el archivo se guardó correctamente.")
