# Filename: predict_image.py
import cv2
import numpy as np
from skimage.feature import hog
import joblib
import os

# Load the pre-trained model and label encoder
svm_model = joblib.load('svm_model.joblib')
label_encoder = joblib.load('label_encoder.joblib')

# Function to extract HOG features
def extract_hog_features(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image_resized = cv2.resize(gray_image, (128, 128))  # Resizing for consistency
    fd, _ = hog(image_resized, orientations=9, pixels_per_cell=(8, 8),
                cells_per_block=(2, 2), block_norm='L2-Hys', visualize=True)
    return fd

# Function to classify a new image
def classify_image(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Could not read the image: {image_path}")
    features = extract_hog_features(image)
    prediction = svm_model.predict([features])
    return label_encoder.inverse_transform(prediction)[0]

# Interactive part to classify a new image
test_image = input("Enter the full path to the test image (e.g., C:\\path\\to\\your\\test_image.jpg): ")
if not os.path.isfile(test_image):
    raise ValueError(f"File does not exist: {test_image}")
predicted_class = classify_image(test_image)
print(f"Predicted class: {predicted_class}")
