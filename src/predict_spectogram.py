import os
import cv2
import numpy as np
import joblib
import subprocess
import sys
import streamlit as st
from skimage.feature import hog

# ---------------------- CONFIGURATION ---------------------- #
# Paths
model_path = "config/mhd_detector_model.pkl"
input_folders = ["../data/spectograms/spectograms_for_ai_learning", "../data/spectograms/spectograms_for_try"]
utilities_folder = "../utilities/similPatternTool/raw_data/"
plot_script = "plot_spectogram.py"  # Script to generate spectrograms

# Check if the model exists
if not os.path.exists(model_path):
    st.error(f"Model {model_path} not found.")
    st.stop()

# Load the trained model
model = joblib.load(model_path)

# ---------------------- GET SPECTROGRAM NUMBER ---------------------- #
if len(sys.argv) < 2:
    st.error("Error: No spectrogram number provided.")
    st.stop()

shot_number = sys.argv[1]
st.write(f"Processing spectrogram: **{shot_number}**")

# ---------------------- CHECK IF SPECTROGRAM EXISTS ---------------------- #
spectrogram_found = False
for folder in input_folders:
    if all(os.path.exists(os.path.join(folder, f"{shot_number}{suffix}.png")) for suffix in ["", "_N", "_N_bw"]):
        spectrogram_found = True
        spectrogram_path = folder
        break

# If the spectrogram does not exist, ask the user if they want to generate it
if not spectrogram_found:
    st.warning(f"No spectrogram found for {shot_number}. Checking raw data...")

    # Check if the file exists in utilities
    potential_file = os.path.join(utilities_folder, f"MIR5C_{shot_number}_{shot_number}.txt")

    if os.path.exists(potential_file):
        user_choice = st.radio(
            f"Do you want to generate the spectrogram using {plot_script}?",
            ("Yes", "No"),
            index=1
        )

        if user_choice == "Yes":
            st.write(f"Generating spectrogram using `{plot_script}`...")
            subprocess.run([sys.executable, "plot_spectogram.py", shot_number])

            # Re-check if spectrogram was generated
            for folder in input_folders:
                if all(os.path.exists(os.path.join(folder, f"{shot_number}{suffix}.png")) for suffix in ["", "_N", "_N_bw"]):
                    spectrogram_found = True
                    spectrogram_path = folder
                    break

            if not spectrogram_found:
                st.error(f"Error: Spectrogram {shot_number} could not be generated.")
                st.stop()
        else:
            st.warning("Spectrogram generation skipped.")
            st.stop()
    else:
        st.error(f"No corresponding raw data file found for {shot_number}. Exiting.")
        st.stop()

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
                st.warning(f"Warning: Could not load {img_path}")

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
if spectrogram_found:
    result = predict_mhd(shot_number)
    if result is not None:
        st.success(f"Spectrogram {shot_number} MHD? **{result}**")
    else:
        st.error(f"Error processing spectrogram {shot_number}.")

    # Show images
    images = load_images_for_shot(shot_number)
    if images:
        st.image(images, caption=["Original", "N", "N_bw"], use_column_width=True)
else:
    st.error(f"Error: Spectrogram {shot_number} is missing. Cannot predict.")
