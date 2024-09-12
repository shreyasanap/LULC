import streamlit as st
import torch
from torchvision import models, transforms
from PIL import Image
import numpy as np
import os

# Define constants
MODEL_PATH = os.path.join('pages', 'best_model.pth')
IMAGE_SIZE = 224
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]
CLASS_NAMES = [
    'AnnualCrop', 'Forest', 'HerbaceousVegetation', 'Highway', 'Industrial', 
    'Mosaic', 'Pasture', 'PermanentCrop', 'Residential', 'River'
]

# Load the trained model
def load_model():
    if not os.path.isfile(MODEL_PATH):
        st.error(f"Model file not found at {MODEL_PATH}")
        return None

    model = models.resnet50(pretrained=True)
    num_ftrs = model.fc.in_features
    model.fc = torch.nn.Linear(num_ftrs, len(CLASS_NAMES))

    # Load model with map_location set to 'cpu'
    try:
        model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu')))
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None
    
    model.eval()
    return model

model = load_model()

# Define image transformations
def transform_image(image):
    preprocess = transforms.Compose([
        transforms.Resize(IMAGE_SIZE),
        transforms.CenterCrop(IMAGE_SIZE),
        transforms.ToTensor(),
        transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
    ])
    return preprocess(image).unsqueeze(0)

# Predict the LULC type with confidence and thresholding
def predict(image, threshold=0.5):
    if model is None:
        return "Model not loaded"
    image_tensor = transform_image(image)
    with torch.no_grad():
        output = model(image_tensor)
        probs = torch.nn.functional.softmax(output, dim=1)
        max_prob, predicted = torch.max(probs, 1)
        confidence = max_prob.item()
        
        if confidence < threshold:
            return f"Uncertain prediction: {CLASS_NAMES[predicted.item()]} (Confidence: {confidence:.2f})"
        return f"Predicted class: {CLASS_NAMES[predicted.item()]} (Confidence: {confidence:.2f})"

# Streamlit app
st.title("Land Use and Land Cover Classification")

uploaded_file = st.file_uploader("Choose an image...", type="jpg")

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image', use_column_width=True)
    st.write("")
    st.write("Classifying...")

    prediction = predict(image, threshold=0.7)  # Set a threshold for prediction confidence
    st.write(f"Result: {prediction}")
