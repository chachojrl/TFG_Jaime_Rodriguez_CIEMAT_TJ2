import os
import cv2
import numpy as np
import joblib
import subprocess
import sys
from skimage.feature import hog


# ---------------------- CONFIGURATION ---------------------- #
# Paths
model_path = "mhd_detector_model.pkl"
input_folders = ["../data/spectograms/spectograms_for_ai_learning", "../data/spectograms/spectograms_for_try"]
utilities_folder = "../utilities/similPatternTool/raw_data/"
plot_script = "plot_spectogram.py"  # Script to generate spectrograms

# Check if the model exists
if not os.path.exists(model_path):
    raise FileNotFoundError(f"Model {model_path} not found.")

# Load the trained model
model = joblib.load(model_path)

# ---------------------- GET SPECTROGRAM NUMBER ---------------------- #
if len(sys.argv) < 2:
    print("Error: No spectrogram number provided.")
    sys.exit(1)

shot_number = sys.argv[1]

# ---------------------- CHECK IF SPECTROGRAM EXISTS ---------------------- #
spectrogram_found = False
for folder in input_folders:
    if all(os.path.exists(os.path.join(folder, f"{shot_number}{suffix}.png")) for suffix in ["", "_N", "_N_bw"]):
        spectrogram_found = True
        spectrogram_path = folder
        break

# If the spectrogram does not exist, ask if the user wants to generate it
if not spectrogram_found:
    print(f"No spectrogram found for {shot_number}. Checking raw data...")

    # Check if the file exists in utilities
    potential_file = os.path.join(utilities_folder, f"MIR5C_{shot_number}_{shot_number}.txt")

    if os.path.exists(potential_file):
        user_input = input(f"Do you want to generate the spectrogram using {plot_script}? (y/n): ").strip().lower()
        if user_input == "y":
            print(f"Generating spectrogram using {plot_script}...")
            subprocess.run([sys.executable, "plot_spectogram.py", shot_number])

            # Re-check if spectrogram was generated
            for folder in input_folders:
                if all(os.path.exists(os.path.join(folder, f"{shot_number}{suffix}.png")) for suffix in ["", "_N", "_N_bw"]):
                    spectrogram_found = True
                    spectrogram_path = folder
                    break

            if not spectrogram_found:
                print(f"Error: Spectrogram {shot_number} could not be generated.")
                sys.exit(1)
        else:
            print("Spectrogram generation skipped.")
            sys.exit(1)
    else:
        print(f"No corresponding raw data file found. Exiting.")
        sys.exit(1)

# ---------------------- LOAD AND PROCESS SPECTROGRAM ---------------------- #
def load_images_for_shot(shot_number):
    """Load three spectrogram images"""
    filenames = [f"{shot_number}.png", f"{shot_number}_N.png", f"{shot_number}_N_bw.png"]
    
    images = []
    for filename in filenames:
        img_path = os.path.join(spectrogram_path, filename)
        if os.path.exists(img_path):
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                images.append(cv2.resize(img, (128, 128)))
            else:
                print(f"Warning: Could not load {img_path}")

    return images if len(images) == 3 else None

def extract_features_from_images(images):
    """Extract HOG features from images"""
    hog_features = []
    for img in images:
        features = hog(img, orientations=9, pixels_per_cell=(8, 8),
                       cells_per_block=(2, 2), visualize=False)
        hog_features.extend(features)
    return np.array(hog_features)

def predict_mhd(shot_number):
    """Predict if spectrogram has MHD"""
    images = load_images_for_shot(shot_number)
    if images is None:
        return None
    
    features = extract_features_from_images(images)
    prediction = model.predict([features])[0]
    return "Yes" if prediction == 1 else "No"

# ---------------------- RUN PREDICTION ---------------------- #
# Ensure the spectrogram exists before predicting
if spectrogram_found:
    result = predict_mhd(shot_number)
    if result is not None:
        print(f"Spectrogram {shot_number} MHD? {result}")
    else:
        print(f"Error processing spectrogram {shot_number}.")
else:
    print(f"Error: Spectrogram {shot_number} is missing. Cannot predict.")
