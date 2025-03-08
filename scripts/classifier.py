import os
import pandas as pd
import cv2
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from skimage.feature import hog
import joblib
from sklearn.metrics import classification_report, accuracy_score

# Ruta a las imágenes de los espectrogramas
IMAGES_FOLDER = "../data/spectograms/spectograms_for_ai_learning"

# Ruta al archivo Excel con etiquetas
EXCEL_PATH = "../data/processed/clasified_spectrograms.xlsx"

# Función para cargar etiquetas desde Excel
def load_labels_from_excel(excel_path):
    df = pd.read_excel(excel_path)
    df['MHD'] = df['MHD'].map({'Y': 1, 'N': 0})  # Convertir a valores numéricos
    return df

# Cargar imágenes de un shot específico
def load_images_for_shot(shot_number):
    print(shot_number)
    filenames = [
        f"{shot_number}.png",          # Color
        f"{shot_number}_N.png",        # Heatmap
        f"{shot_number}_N_bw.png"      # Escala de grises
    ]
    images = []
    
    for filename in filenames:
        img_path = os.path.join(IMAGES_FOLDER, filename)
        if os.path.exists(img_path):
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            images.append(cv2.resize(img, (128, 128)))  # Redimensionar imágenes
        else:
            print(f"Warning: {img_path} not found")
            return None  # Si falta una imagen, descartar el shot
    
    return images

# Extraer características HOG de las imágenes concatenadas
def extract_features_from_images(images):
    hog_features = []
    for img in images:
        features = hog(img, orientations=9, pixels_per_cell=(8, 8),
                       cells_per_block=(2, 2), visualize=False)
        hog_features.extend(features)  # Concatenar features de las 3 imágenes
    return np.array(hog_features)

# Cargar y procesar el dataset completo
def load_dataset(excel_path):
    df = load_labels_from_excel(excel_path)

    all_features = []
    all_labels = []

    for _, row in df.iterrows():
        shot_number = row['Spectrogram Number']
        mhd_label = row['MHD']

        images = load_images_for_shot(shot_number)
        if images is not None:
            features = extract_features_from_images(images)
            all_features.append(features)
            all_labels.append(mhd_label)

    # Convertir a arrays de NumPy
    X = np.array(all_features)
    y = np.array(all_labels)

    if len(X) == 0:
        raise ValueError("No se encontraron datos válidos para entrenar el modelo.")

    return X, y

# Entrenar y evaluar el modelo
def train_and_evaluate_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = SVC(kernel='linear', probability=True)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    print(classification_report(y_test, y_pred))
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.2f}")

    # Guardar el modelo entrenado
    joblib.dump(model, "mhd_detector_model.pkl")
    print("Modelo guardado como 'mhd_detector_model.pkl'")

    return model

# Predecir MHD en un nuevo shot usando el modelo entrenado
def predict_shot(model, shot_number):
    images = load_images_for_shot(shot_number)
    if images is None:
        return None

    features = extract_features_from_images(images)
    prediction = model.predict([features])[0]
    return prediction

# Ejecutar todo el proceso automáticamente
if __name__ == "__main__":
    print("Cargando dataset y entrenando modelo...")

    try:
        X, y = load_dataset(EXCEL_PATH)
        print(f"Dataset cargado con {len(X)} muestras")

        model = train_and_evaluate_model(X, y)

        # Probar con un shot aleatorio del dataset
        test_shot = np.random.choice(y.shape[0])
        prediction = predict_shot(model, test_shot)

        if prediction is not None:
            print(f"¿El shot {test_shot} tiene MHD? {'Sí' if prediction == 1 else 'No'}")
        else:
            print(f"No se encontraron imágenes para el shot {test_shot}")

    except Exception as e:
        print(f"Error durante la ejecución: {e}")
