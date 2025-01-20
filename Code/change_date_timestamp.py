'''import pandas as pd

file_path = 'C:/Users/jaimerodriguezlara/OneDrive - IBM/Escritorio/TFG/CSV_Y_EXCEL_PARAMETROS_TJ2/PARAMETROS_TJ2_CSV_UTF-8.csv'
df = pd.read_csv(file_path)

df['fecha'] = pd.to_datetime(df['fecha'].astype(str), format='%Y%m%d')

df['hora'] = pd.to_datetime(df['hora'], format='%H:%M').dt.time
df['timestamp'] = pd.to_datetime(df['fecha'].astype(str) + ' ' + df['hora'].astype(str))

output_path = 'C:/Users/jaimerodriguezlara/OneDrive - IBM/Escritorio/TFG/CSV_Y_EXCEL_PARAMETROS_TJ2/PARAMETROS_TJ2_Converted.csv'
df.to_csv(output_path, index=False)

print("Archivo procesado y guardado correctamente.")'''

'''import pandas as pd

# Ruta del archivo CSV
file_path = 'C:/Users/jaimerodriguezlara/OneDrive - IBM/Escritorio/TFG/CSV_Y_EXCEL_PARAMETROS_TJ2/PARAMETROS_TJ2_CSV_UTF-8.csv'

try:
    # Leer solo las columnas de 'fecha' y 'hora'
    df = pd.read_csv(file_path, encoding='utf-8', usecols=['fecha', 'hora'])
except UnicodeDecodeError:
    print("Codificación UTF-8 fallida. Intentando con latin1...")
    df = pd.read_csv(file_path, encoding='latin1', usecols=['fecha', 'hora'])

# Convertir la columna de fecha (formato YYYYMMDD como integer) a tipo Date
df['fecha'] = pd.to_datetime(df['fecha'].astype(str), format='%Y%m%d')

# Combinar las columnas de fecha y hora para crear una columna de tipo Timestamp
df['hora'] = pd.to_datetime(df['hora'], format='%H:%M').dt.time
df['timestamp'] = pd.to_datetime(df['fecha'].astype(str) + ' ' + df['hora'].astype(str))

# Guardar el resultado en un nuevo archivo CSV
output_path = 'C:/Users/jaimerodriguezlara/OneDrive - IBM/Escritorio/TFG/CSV_Y_EXCEL_PARAMETROS_TJ2/PARAMETROS_TJ2_Converted.csv'
df.to_csv(output_path, index=False)

print("Archivo procesado y guardado correctamente.")'''

import pandas as pd

# Ruta del archivo CSV
file_path = 'C:/Users/jaimerodriguezlara/OneDrive - IBM/Escritorio/TFG/CSV_Y_EXCEL_PARAMETROS_TJ2/PARAMETROS_TJ2_CSV_UTF-8.csv'

# Leer el archivo CSV
df = pd.read_csv(file_path, encoding='utf-8', on_bad_lines='skip')

# Convertir la columna 'fecha' (formato YYYYMMDD como integer) a tipo Date
df['fecha'] = pd.to_datetime(df['fecha'].astype(str), format='%Y%m%d')

# Convertir la columna 'hora' de tipo string a tipo Time
df['hora'] = pd.to_datetime(df['hora'], format='%H:%M').dt.time

# Crear una nueva columna 'timestamp' combinando 'fecha' y 'hora'
df['timestamp'] = pd.to_datetime(df['fecha'].astype(str) + ' ' + df['hora'].astype(str))

# Ruta del archivo de salida
output_path = 'C:/Users/jaimerodriguezlara/OneDrive - IBM/Escritorio/TFG/CSV_Y_EXCEL_PARAMETROS_TJ2/PARAMETROS_TJ2_Converted.csv'

# Guardar el DataFrame actualizado a un nuevo archivo CSV, sin alterar las demás columnas
df.to_csv(output_path, index=False)

print("Archivo procesado y guardado correctamente.")


