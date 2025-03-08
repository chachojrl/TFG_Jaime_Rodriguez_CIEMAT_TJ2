import os
import cv2
import numpy as np
import joblib
from skimage.feature import hog

# ---------------------- CONFIGURACIÓN ---------------------- #
# Ruta del modelo entrenado
model_path = "mhd_detector_model.pkl"

# Ruta de la carpeta con los espectrogramas para probar
input_folder = "../data/spectograms/spectograms_for_try"

# Verificar que el modelo existe
if not os.path.exists(model_path):
    raise FileNotFoundError(f"No se encontró el modelo {model_path}. Asegúrate de haberlo entrenado.")

# Cargar el modelo entrenado
model = joblib.load(model_path)

# ---------------------- FUNCIÓN PARA PROCESAR ESPECTROGRAMAS ---------------------- #
def load_images_for_shot(shot_name):
    """Carga las tres imágenes (color, heatmap, blanco y negro) de un espectrograma"""
    filenames = [
        f"{shot_name}.png",         # Color
        f"{shot_name}_N.png",       # Heatmap
        f"{shot_name}_N_bw.png"     # Escala de grises
    ]
    
    images = []
    for filename in filenames:
        img_path = os.path.join(input_folder, filename)
        if os.path.exists(img_path):
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                images.append(cv2.resize(img, (128, 128)))  # Redimensionar imágenes
            else:
                print(f"Advertencia: No se pudo cargar {img_path}")
        #else:
            #print(f"Advertencia: No se encontró {img_path}")

    # Solo devolver imágenes si se cargaron las 3
    return images if len(images) == 3 else None

def extract_features_from_images(images):
    """Extrae las características HOG de las tres imágenes combinadas"""
    hog_features = []
    for img in images:
        features = hog(img, orientations=9, pixels_per_cell=(8, 8),
                       cells_per_block=(2, 2), visualize=False)
        hog_features.extend(features)  # Combinar características de todas las imágenes
    return np.array(hog_features)

def predict_mhd(shot_name):
    """Carga un conjunto de espectrogramas y predice si tienen MHD"""
    images = load_images_for_shot(shot_name)
    if images is None:
        return None
    
    features = extract_features_from_images(images)
    prediction = model.predict([features])[0]
    return "Sí" if prediction == 1 else "No"

# ---------------------- PROCESAR TODOS LOS SPECTOGRAMAS ---------------------- #
# Obtener nombres de todos los archivos en la carpeta
files = os.listdir(input_folder)

# Extraer nombres únicos de los espectrogramas (sin la extensión)
shot_names = set(f.split(".png")[0].replace("_N", "").replace("_N_bw", "") for f in files if f.endswith(".png"))

print("\n**Espectrogramas detectados:**")
print(shot_names)

# Evaluar cada espectrograma
results = {}
for shot in sorted(shot_names):
    result = predict_mhd(shot)
    if result is not None:
        results[shot] = result
        print(f"¿El espectrograma {shot} tiene MHD? {result}")
    #else:
        #print(f"Advertencia: No se pudo analizar {shot} (faltan imágenes)")

print("\n**Análisis completado.**")
