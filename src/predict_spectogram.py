import os
import cv2
import numpy as np
import joblib
import subprocess
import sys
from skimage.feature import hog

# ---------------------- CONFIGURATION ---------------------- #
model_path = "config/mhd_detector_model.pkl"
input_folders = ["./spectograms/spectograms_for_ai_learning", "./spectograms/spectograms_for_try"]
utilities_folder = "../utilities/similPatternTool/raw_data/"
plot_script = "plot_spectogram.py"

# Check if the model exists
if not os.path.exists(model_path):
    print(f"ERROR: Model {model_path} not found.")
    sys.exit(1)

# Load the trained model
model = joblib.load(model_path)

def check_spectrogram_exists(shot_number):
    """Check if spectrogram exists in any of the input folders."""
    for folder in input_folders:
        if os.path.exists(os.path.join(folder, f"{shot_number}.png")):
            return folder
    return None

def generate_spectrogram(shot_number):
    """Ejecuta plot_spectogram.py y devuelve la imagen generada."""
    result = subprocess.run(
        [sys.executable, plot_script, str(shot_number)],
        capture_output=True, text=True
    )

    if result.returncode == 0:
        generated_image = result.stdout.strip()
        return generated_image if generated_image.endswith(".png") else None
    return None

def load_images_for_shot(shot_number, spectrogram_path):
    """Carga las tres imágenes del espectrograma: Original, N y N_bw."""
    filenames = [f"{shot_number}.png", f"{shot_number}_N.png", f"{shot_number}_N_bw.png"]
    
    images = []
    for filename in filenames:
        img_path = os.path.join(spectrogram_path, filename)
        if os.path.exists(img_path):
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                images.append(cv2.resize(img, (128, 128))) 

    return images if len(images) == 3 else None

def extract_features_from_images(images):
    """Extrae características HOG de las tres imágenes y las concatena."""
    hog_features = []
    for img in images:
        features = hog(img, orientations=9, pixels_per_cell=(8, 8),
                       cells_per_block=(2, 2), visualize=False)
        hog_features.extend(features) 
    return np.array(hog_features)

def predict_mhd(shot_number, generate_if_missing):
    """Predice si el espectrograma tiene MHD usando las tres imágenes."""
    spectrogram_path = check_spectrogram_exists(shot_number)
    
    if not spectrogram_path:
        if generate_if_missing == "Yes":
            spectrogram_path = generate_spectrogram(shot_number)
            spectrogram_path = os.path.dirname(spectrogram_path)
            if not spectrogram_path:
                print(f"ERROR: Could not generate spectrogram for shot {shot_number}.")
                sys.exit(1)
        else:
            print(f"ERROR: Spectrogram {shot_number} is missing. Cannot predict.")
            sys.exit(1)

    images = load_images_for_shot(shot_number, spectrogram_path)
    if images is None:
        print(f"ERROR: Spectrogram images for {shot_number} not found.")
        sys.exit(1)

    features = extract_features_from_images(images)
    if features is None or len(features) != 24300:
        print(f"ERROR: Incorrect feature size ({len(features)} instead of 24300)")
        sys.exit(1)

    prediction = model.predict([features])[0]
    result_text = f"SUCCESS: Spectrogram {shot_number} MHD? {'Yes' if prediction == 1 else 'No'}"

    print(result_text)
    #print(os.path.join(spectrogram_path, f"{shot_number}.png"))
    sys.exit(0)

# ---------------------- MAIN EXECUTION ---------------------- #
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("ERROR: No spectrogram number or missing generation option provided.")
        sys.exit(1)
        

    shot_number = sys.argv[1]
    generate_if_missing = sys.argv[2]  # "Yes" o "No"
    predict_mhd(shot_number, generate_if_missing)
