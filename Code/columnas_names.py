import pandas as pd

# Ruta del archivo CSV
file_path = 'C:/Users/jaimerodriguezlara/OneDrive - IBM/Escritorio/TFG/codigo/PARAMETROS_TJ2_CSV_UTF-8.csv'

# Leer las primeras 5 filas del archivo para inspeccionar las columnas

df_preview = pd.read_csv(file_path, encoding='utf-8', nrows=5)

#print(df_preview.columns)

#df['fecha'] = pd.to_datetime(df['fecha'].astype(str), format='%Y%m%d')

print(df_preview['hora'].head())  # Ver los primeros 5 valores de la columna 'fecha'
print(df_preview['hora'].isnull().sum())  # Ver cuántos valores nulos hay en la columna 'fecha'

