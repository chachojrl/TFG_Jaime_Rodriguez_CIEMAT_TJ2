import os
import pandas as pd
import cv2
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from skimage.feature import hog
import joblib
from sklearn.metrics import classification_report, accuracy_score

# Path to the folder containing spectrogram images
IMAGES_FOLDER = "../data/spectograms/spectograms_for_ai_learning"

# Load data from the Excel file
def load_labels_from_excel(excel_path):
    df = pd.read_excel(excel_path)
    df['MHD'] = df['MHD'].map({'Y': 1, 'N': 0})
    return df

# Load the 3 images for each spectrogram
def load_images_for_shot(shot_number):
    filenames = [
        f"{shot_number}.png",          # color
        f"{shot_number}_N.png",        # heatmap
        f"{shot_number}_N_bw.png"      # grayscale
    ]
    images = []
    for filename in filenames:
        img_path = os.path.join(IMAGES_FOLDER, filename)
        if os.path.exists(img_path):
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            images.append(cv2.resize(img, (128, 128)))
        else:
            print(f"Warning: {img_path} not found")
            return None
    return images

# Extract HOG features from the 3 concatenated images
def extract_features_from_images(images):
    hog_features = []
    for img in images:
        features = hog(img, orientations=9, pixels_per_cell=(8, 8),
                       cells_per_block=(2, 2), visualize=False)
        hog_features.extend(features)  # Combine features from all 3 images
    return np.array(hog_features)

# Load the full dataset
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

    return np.array(all_features), np.array(all_labels)

# Train and evaluate the model
def train_and_evaluate_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = SVC(kernel='linear', probability=True)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    print(classification_report(y_test, y_pred))
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.2f}")

    joblib.dump(model, "mhd_detector_model.pkl")
    print("Model saved as 'mhd_detector_model.pkl'")

    return model

# Predict whether a new spectrogram has MHD
def predict_shot(model, shot_number):
    images = load_images_for_shot(shot_number)
    if images is None:
        return None

    features = extract_features_from_images(images)
    prediction = model.predict([features])[0]
    return prediction

# Main
if __name__ == "__main__":
    excel_path = "../data/processed/clasified_spectrograms.xlsx"

    print("Loading dataset and training model...")
    X, y = load_dataset(excel_path)
    print(f"Dataset loaded with {len(X)} samples")

    model = train_and_evaluate_model(X, y)

    test_shot = 37986  # Shot number to predict
    prediction = predict_shot(model, test_shot)

    if prediction is not None:
        print(f"Does shot {test_shot} have MHD? {'Yes' if prediction == 1 else 'No'}")
    else:
        print(f"No images found for shot {test_shot}")
