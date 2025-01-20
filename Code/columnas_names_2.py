'''import pandas as pd

# Ruta del archivo CSV
file_path = 'C:/Users/Administrador.HP_Jaime/Desktop/TFG-main/Data/PARAMETROS_TJ2.csv'

# Leer las primeras 5 filas del archivo para inspeccionar las columnas

df_preview = pd.read_csv(file_path, encoding='utf-8', nrows=5)

#print(df_preview.columns)

#df['fecha'] = pd.to_datetime(df['fecha'].astype(str), format='%Y%m%d')

print(df_preview['hora'].head())  # Ver los primeros 5 valores de la columna 'fecha'
print(df_preview['hora'].isnull().sum())  # Ver cuántos valores nulos hay en la columna 'fecha'''

import pandas as pd

# Ruta del archivo CSV
file_path = 'C:/Users/Administrador.HP_Jaime/Desktop/TFG-main/Data/PARAMETROS_TJ2.csv'

# Leer el archivo CSV con el separador correcto
df_preview = pd.read_csv(file_path, sep=';', encoding='utf-8', nrows=5)

# Imprimir las columnas y las primeras filas
print("Columnas del DataFrame:", df_preview.columns)
print(df_preview.head())

# Acceder a la columna 'hora'
print(df_preview['hora'].head())


