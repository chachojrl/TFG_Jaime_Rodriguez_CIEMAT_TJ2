import pandas as pd
import re
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

# 🔹 Cargar el dataset
csv_path = "PARAMETROS_TJ2.csv"  # Asegúrate de colocar la ruta correcta del archivo
df = pd.read_csv(csv_path, delimiter=";", encoding="ISO-8859-1")

# 🔹 Seleccionar variables relevantes para la predicción
features = ["itf", "vf", "icc", "hx"]
target_ECRH1 = "potencia_nominal_ECRH1"
target_ECRH2 = "potencia_nominal_ECRH2"

# 🔹 Eliminar filas con valores nulos en las variables seleccionadas
df_clean = df.dropna(subset=features + [target_ECRH1, target_ECRH2])

# 🔹 Dividir en conjuntos de entrenamiento y prueba
X = df_clean[features]
y_ECRH1 = df_clean[target_ECRH1]
y_ECRH2 = df_clean[target_ECRH2]

X_train, X_test, y_train_ECRH1, y_test_ECRH1 = train_test_split(X, y_ECRH1, test_size=0.2, random_state=42)
X_train, X_test, y_train_ECRH2, y_test_ECRH2 = train_test_split(X, y_ECRH2, test_size=0.2, random_state=42)

# 🔹 Entrenar modelos de Random Forest
rf_ECRH1 = RandomForestRegressor(n_estimators=100, random_state=42)
rf_ECRH1.fit(X_train, y_train_ECRH1)

rf_ECRH2 = RandomForestRegressor(n_estimators=100, random_state=42)
rf_ECRH2.fit(X_train, y_train_ECRH2)

# 🔹 Evaluar el modelo
y_pred_ECRH1 = rf_ECRH1.predict(X_test)
y_pred_ECRH2 = rf_ECRH2.predict(X_test)

mae_ECRH1 = mean_absolute_error(y_test_ECRH1, y_pred_ECRH1)
mse_ECRH1 = mean_squared_error(y_test_ECRH1, y_pred_ECRH1)

mae_ECRH2 = mean_absolute_error(y_test_ECRH2, y_pred_ECRH2)
mse_ECRH2 = mean_squared_error(y_test_ECRH2, y_pred_ECRH2)

print(f"🔹 MAE ECRH1: {mae_ECRH1}, MSE ECRH1: {mse_ECRH1}")
print(f"🔹 MAE ECRH2: {mae_ECRH2}, MSE ECRH2: {mse_ECRH2}")

# 🔹 Función para predecir la potencia nominal
def predecir_potencia(itf, vf, icc, hx):
    entrada = [[itf, vf, icc, hx]]
    pred_ECRH1 = rf_ECRH1.predict(entrada)[0]
    pred_ECRH2 = rf_ECRH2.predict(entrada)[0]

    return {
        "potencia_nominal_ECRH1": pred_ECRH1,
        "potencia_nominal_ECRH2": pred_ECRH2
    }

# 🔹 Función para procesar preguntas y hacer predicciones
def procesar_pregunta_y_predecir(pregunta):
    """
    Extrae los valores numéricos de una pregunta y predice la potencia nominal.
    """
    valores = re.findall(r"[-+]?\d*\.\d+|\d+", pregunta)

    if len(valores) >= 4:
        itf, vf, icc, hx = map(float, valores[:4])
        predicciones = predecir_potencia(itf, vf, icc, hx)
        
        respuesta = (
            f"🔹 Basado en los valores proporcionados:\n"
            f"- **itf:** {itf}\n"
            f"- **vf:** {vf}\n"
            f"- **icc:** {icc}\n"
            f"- **hx:** {hx}\n\n"
            f"🔮 Predicciones de potencia nominal:\n"
            f"- **ECRH1:** {predicciones['potencia_nominal_ECRH1']:.2f} unidades\n"
            f"- **ECRH2:** {predicciones['potencia_nominal_ECRH2']:.2f} unidades\n"
        )
    else:
        respuesta = "❌ No encontré suficientes valores en la pregunta. Proporciona **itf, vf, icc y hx**."

    return respuesta

# 🔹 Simulación de interacción con el chatbot
while True:
    pregunta = input("\n🗣️ Haz una pregunta sobre predicción de potencia (o escribe 'salir' para terminar):\n>> ")
    
    if pregunta.lower() in ["salir", "exit", "quit"]:
        print("👋 Saliendo del chatbot...")
        break

    respuesta = procesar_pregunta_y_predecir(pregunta)
    print(respuesta)
