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


