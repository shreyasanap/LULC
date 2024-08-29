# Filename: train_model.py
import cv2
import os
import numpy as np
from skimage.feature import hog
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib

# Corrected predefined classes
classes = ["River", "Residential", "Industrial", "Highway", "Forest", "AnnualCrop"]

# Path to training image folders
image_folder = r"C:\Users\sanik\Desktop\code playground\identify class\data"

# Function to extract HOG features
def extract_hog_features(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image_resized = cv2.resize(gray_image, (128, 128))  # Resizing for consistency
    fd, _ = hog(image_resized, orientations=9, pixels_per_cell=(8, 8),
                cells_per_block=(2, 2), block_norm='L2-Hys', visualize=True)
    return fd

# Prepare training data
X = []
y = []

for label in classes:
    folder_path = os.path.join(image_folder, label)
    if not os.path.exists(folder_path):
        print(f"Folder for class {label} does not exist!")
        continue
    for filename in os.listdir(folder_path):
        img_path = os.path.join(folder_path, filename)
        image = cv2.imread(img_path, cv2.IMREAD_COLOR)
        if image is not None:
            features = extract_hog_features(image)
            X.append(features)
            y.append(label)
        else:
            print(f"Warning: Could not read image {img_path}")

# Convert to NumPy arrays
X = np.array(X)
y = np.array(y)

# Check if data is available
if len(X) == 0:
    raise ValueError("No training data found. Please check your image folders.")

# Encode class labels
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Split into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

# Train SVM model
svm_model = SVC(kernel='linear')
svm_model.fit(X_train, y_train)

# Predict on test set
y_pred = svm_model.predict(X_test)

# Evaluate the classifier
print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))
print(f"Accuracy: {accuracy_score(y_test, y_pred):.2f}")

# Save the trained model and label encoder
joblib.dump(svm_model, 'svm_model.joblib')
joblib.dump(label_encoder, 'label_encoder.joblib')

print("Training complete. Model and label encoder saved.")
